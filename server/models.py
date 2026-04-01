from server.database import cursor, conn

buffered_inserts = []
BATCH_SIZE = 10  # NEW

def insert_metric(data):
    buffered_inserts.append((
        data['system_id'],
        data['avg_cpu'],
        data['avg_memory'],
        data['avg_disk'],
        data['timestamp']
    ))

    if len(buffered_inserts) >= BATCH_SIZE:
        cursor.executemany(
            "INSERT INTO metrics (system_id, avg_cpu, avg_memory, avg_disk, timestamp) VALUES (?, ?, ?, ?, ?)",
            buffered_inserts
        )
        conn.commit()
        buffered_inserts.clear()


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