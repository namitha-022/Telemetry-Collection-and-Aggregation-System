from fastapi import FastAPI
from server.models import get_all_metrics
from server.metrics import get_stats

app = FastAPI()


@app.get("/metrics")
def metrics():
    return get_all_metrics()


@app.get("/analysis")
def analysis():
    data = get_all_metrics()
    if not data:
        return {}

    avg_cpu = sum(d["avg_cpu"] for d in data) / len(data)
    max_cpu = max(d["avg_cpu"] for d in data)

    return {
        "overall_avg_cpu": avg_cpu,
        "max_cpu": max_cpu
    }


@app.get("/stats")  # 🔥 NEW
def stats():
    return get_stats()

@app.get("/dashboard")
def dashboard():
    return {
        "metrics": get_all_metrics(),
        "stats": get_stats()
    }