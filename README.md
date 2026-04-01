# 📡 Telemetry Collection and Aggregation System

A distributed telemetry system where multiple clients (agents) continuously send system metrics to a centralized server using UDP. The system performs real-time aggregation, packet loss tracking, and performance monitoring.

---

## 🚀 Features

### ✅ Core Capabilities

*  **UDP-based Telemetry Ingestion** (high-throughput, low overhead)
*  **Per-system Aggregation** (CPU, memory, disk)
*  **Sequence Tracking** for each client
*  **Packet Loss Detection**
*  **Persistent Storage** using SQLite
*  **Live Dashboard** (Streamlit)

---

### ⚡ Performance & Scalability

* Multi-threaded ingestion pipeline
* Queue-based processing (decoupled ingestion & computation)
* Batch database writes (optimized performance)
* Configurable worker threads

---

## 🏗️ Architecture

```
[Agent]
   ↓ UDP
[Receiver Thread]
   ↓
[Queue]
   ↓
[Worker Threads]
   ↓
[Aggregation Buffer]
   ↓
[Database (SQLite)]
   ↓
[Dashboard (Streamlit)]
```

---

## 📂 Project Structure

```
agent/
  └── agent.py          # Sends telemetry data

common/
  ├── config.py         # Configuration
  └── logger.py         # Logging setup

server/
  ├── server.py         # UDP server + processing
  ├── database.py       # DB connection
  ├── models.py         # DB operations
  └── metrics.py        # Packet loss tracking

dashboard/
  └── app.py            # Streamlit dashboard

requirements.txt
README.md
```

---

## 📦 Installation

### 1. Clone repository

```bash
git clone <your-repo-url>
cd telemetry-system
```

### 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## ▶️ Running the System

### 1. Start the server

```bash
python server/server.py
```

---

### 2. Start agent(s)

Run one or multiple agents (simulate distributed systems):

```bash
python agent/agent.py
```

---

### 3. Start dashboard

```bash
streamlit run dashboard/app.py
```

---

## 📊 Data Flow

Each agent sends:

```json
{
  "system_id": "host123",
  "seq": 10,
  "cpu": 45.5,
  "memory": 60.2,
  "disk": 70.1,
  "timestamp": 1710000000
}
```

---

## 🔍 Key Concepts

### 🔢 Sequence Tracking

Each packet includes a sequence number:

* Detects missing packets
* Enables packet loss calculation

---

### ⚠️ Packet Loss Detection

Server tracks:

```
expected_seq vs received_seq
```

If mismatch:

```
loss = received - expected
```

---

### 📊 Aggregation

Data is buffered per system and aggregated after:

```
AGGREGATION_BATCH_SIZE (default = 5)
```

Metrics stored:

* avg_cpu
* avg_memory
* avg_disk

---

### ⚡ High-Rate Processing

* UDP ingestion (non-blocking)
* Queue-based buffering
* Worker thread pool

---

## ⚙️ Configuration

Modify in `common/config.py`:

```python
SERVER_PORT = 8000
AGGREGATION_BATCH_SIZE = 5
WORKER_THREADS = 4
MAX_QUEUE_SIZE = 10000
MAX_BUFFER_SIZE = 1000
```

---

## 📈 Performance Metrics

The system tracks:

* Total packets received
* Packet loss per system
* Aggregation events

---

## ⚠️ Limitations

* UDP is unreliable (intentional for this system)
* SQLite is not ideal for high-scale production
* No authentication or encryption

---

## 🚀 Future Improvements

* Replace SQLite with PostgreSQL
* Add FastAPI REST endpoints
* Implement authentication
* Add compression (zlib)
* Use asyncio for higher throughput
* Deploy with Docker

---

## 🎯 Use Cases

* Distributed system monitoring
* Performance testing environments
* Network telemetry pipelines
* Observability system prototypes

---

## 👨‍💻 Tech Stack

* Python
* UDP Sockets
* SQLite
* Streamlit
* Multithreading

---

## 🧾 Summary

This project demonstrates a **real-world telemetry pipeline** with:

* High-throughput ingestion
* Loss detection
* Aggregation logic
* Scalable architecture patterns

---

## 📬 Author

Your Name
(Replace with your details)

---
