import psutil
import time
import socket
import json
from common.config import SERVER_IP_FOR_CLIENTS, SERVER_PORT
from common.logger import logger

SYSTEM_ID = socket.gethostname()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 65536)

seq = 0

while True:
    data = {
        "system_id": SYSTEM_ID,
        "seq": seq,
        "cpu": psutil.cpu_percent(),
        "memory": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage('/').percent,
        "timestamp": time.time()
    }

    try:
        message = json.dumps(data).encode('utf-8')
        sock.sendto(message, (SERVER_IP_FOR_CLIENTS, SERVER_PORT))
        logger.info(f"[{SYSTEM_ID}] Sent seq={seq}")
        seq += 1
    except Exception as e:
        logger.error(f"[{SYSTEM_ID}] Failed: {e}")

    time.sleep(2)