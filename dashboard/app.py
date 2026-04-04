import streamlit as st
import pandas as pd
import requests
import time
import plotly.express as px
from streamlit_autorefresh import st_autorefresh

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
API_BASE = "http://localhost:8001"

st.set_page_config(
    page_title="Telemetry Dashboard",
    layout="wide",
    page_icon="📡"
)

# Auto refresh (smooth)
st_autorefresh(interval=2000, key="refresh")

# ─────────────────────────────────────────────
# 🎨 CUSTOM UI (PROFESSIONAL STYLE)
# ─────────────────────────────────────────────
st.markdown("""
<style>
/* Background */
body {
    background-color: #0E1117;
}

/* KPI Cards */
div[data-testid="stMetric"] {
    background-color: #1A1F2B;
    padding: 18px;
    border-radius: 12px;
    border: 1px solid #2A2F3A;
}

/* Section spacing */
.block-container {
    padding-top: 2rem;
}

/* Headings */
h1, h2, h3 {
    font-weight: 700;
}

/* Dataframe */
[data-testid="stDataFrame"] {
    border-radius: 10px;
    overflow: hidden;
}
</style>
""", unsafe_allow_html=True)

st.title("📡 Telemetry Monitoring Dashboard")
st.caption("Real-time system metrics • Network health • Performance analytics")

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def get_status(value):
    try:
        value = float(value)
        if value >= 80:
            return "🔴 Critical"
        elif value >= 60:
            return "🟡 Warning"
        return "🟢 Healthy"
    except:
        return "⚪ Unknown"


def get_system_status(ts):
    try:
        ts = float(ts)
        return "🟢 Online" if (time.time() - ts) < 5 else "🔴 Offline"
    except:
        return "⚪ Unknown"


@st.cache_data(ttl=2)
def fetch_data():
    try:
        res = requests.get(f"{API_BASE}/dashboard", timeout=2)
        res.raise_for_status()
        return res.json()
    except requests.exceptions.RequestException:
        return {"metrics": [], "stats": {}}


# ─────────────────────────────────────────────
# DATA
# ─────────────────────────────────────────────
data = fetch_data()
metrics = data.get("metrics", [])
stats = data.get("stats", {})

if not metrics:
    st.warning("⏳ Waiting for telemetry data...")
    st.stop()

df = pd.DataFrame(metrics)

required_cols = ["system_id", "avg_cpu", "avg_memory", "avg_disk", "timestamp"]
if not all(col in df.columns for col in required_cols):
    st.error("Invalid API response")
    st.stop()

df = df.sort_values("timestamp")

# ─────────────────────────────────────────────
# 📊 KPI SECTION (CARDS)
# ─────────────────────────────────────────────
st.markdown("## 📊 System Overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Active Systems", df["system_id"].nunique())
col2.metric("Avg CPU", f"{df['avg_cpu'].mean():.2f}%")
col3.metric("Max CPU", f"{df['avg_cpu'].max():.2f}%")
col4.metric("Total Records", len(df))

# ─────────────────────────────────────────────
# 🌐 NETWORK
# ─────────────────────────────────────────────
st.markdown("## 🌐 Network Health")

c1, c2, c3 = st.columns(3)

c1.metric("Packets", f"{stats.get('total_received', 0):,}")
c2.metric("Throughput", f"{stats.get('throughput', 0):.2f} pkt/s")
c3.metric("Loss", f"{stats.get('packet_loss_percent', 0):.2f}%")

# ─────────────────────────────────────────────
# 🖥️ SYSTEM TABLE
# ─────────────────────────────────────────────
st.markdown("## 🖥️ Systems Overview")

latest = (
    df.groupby("system_id")
    .tail(1)
    .sort_values("avg_cpu", ascending=False)
)

latest["Status"] = latest["timestamp"].apply(get_system_status)
latest["Health"] = latest["avg_cpu"].apply(get_status)

table = latest[
    ["system_id", "Status", "avg_cpu", "avg_memory", "avg_disk", "Health"]
].copy()

table.columns = ["System", "Status", "CPU", "Memory", "Disk", "Health"]

st.dataframe(table, use_container_width=True)

# ─────────────────────────────────────────────
# 🔍 DETAILS (STATE SAFE)
# ─────────────────────────────────────────────
st.markdown("## 🔍 System Details")

systems = sorted(df["system_id"].unique())

if "selected_system" not in st.session_state:
    st.session_state.selected_system = systems[0]

selected = st.selectbox(
    "Select System",
    systems,
    index=systems.index(st.session_state.selected_system)
)

st.session_state.selected_system = selected

system_df = df[df["system_id"] == selected]

if system_df.empty:
    st.warning("No data available")
    st.stop()

latest_row = system_df.iloc[-1]
status = get_system_status(latest_row["timestamp"])

st.markdown(f"### {selected} — {status}")

m1, m2, m3 = st.columns(3)

m1.metric("CPU", f"{latest_row['avg_cpu']:.1f}%", get_status(latest_row["avg_cpu"]))
m2.metric("Memory", f"{latest_row['avg_memory']:.1f}%", get_status(latest_row["avg_memory"]))
m3.metric("Disk", f"{latest_row['avg_disk']:.1f}%", get_status(latest_row["avg_disk"]))

# ─────────────────────────────────────────────
# 📈 MODERN CHART
# ─────────────────────────────────────────────
st.markdown("### 📈 Performance Trends")

fig = px.line(
    system_df,
    x="timestamp",
    y=["avg_cpu", "avg_memory", "avg_disk"],
    template="plotly_dark"
)

fig.update_layout(
    legend_title_text='Metrics',
    hovermode="x unified"
)

st.plotly_chart(fig, use_container_width=True)