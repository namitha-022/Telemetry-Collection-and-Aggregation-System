import streamlit as st
import requests
import pandas as pd
import time
from streamlit_autorefresh import st_autorefresh
from common.config import SERVER_URL

# ─────────────────────────────────────────────
# Page Config
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Telemetry Monitoring",
    layout="wide"
)

st.title("📡 Telemetry Monitoring Dashboard")
st.caption("Real-time system telemetry, network health, and performance insights")

st_autorefresh(interval=2000)

# ─────────────────────────────────────────────
# Helper Functions
# ─────────────────────────────────────────────
def get_status(value):
    if value >= 80:
        return "🔴 Critical"
    elif value >= 60:
        return "🟡 Warning"
    return "🟢 Healthy"


def get_system_status(last_timestamp):
    return "🟢 Online" if (time.time() - last_timestamp) < 5 else "🔴 Offline"


# ─────────────────────────────────────────────
# Data Fetch
# ─────────────────────────────────────────────
try:
    metrics = requests.get(f"{SERVER_URL}/metrics", timeout=2).json()
    analysis = requests.get(f"{SERVER_URL}/analysis", timeout=2).json()
    stats = requests.get(f"{SERVER_URL}/stats", timeout=2).json()

    if not metrics:
        st.warning("⚠️ No telemetry data available")
        st.stop()

    df = pd.DataFrame(metrics)

    # ─────────────────────────────────────────────
    # 🔷 TOP KPIs
    # ─────────────────────────────────────────────
    st.markdown("## 📊 System Overview")

    systems = df["system_id"].nunique()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("🖥️ Active Systems", systems)
    col2.metric("⚡ Avg CPU", f"{analysis.get('overall_avg_cpu', 0):.2f}%")
    col3.metric("🔥 Max CPU", f"{analysis.get('max_cpu', 0):.2f}%")
    col4.metric("📦 Total Records", len(df))

    st.markdown("---")

    # ─────────────────────────────────────────────
    # 📡 NETWORK METRICS
    # ─────────────────────────────────────────────
    st.markdown("## 📡 Network Health")

    total_received = stats.get("total_received", 0)
    throughput = stats.get("throughput", 0)
    packet_loss = stats.get("packet_loss", {})

    loss_total = sum(packet_loss.values())

    c1, c2, c3 = st.columns(3)

    c1.metric("📥 Packets Received", f"{total_received:,}")
    c2.metric("🚀 Throughput", f"{throughput:.2f} pkt/s")
    c3.metric("⚠️ Packet Loss", loss_total)

    # Loss breakdown
    if packet_loss:
        st.markdown("### Packet Loss by System")

        loss_df = pd.DataFrame(
            list(packet_loss.items()),
            columns=["System", "Packets Lost"]
        ).sort_values("Packets Lost", ascending=False)

        st.dataframe(loss_df, use_container_width=True)

    st.markdown("---")

    # ─────────────────────────────────────────────
    # 🖥️ SYSTEM TABLE
    # ─────────────────────────────────────────────
    st.markdown("## 🖥️ Systems Status")

    latest_all = (
        df.sort_values("timestamp")
        .groupby("system_id")
        .tail(1)
        .sort_values("avg_cpu", ascending=False)
    )

    overview_df = latest_all.copy()

    overview_df["Status"] = overview_df["timestamp"].apply(get_system_status)
    overview_df["CPU Status"] = overview_df["avg_cpu"].apply(get_status)

    overview_df = overview_df[[
        "system_id", "Status", "avg_cpu", "avg_memory", "avg_disk", "CPU Status"
    ]]

    overview_df.columns = [
        "System", "Status", "CPU (%)", "Memory (%)", "Disk (%)", "Health"
    ]

    st.dataframe(overview_df, use_container_width=True)

    st.markdown("---")

    # ─────────────────────────────────────────────
    # 🔍 SYSTEM DETAILS
    # ─────────────────────────────────────────────
    st.markdown("## 🔍 System Details")

    selected_system = st.selectbox(
        "Select a system",
        df["system_id"].unique()
    )

    system_df = df[df["system_id"] == selected_system]
    latest = system_df.iloc[-1]

    status = get_system_status(latest["timestamp"])

    st.markdown(f"### {selected_system} — {status}")

    cpu_status = get_status(latest["avg_cpu"])
    mem_status = get_status(latest["avg_memory"])
    disk_status = get_status(latest["avg_disk"])

    m1, m2, m3 = st.columns(3)

    m1.metric("CPU Usage", f"{latest['avg_cpu']:.1f}%", cpu_status)
    m2.metric("Memory Usage", f"{latest['avg_memory']:.1f}%", mem_status)
    m3.metric("Disk Usage", f"{latest['avg_disk']:.1f}%", disk_status)

    st.markdown("### 📈 Trends")

    st.line_chart(system_df.set_index("timestamp")[["avg_cpu"]])
    st.line_chart(system_df.set_index("timestamp")[["avg_memory"]])
    st.line_chart(system_df.set_index("timestamp")[["avg_disk"]])

except Exception as e:
    st.error(f"❌ Unable to connect to server: {e}")