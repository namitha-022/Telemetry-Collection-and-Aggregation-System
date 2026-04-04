import streamlit as st
import pandas as pd
import requests
import time
from streamlit_autorefresh import st_autorefresh

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
API_BASE = "http://localhost:8001"  # change if needed

st.set_page_config(
    page_title="Telemetry Dashboard",
    layout="wide",
    page_icon="📡"
)

st.title("📡 Telemetry Monitoring Dashboard")
st.caption("Real-time system metrics • Network health • Performance analytics")

# 🔥 Reduced refresh frequency (less flicker)
st_autorefresh(interval=5000, key="refresh")

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def get_status(value):
    if value >= 80:
        return "🔴 Critical"
    elif value >= 60:
        return "🟡 Warning"
    return "🟢 Healthy"


def get_system_status(ts):
    return "🟢 Online" if (time.time() - ts) < 5 else "🔴 Offline"


# ─────────────────────────────────────────────
# FETCH DATA (OPTIMIZED)
# ─────────────────────────────────────────────
@st.cache_data(ttl=5)
def fetch_data():
    try:
        # 🔥 Single API call (faster)
        res = requests.get(f"{API_BASE}/dashboard", timeout=2)
        data = res.json()
        return data.get("metrics", []), data.get("stats", {})
    except:
        return [], {}


# ─────────────────────────────────────────────
# MAIN APP
# ─────────────────────────────────────────────
with st.spinner("🔄 Updating telemetry data..."):
    metrics, stats = fetch_data()

if not metrics:
    st.warning("⚠️ No telemetry data available")
    st.stop()

df = pd.DataFrame(metrics)

# ─────────────────────────────────────────────
# 🔝 TOP KPIs
# ─────────────────────────────────────────────
st.markdown("## 📊 System Overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Active Systems", df["system_id"].nunique())
col2.metric("Avg CPU", f"{df['avg_cpu'].mean():.2f}%")
col3.metric("Max CPU", f"{df['avg_cpu'].max():.2f}%")
col4.metric("Total Records", len(df))

st.divider()

# ─────────────────────────────────────────────
# 🌐 NETWORK HEALTH
# ─────────────────────────────────────────────
st.markdown("## 🌐 Network Health")

c1, c2, c3 = st.columns(3)

c1.metric("Packets Received", f"{stats.get('total_received', 0):,}")
c2.metric("Throughput", f"{stats.get('throughput', 0):.2f} pkt/s")
c3.metric("Packet Loss", f"{stats.get('packet_loss_percent', 0):.2f}%")

# Packet loss breakdown
if stats.get("packet_loss"):
    st.markdown("### 📉 Packet Loss by System")

    loss_df = pd.DataFrame(
        list(stats["packet_loss"].items()),
        columns=["System", "Packets Lost"]
    ).sort_values("Packets Lost", ascending=False)

    st.dataframe(loss_df, use_container_width=True)

st.divider()

# ─────────────────────────────────────────────
# 🖥️ SYSTEM OVERVIEW TABLE
# ─────────────────────────────────────────────
st.markdown("## 🖥️ Systems Overview")

latest = (
    df.sort_values("timestamp")
    .groupby("system_id")
    .tail(1)
    .sort_values("avg_cpu", ascending=False)
)

latest["Status"] = latest["timestamp"].apply(get_system_status)
latest["Health"] = latest["avg_cpu"].apply(get_status)

table = latest[[
    "system_id", "Status", "avg_cpu", "avg_memory", "avg_disk", "Health"
]]

table.columns = [
    "System", "Status", "CPU (%)", "Memory (%)", "Disk (%)", "Health"
]

st.dataframe(table, use_container_width=True)

st.divider()

# ─────────────────────────────────────────────
# 🔍 SYSTEM DETAILS
# ─────────────────────────────────────────────
st.markdown("## 🔍 System Details")

selected = st.selectbox("Select System", df["system_id"].unique())

system_df = df[df["system_id"] == selected]
latest_row = system_df.iloc[-1]

status = get_system_status(latest_row["timestamp"])

st.markdown(f"### {selected} — {status}")

m1, m2, m3 = st.columns(3)

m1.metric("CPU Usage", f"{latest_row['avg_cpu']:.1f}%", get_status(latest_row["avg_cpu"]))
m2.metric("Memory Usage", f"{latest_row['avg_memory']:.1f}%", get_status(latest_row["avg_memory"]))
m3.metric("Disk Usage", f"{latest_row['avg_disk']:.1f}%", get_status(latest_row["avg_disk"]))

st.markdown("### 📈 Trends")

if len(system_df) > 1:
    st.line_chart(system_df.set_index("timestamp")[["avg_cpu"]])
    st.line_chart(system_df.set_index("timestamp")[["avg_memory"]])
    st.line_chart(system_df.set_index("timestamp")[["avg_disk"]])
else:
    st.info("📊 Not enough data for trends")