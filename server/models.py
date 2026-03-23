from server.database import cursor, conn

def insert_metric(data):
    cursor.execute(
        "INSERT INTO metrics (system_id, avg_cpu, avg_memory, avg_disk, timestamp) VALUES (?, ?, ?, ?, ?)",
        (data['system_id'], data['avg_cpu'], data['avg_memory'], data['avg_disk'], data['timestamp'])
    )
    conn.commit()


def get_all_metrics():
    cursor.execute("SELECT system_id, avg_cpu, avg_memory, avg_disk, timestamp FROM metrics")
    rows = cursor.fetchall()

    return [
        {
            "system_id": r[0],
            "avg_cpu": r[1],
            "avg_memory": r[2],
            "avg_disk": r[3],
            "timestamp": r[4]
        }
        for r in rows
    ]