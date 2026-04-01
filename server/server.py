from server.models import insert_metric
from server.metrics import update_sequence
from common.config import (
    SERVER_HOST, SERVER_PORT,
    AGGREGATION_BATCH_SIZE,
    WORKER_THREADS, MAX_QUEUE_SIZE, MAX_BUFFER_SIZE
)
from common.logger import logger

import socket
import json
import time
from threading import Thread, Lock
from queue import Queue

buffers = {}
lock = Lock()
queue = Queue(maxsize=MAX_QUEUE_SIZE)


def process_data(data):
    required = ["system_id", "seq", "cpu", "memory", "disk", "timestamp"]
    if not all(k in data for k in required):
        return

    system_id = data["system_id"]
    seq = data["seq"]

    update_sequence(system_id, seq)

    with lock:
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
    while True:
        try:
            data, _ = sock.recvfrom(4096)
            queue.put_nowait(data)
        except:
            logger.warning("Queue full → packet dropped")


def worker():
    while True:
        try:
            raw = queue.get()
            message = json.loads(raw.decode('utf-8'))
            process_data(message)
        except Exception as e:
            logger.error(f"Worker error: {e}")


def start_udp_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((SERVER_HOST, SERVER_PORT))

    logger.info(f"UDP Server running on {SERVER_HOST}:{SERVER_PORT}")

    Thread(target=receiver, args=(sock,), daemon=True).start()

    for _ in range(WORKER_THREADS):
        Thread(target=worker, daemon=True).start()

    while True:
        time.sleep(10)