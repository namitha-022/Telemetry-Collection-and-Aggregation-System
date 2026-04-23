# 📡 Telemetry Collection and Aggregation System

A distributed telemetry system where multiple clients (agents)
continuously send system metrics to a centralized server using UDP. The
system performs real-time aggregation, packet loss tracking, and
performance monitoring with a live dashboard.

------------------------------------------------------------------------

## 🚀 Features

### ✅ Core Capabilities

-   UDP-based telemetry ingestion (high throughput, low overhead)
-   Real-time system metrics collection (CPU, Memory, Disk)
-   Sequence tracking for each client
-   Packet loss detection
-   Aggregation and summarization
-   Persistent storage using SQLite
-   Interactive dashboard using Streamlit

------------------------------------------------------------------------

### ⚡ Performance & Scalability

-   Multi-threaded ingestion pipeline
-   Queue-based processing (decouples ingestion from computation)
-   Batch database writes
-   Configurable worker threads
-   Supports multi-machine deployment over network

------------------------------------------------------------------------

## 🏗️ Architecture

    [Agent(s)]
       ↓ UDP
    [Receiver Thread]
       ↓
    [Queue Buffer]
       ↓
    [Worker Threads]
       ↓
    [Aggregation Buffer]
       ↓
    [Database (SQLite)]
       ↓
    [FastAPI Server]
       ↓ HTTP
    [Dashboard (Streamlit)]

------------------------------------------------------------------------

## 📂 Project Structure

```
Telemetry-Collection-and-Aggregation-System
├── agent/                     → Telemetry sender (UDP client)
│   ├── __pycache__/
│   └── agent.py
│
├── server/                    → Ingestion + processing + API
│   ├── __pycache__/
│   ├── __init__.py
│   ├── server.py              → UDP server + pipeline orchestration
│   ├── api.py                 → FastAPI endpoints
│   ├── database.py            → SQLite setup
│   ├── models.py              → DB operations (insert/query)
│   └── metrics.py             → Packet tracking & stats
│
├── dashboard/                 → UI (Streamlit)
│   └── app.py
│
├── common/                    → Shared configs & logging
│   ├── __pycache__/
│   ├── config.py              → Global configuration
│   └── logger.py              → Logging setup
│
├── .gitignore
├── README.md
└── requirements.txt
```

------------------------------------------------------------------------

## ⚙️ Installation

``` bash
python -m venv venv
venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

------------------------------------------------------------------------

## ▶️ Running the System

### 🖥️ Start Server (UDP + API)

``` bash
python -m server.server
```

------------------------------------------------------------------------

### 💻 Start Agent(s)

``` bash
python -m agent.agent
```

------------------------------------------------------------------------

### 📊 Start Dashboard

``` bash
streamlit run dashboard/app.py
```

Open in browser: http://localhost:8501

------------------------------------------------------------------------

## 🌐 Multi-PC Setup

Edit `common/config.py`:

``` python
SERVER_IP_FOR_CLIENTS = "192.168.X.X"
```

### Requirements:

-   Same network (LAN)
-   Firewall allows UDP port 8000

------------------------------------------------------------------------

## 📊 Data Format

``` json
{
  "system_id": "host123",
  "seq": 10,
  "cpu": 45.5,
  "memory": 60.2,
  "disk": 70.1,
  "timestamp": 1710000000
}
```

------------------------------------------------------------------------

## 🔍 Key Concepts

### 🔢 Sequence Tracking

-   Detects missing packets using sequence numbers

### ⚠️ Packet Loss Detection

-   Compares expected vs received sequence numbers

### 📊 Aggregation

-   Data buffered and averaged over batch size

### ⚡ High-Rate Processing

-   UDP ingestion + queue + worker threads

------------------------------------------------------------------------

## 📈 Metrics Tracked

-   CPU / Memory / Disk usage
-   Packet loss per system
-   Throughput (packets/sec)

------------------------------------------------------------------------

## 🎯 Conclusion

This project demonstrates a complete telemetry pipeline including: -
Distributed data collection - High-throughput ingestion - Real-time
aggregation - Network reliability analysis - Live visualization

------------------------------------------------------------------------

## 👨‍💻 Tech Stack

-   Python
-   UDP Sockets
-   FastAPI
-   SQLite
-   Streamlit
-   Multithreading
