import psutil
import requests
import time

AGGREGATOR_URL = "http://localhost:9000/collect"

while True:
    data = {
        "cpu": psutil.cpu_percent(),
        "memory": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage('/').percent,
        "timestamp": time.time()
    }

    try:
        requests.post(AGGREGATOR_URL, json=data)
        print("Sent:", data)
    except Exception as e:
        print("Error:", e)

    time.sleep(2)
    