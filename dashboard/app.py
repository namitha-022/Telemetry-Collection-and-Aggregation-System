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
    page_title="Telemetry Dashboard",
    layout="wide"
)

st.title("Telemetry Monitoring Dashboard")

# Auto refresh every 2 seconds
st_autorefresh(interval=2000)

# ─────────────────────────────────────────────
# Helper Functions
# ─────────────────────────────────────────────
def get_status(value):
    if value >= 80:
        return "Critical", "🔴"
    elif value >= 60:
        return "Warning", "🟡"
    return "Healthy", "🟢"

def get_system_status(last_timestamp):
    return "🟢 Online" if (time.time() - last_timestamp) < 5 else "🔴 Offline"

# ─────────────────────────────────────────────
# Data Fetch
# ─────────────────────────────────────────────
try:
    metrics = requests.get(f"{SERVER_URL}/metrics", timeout=2).json()
    analysis = requests.get(f"{SERVER_URL}/analysis", timeout=2).json()

    if not metrics:
        st.metric("Connected Systems", 0)
        st.warning("⚠️ No systems are currently sending data.")
        st.stop()

    df = pd.DataFrame(metrics)

    # ─────────────────────────────────────────────
    # Top KPIs
    # ─────────────────────────────────────────────
    systems = df["system_id"].nunique()

    k1, k2, k3 = st.columns(3)

    k1.metric("Connected Systems", systems)
    k2.metric("Average CPU", f"{analysis.get('overall_avg_cpu', 0):.2f}%")
    k3.metric("Max CPU", f"{analysis.get('max_cpu', 0):.2f}%")

    st.markdown("---")

    # ─────────────────────────────────────────────
    # System Overview
    # ─────────────────────────────────────────────
    st.subheader("System Overview")

    latest_all = (
        df.sort_values("timestamp")
        .groupby("system_id")
        .tail(1)
        .sort_values("avg_cpu", ascending=False)
    )

    overview_df = latest_all[[
        "system_id", "avg_cpu", "avg_memory", "avg_disk"
    ]].copy()

    overview_df.columns = ["System", "CPU (%)", "Memory (%)", "Disk (%)"]

    # Add status column
    overview_df["Status"] = latest_all["timestamp"].apply(get_system_status)

    st.dataframe(overview_df, use_container_width=True)

    st.markdown("---")

    # ─────────────────────────────────────────────
    # System Details
    # ─────────────────────────────────────────────
    st.subheader("System Details")

    selected_system = st.selectbox(
        "Select System",
        df["system_id"].unique()
    )

    system_df = df[df["system_id"] == selected_system]
    latest = system_df.iloc[-1]

    # System status
    system_status = get_system_status(latest["timestamp"])

    st.markdown(f"**System:** {selected_system} &nbsp;&nbsp;&nbsp; **Status:** {system_status}")

    # ─────────────────────────────────────────────
    # Metrics Row (with color hints)
    # ─────────────────────────────────────────────
    cpu_status, cpu_icon = get_status(latest["avg_cpu"])
    mem_status, mem_icon = get_status(latest["avg_memory"])
    disk_status, disk_icon = get_status(latest["avg_disk"])

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "CPU Usage",
        f"{latest['avg_cpu']:.1f}% {cpu_icon}",
        help=cpu_status
    )

    c2.metric(
        "Memory Usage",
        f"{latest['avg_memory']:.1f}% {mem_icon}",
        help=mem_status
    )

    c3.metric(
        "Disk Usage",
        f"{latest['avg_disk']:.1f}% {disk_icon}",
        help=disk_status
    )

    st.markdown("---")

    # ─────────────────────────────────────────────
    # Charts
    # ─────────────────────────────────────────────
    st.subheader("CPU Usage Over Time")
    st.line_chart(system_df.set_index("timestamp")[["avg_cpu"]])

    st.subheader("Memory Usage Over Time")
    st.line_chart(system_df.set_index("timestamp")[["avg_memory"]])

    st.subheader("Disk Usage Over Time")
    st.line_chart(system_df.set_index("timestamp")[["avg_disk"]])

except Exception as e:
    st.error(f"❌ Server not reachable: {e}")