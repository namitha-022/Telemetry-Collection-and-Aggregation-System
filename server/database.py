import sqlite3
from common.config import DB_FILE

conn = sqlite3.connect(DB_FILE, check_same_thread=False)
cursor = conn.cursor()

cursor.execute("PRAGMA journal_mode=WAL;")

cursor.execute("""
CREATE TABLE IF NOT EXISTS metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    system_id TEXT,
    avg_cpu REAL,
    avg_memory REAL,
    avg_disk REAL,
    timestamp REAL
)
""")

conn.commit()