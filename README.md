# 📡 Distributed Telemetry Monitoring System

## 📌 Overview
This project is a **multi-system telemetry monitoring platform** that collects system metrics (CPU, memory, disk) from multiple machines over a network, aggregates them, stores them, and visualizes them in real-time through a web dashboard.

It simulates a lightweight **observability pipeline**, similar to tools like Prometheus or Datadog.

---

## 🚀 Features

- 🔄 Real-time system monitoring  
- 🌐 Multi-machine support over network (WiFi / hotspot)  
- 🧠 Per-system data aggregation  
- 📊 Interactive dashboard with system selection  
- 📈 Live charts for CPU, Memory, and Disk usage  
- 🟢 System status detection (Online / Offline)  
- ⚙️ Centralized configuration  
- 🪵 Structured logging  

---

## 🧱 Architecture

```
Agents (multiple systems)
        ↓
   Server (Aggregation + Storage)
        ↓
   Dashboard (Visualization)
```

---

## 📁 Project Structure

```
telemetry_system/
│
├── agent/            # Collects system metrics
├── server/           # Aggregates + stores data
├── dashboard/        # Streamlit UI
├── common/           # Config + logging
│
├── requirements.txt
└── README.md
```

---

## ⚙️ Installation

1. Clone the repository:
```
git clone <your-repo-url>
cd telemetry_system
```

2. Create virtual environment (recommended):
```
python -m venv venv
venv\Scripts\activate   # Windows
```

3. Install dependencies:
```
pip install -r requirements.txt
```

---

## 🌐 Configuration

Edit:
```
common/config.py
```

Update your server IP:

```python
SERVER_URL = "http://<YOUR_SERVER_IP>:8000"
```

To find your IP:
```
ipconfig   # Windows
ifconfig   # Linux/Mac
```

---

## ▶️ How to Run

### 1️⃣ Start Server
```
python -m server.server
```

### 2️⃣ Start Dashboard
```
python -m streamlit run dashboard/app.py
```

Open in browser:
```
http://localhost:8501
```

### 3️⃣ Start Agents (on multiple machines)
```
python -m agent.agent
```

---

## 📊 Dashboard Features

- View number of connected systems  
- Select individual system  
- Monitor CPU, memory, disk usage  
- Real-time updating graphs  
- System status (Online / Offline)  
- Overview table for all systems  

---

## 🔌 API Endpoints

| Endpoint | Method | Description |
|---------|--------|------------|
| `/collect` | POST | Receive raw metrics from agents |
| `/metrics` | GET | Get stored aggregated metrics |
| `/analysis` | GET | Get overall statistics |

---

## ⚠️ Notes

- Ensure all devices are on the same network  
- Make sure firewall allows port **8000**  
- Delete `telemetry.db` if schema changes  
- Run commands from project root directory  
