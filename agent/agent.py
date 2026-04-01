import psutil
import time
import socket
import json
from common.config import SERVER_HOST, SERVER_PORT
from common.logger import logger

SYSTEM_ID = socket.gethostname()

# Create UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while True:
    data = {
        "system_id": SYSTEM_ID,
        "cpu": psutil.cpu_percent(),
        "memory": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage('/').percent,
        "timestamp": time.time()
    }

    try:
        # Send data via UDP
        message = json.dumps(data).encode('utf-8')
        sock.sendto(message, (SERVER_HOST, SERVER_PORT))
        logger.info(f"[{SYSTEM_ID}] Sent data via UDP: {data}")
    except Exception as e:
        logger.error(f"[{SYSTEM_ID}] Failed to send data: {e}")

    time.sleep(2)
