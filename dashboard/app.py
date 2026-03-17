import streamlit as st
import requests
import pandas as pd
import time

st.set_page_config(page_title="Telemetry Dashboard", layout="wide")

st.title("📊 Telemetry Dashboard")

SERVER = "http://localhost:8000"

placeholder = st.empty()

while True:
    try:
        metrics = requests.get(f"{SERVER}/metrics").json()
        analysis = requests.get(f"{SERVER}/analysis").json()

        if metrics:
            df = pd.DataFrame(metrics)

            # Convert timestamp → readable time
            df["time"] = pd.to_datetime(df["timestamp"], unit='s')

            with placeholder.container():

                # 🔹 Analysis Section
                st.subheader("📈 Analysis")
                col1, col2 = st.columns(2)

                col1.metric("Avg CPU", round(analysis.get("overall_avg_cpu", 0), 2))
                col2.metric("Max CPU", round(analysis.get("max_cpu", 0), 2))

                # 🔹 Charts
                st.subheader("CPU Usage Over Time")
                st.line_chart(df.set_index("time")["avg_cpu"])

                st.subheader("Memory Usage Over Time")
                st.line_chart(df.set_index("time")["avg_memory"])

                st.subheader("Disk Usage Over Time")
                st.line_chart(df.set_index("time")["avg_disk"])

    except Exception as e:
        st.error(f"Error: {e}")

    time.sleep(2)