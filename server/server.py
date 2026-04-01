from server.models import insert_metric, get_all_metrics
from common.config import SERVER_HOST, SERVER_PORT, AGGREGATION_BATCH_SIZE
from common.logger import logger
import socket
import json
import time
from threading import Lock

buffers = {}
lock = Lock()


def process_data(data):
    """Process incoming telemetry data"""
    required = ["system_id", "cpu", "memory", "disk", "timestamp"]
    if not all(k in data for k in required):
        logger.error("Invalid payload received")
        return

    system_id = data["system_id"]

    with lock:
        if system_id not in buffers:
            buffers[system_id] = []

        buffers[system_id].append(data)
        logger.info(f"Received data from {system_id}")

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

            logger.info(f"Aggregated + stored data for {system_id}")


def start_udp_server():
    """Start UDP server to listen for telemetry data"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((SERVER_HOST, SERVER_PORT))
    logger.info(f"UDP Server listening on {SERVER_HOST}:{SERVER_PORT}")

    while True:
        try:
            data, addr = sock.recvfrom(4096)
            message = json.loads(data.decode('utf-8'))
            logger.info(f"Received UDP packet from {addr}")
            process_data(message)
        except Exception as e:
            logger.error(f"Error processing UDP packet: {e}")


if __name__ == '__main__':
    start_udp_server()
