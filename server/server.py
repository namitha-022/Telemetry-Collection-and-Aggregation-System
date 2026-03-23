from flask import Flask, request, jsonify
from server.models import insert_metric, get_all_metrics
from common.config import SERVER_HOST, SERVER_PORT, AGGREGATION_BATCH_SIZE
from common.logger import logger
import time
from threading import Lock

app = Flask(__name__)

buffers = {}
lock = Lock()


@app.route('/collect', methods=['POST'])
def collect():
    data = request.json

    required = ["system_id", "cpu", "memory", "disk", "timestamp"]
    if not data or not all(k in data for k in required):
        return jsonify({"error": "invalid payload"}), 400

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

    return jsonify({"status": "received"})


@app.route('/metrics', methods=['GET'])
def metrics():
    return jsonify(get_all_metrics())


@app.route('/analysis', methods=['GET'])
def analysis():
    data_store = get_all_metrics()

    if not data_store:
        return jsonify({
            "systems": 0,
            "overall_avg_cpu": 0,
            "max_cpu": 0
        })

    avg_cpu = sum(d['avg_cpu'] for d in data_store) / len(data_store)
    max_cpu = max(d['avg_cpu'] for d in data_store)
    systems = len(set(d["system_id"] for d in data_store))

    return jsonify({
        "systems": systems,
        "overall_avg_cpu": avg_cpu,
        "max_cpu": max_cpu
    })


if __name__ == '__main__':
    app.run(host=SERVER_HOST, port=SERVER_PORT)