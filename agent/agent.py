import psutil
import requests
import time
import socket
from common.config import SERVER_URL
from common.logger import logger

COLLECT_URL = f"{SERVER_URL}/collect"
SYSTEM_ID = socket.gethostname()

while True:
    data = {
        "system_id": SYSTEM_ID,
        "cpu": psutil.cpu_percent(),
        "memory": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage('/').percent,
        "timestamp": time.time()
    }

    try:
        requests.post(COLLECT_URL, json=data, timeout=2)
        logger.info(f"[{SYSTEM_ID}] Sent data: {data}")
    except Exception as e:
        logger.error(f"[{SYSTEM_ID}] Failed to send data: {e}")

    time.sleep(2)