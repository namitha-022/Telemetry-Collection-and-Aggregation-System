import streamlit as st
import requests
import pandas as pd
from streamlit_autorefresh import st_autorefresh
from common.config import SERVER_URL

st.set_page_config(page_title="Telemetry Dashboard", layout="wide")

st.title("📡 Multi-System Telemetry Dashboard")

# 🔁 auto refresh
st_autorefresh(interval=2000)

try:
    metrics = requests.get(f"{SERVER_URL}/metrics", timeout=2).json()
    analysis = requests.get(f"{SERVER_URL}/analysis", timeout=2).json()

    if not metrics:
        st.metric("Connected Systems", 0)
        st.info("No systems connected")
        st.stop()

    df = pd.DataFrame(metrics)

    systems = df["system_id"].unique()
    st.metric("Connected Systems", len(systems))

    selected = st.selectbox("Select System", systems)

    filtered = df[df["system_id"] == selected]
    latest = filtered.iloc[-1]

    col1, col2, col3 = st.columns(3)
    col1.metric("CPU", f"{latest['avg_cpu']:.1f}%")
    col2.metric("Memory", f"{latest['avg_memory']:.1f}%")
    col3.metric("Disk", f"{latest['avg_disk']:.1f}%")

    st.subheader("CPU Usage")
    st.line_chart(filtered.set_index("timestamp")[["avg_cpu"]])

    st.subheader("Memory Usage")
    st.line_chart(filtered.set_index("timestamp")[["avg_memory"]])

    st.subheader("Disk Usage")
    st.line_chart(filtered.set_index("timestamp")[["avg_disk"]])

    st.subheader("Overall Analysis")
    st.write(analysis)

except Exception as e:
    st.error(f"Server not reachable: {e}")