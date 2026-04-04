from server.models import insert_metric, db_worker
from server.metrics import update_sequence
from common.config import (
    SERVER_HOST, SERVER_PORT,
    AGGREGATION_BATCH_SIZE,
    WORKER_THREADS, MAX_QUEUE_SIZE, MAX_BUFFER_SIZE
)
from common.logger import logger

import uvicorn
from threading import Thread
import socket
import json
import time
from threading import Thread, Lock
from queue import Queue
from collections import defaultdict
import signal
import sys

buffers = {}
locks = defaultdict(Lock)
queue = Queue(maxsize=MAX_QUEUE_SIZE)

dropped_packets = 0

def start_api():
    uvicorn.run(
        "server.api:app",
        host="0.0.0.0",
        port=8001,
        log_level="info"
    )

def process_data(data):
    required = ["system_id", "seq", "cpu", "memory", "disk", "timestamp"]
    if not all(k in data for k in required):
        return

    system_id = data["system_id"]
    seq = data["seq"]

    update_sequence(system_id, seq)

    with locks[system_id]:
        if system_id not in buffers:
            buffers[system_id] = []

        buffers[system_id].append(data)

        if len(buffers[system_id]) > MAX_BUFFER_SIZE:
            buffers[system_id] = buffers[system_id][-MAX_BUFFER_SIZE:]

        if len(buffers[system_id]) >= AGGREGATION_BATCH_SIZE:
            buf = buffers[system_id]

            avg_cpu = sum(d['cpu'] for d in buf) / len(buf)
            avg_mem = sum(d['memory'] for d in buf) / len(buf)
            avg_disk = sum(d['disk'] for d in buf) / len(buf)

            aggregated = {
                "system_id": system_id,
                "avg_cpu": avg_cpu,
                "avg_memory": avg_mem,
                "avg_disk": avg_disk,
                "timestamp": time.time()
            }

            insert_metric(aggregated)
            buffers[system_id] = []

            logger.info(f"Stored aggregated data for {system_id}")


def receiver(sock):
    global dropped_packets

    while True:
        try:
            data, addr = sock.recvfrom(4096)
            logger.info(f"Received from {addr}")
            queue.put_nowait(data)
        except:
            dropped_packets += 1
            logger.warning(f"Queue full → dropped={dropped_packets}")


def worker():
    while True:
        try:
            raw = queue.get()
            message = json.loads(raw.decode('utf-8'))
            process_data(message)
        except Exception as e:
            logger.error(f"Worker error: {e}")


def shutdown(sig, frame):
    logger.info("Shutting down server...")
    sys.exit(0)


def start_udp_server():
    signal.signal(signal.SIGINT, shutdown)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 65536)

    sock.bind((SERVER_HOST, SERVER_PORT))
    logger.info(f"UDP Server running on {SERVER_HOST}:{SERVER_PORT}")

    Thread(target=db_worker, daemon=True).start()
    Thread(target=receiver, args=(sock,), daemon=True).start()

    for _ in range(WORKER_THREADS):
        Thread(target=worker, daemon=True).start()

    while True:
        time.sleep(10)

if __name__ == "__main__":
    # 🔥 Start API in background
    Thread(target=start_api, daemon=True).start()

    # 🔥 Start UDP server
    start_udp_server()