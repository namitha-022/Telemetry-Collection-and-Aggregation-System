from flask import Flask, request, jsonify
from server.models import insert_metric, get_all_metrics

app = Flask(__name__)

@app.route('/store', methods=['POST'])
def store():
    data = request.json
    insert_metric(data)
    return jsonify({"status": "stored"})

@app.route('/metrics', methods=['GET'])
def metrics():
    return jsonify(get_all_metrics())

@app.route('/analysis', methods=['GET'])
def analysis():
    data_store = get_all_metrics()

    if not data_store:
        return jsonify({})

    avg_cpu = sum(d['avg_cpu'] for d in data_store) / len(data_store)
    max_cpu = max(d['avg_cpu'] for d in data_store)

    return jsonify({
        "overall_avg_cpu": avg_cpu,
        "max_cpu": max_cpu
    })

if __name__ == '__main__':
    app.run(port=8000)