from server.database import cursor, conn

def insert_metric(data):
    cursor.execute(
        "INSERT INTO metrics (avg_cpu, avg_memory, avg_disk, timestamp) VALUES (?, ?, ?, ?)",
        (data['avg_cpu'], data['avg_memory'], data['avg_disk'], data['timestamp'])
    )
    conn.commit()

def get_all_metrics():
    cursor.execute("SELECT avg_cpu, avg_memory, avg_disk, timestamp FROM metrics")
    rows = cursor.fetchall()

    return [
        {
            "avg_cpu": r[0],
            "avg_memory": r[1],
            "avg_disk": r[2],
            "timestamp": r[3]
        }
        for r in rows
    ]
