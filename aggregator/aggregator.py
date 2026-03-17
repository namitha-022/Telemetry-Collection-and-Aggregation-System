from flask import Flask, request, jsonify
import requests
import time

app = Flask(__name__)

SERVER_URL = "http://localhost:8000/store"
buffer = []

@app.route('/collect', methods=['POST'])
def collect():
    data = request.json
    buffer.append(data)

    if len(buffer) >= 5:
        avg_cpu = sum(d['cpu'] for d in buffer) / len(buffer)
        avg_mem = sum(d['memory'] for d in buffer) / len(buffer)
        avg_disk = sum(d['disk'] for d in buffer) / len(buffer)

        aggregated = {
            "avg_cpu": avg_cpu,
            "avg_memory": avg_mem,
            "avg_disk": avg_disk,
            "timestamp": time.time()
        }

        try:
            requests.post(SERVER_URL, json=aggregated)
        except:
            pass

        buffer.clear()

    return jsonify({"status": "received"})

if __name__ == '__main__':
    app.run(port=9000)