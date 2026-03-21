import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime

st.set_page_config(page_title="Telemetry Dashboard", layout="wide", page_icon="📡")

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Inter:wght@400;500;600&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .metric-card {
        border-radius: 12px;
        padding: 18px 22px;
        margin-bottom: 8px;
        border: 1px solid rgba(255,255,255,0.08);
    }
    .card-green  { background: linear-gradient(135deg, #0f2e1a 0%, #1a4a2a 100%); border-color: #2ecc71; }
    .card-yellow { background: linear-gradient(135deg, #2e2a0f 0%, #4a420a 100%); border-color: #f1c40f; }
    .card-red    { background: linear-gradient(135deg, #2e0f0f 0%, #4a1a1a 100%); border-color: #e74c3c; }

    .metric-title  { font-size: 15px; letter-spacing: 1.5px; text-transform: uppercase; opacity: 0.6; margin-bottom: 4px; }
    .metric-value  { font-family: 'JetBrains Mono', monospace; font-size: 36px; font-weight: 600; line-height: 1; }
    .metric-sub    { font-size: 13px; opacity: 0.55; margin-top: 6px; }
    .metric-trend  { font-size: 15px; font-weight: 600; margin-top: 4px; }

    .badge {
        display: inline-block;
        padding: 4px 14px;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 600;
        letter-spacing: 0.5px;
        margin-left: 10px;
        vertical-align: middle;
    }
    .badge-green  { background: #1a4a2a; color: #2ecc71; border: 1px solid #2ecc71; }
    .badge-yellow { background: #4a420a; color: #f1c40f; border: 1px solid #f1c40f; }
    .badge-red    { background: #4a1a1a; color: #e74c3c; border: 1px solid #e74c3c; }

    .health-bar-outer {
        background: rgba(255,255,255,0.08);
        border-radius: 999px;
        height: 8px;
        width: 100%;
        margin-top: 8px;
    }
    .health-bar-inner {
        height: 8px;
        border-radius: 999px;
    }

    .section-header {
        font-size: 15px;
        letter-spacing: 2px;
        text-transform: uppercase;
        opacity: 0.5;
        margin: 24px 0 12px;
        border-bottom: 1px solid rgba(255,255,255,0.06);
        padding-bottom: 6px;
    }

    .last-updated {
        font-size: 11px;
        opacity: 0.35;
        font-family: 'JetBrains Mono', monospace;
    }
</style>
""", unsafe_allow_html=True)

SERVER = "http://localhost:8000"

# ── Helpers ───────────────────────────────────────────────────────────────────
def get_color(value, warn=60, crit=80):
    if value >= crit:
        return "red", "🔴", "Critical"
    if value >= warn:
        return "yellow", "🟡", "Warning"
    return "green", "🟢", "Healthy"

def trend_arrow(current, previous):
    if previous is None:
        return "─", "opacity:0.4"
    diff = current - previous
    if abs(diff) < 0.5:
        return "─", "opacity:0.4"
    if diff > 0:
        return f"↑ +{diff:.1f}%", "color:#e74c3c"
    return f"↓ {diff:.1f}%", "color:#2ecc71"

def health_score(cpu, mem, disk):
    penalty = 0
    for v in [cpu, mem, disk]:
        if v >= 80:
            penalty += 30
        elif v >= 60:
            penalty += 10
    return max(0, 100 - penalty)

def score_color(score):
    if score >= 80:
        return "#2ecc71", "green", "Healthy"
    if score >= 50:
        return "#f1c40f", "yellow", "Warning"
    return "#e74c3c", "red", "Critical"

def area_chart_config(df, col, color, threshold=80):
    import altair as alt

    df2 = df[["time_label", col]].copy()
    df2.columns = ["Time", "Value"]

    base = alt.Chart(df2).encode(
        x=alt.X("Time:O", axis=alt.Axis(labelAngle=-45, title=None)),
        y=alt.Y("Value:Q", scale=alt.Scale(domain=[0, 100]),
                axis=alt.Axis(title="%", tickCount=5))
    )

    area = base.mark_area(
        color=color,
        opacity=0.25,
        line={"color": color, "strokeWidth": 2},
        point={"color": color, "size": 40}
    )

    rule = alt.Chart(
        pd.DataFrame({"threshold": [threshold]})
    ).mark_rule(
        color="#e74c3c", strokeDash=[6, 3], strokeWidth=1.5
    ).encode(y="threshold:Q")

    label_df = pd.DataFrame({
        "threshold": [threshold],
        "Time": [df2["Time"].iloc[-1]]
    })
    threshold_label = alt.Chart(label_df).mark_text(
        align="right", color="#e74c3c", fontSize=11, dx=-4, dy=-8
    ).encode(
        x=alt.X("Time:O"),
        y=alt.Y("threshold:Q"),
        text=alt.value(f"Danger: {threshold}%")
    )

    chart = (area + rule + threshold_label).properties(height=220).configure_view(
        strokeWidth=0
    ).configure_axis(
        grid=True,
        gridColor="rgba(255,255,255,0.05)",
        domainColor="transparent",
        tickColor="transparent",
        labelColor="rgba(255,255,255,0.4)",
        labelFontSize=11
    )
    return chart


# ── Main loop ─────────────────────────────────────────────────────────────────
st.title("Telemetry Monitor")

placeholder = st.empty()
prev = {"cpu": None, "memory": None, "disk": None}

while True:
    try:
        metrics_raw  = requests.get(f"{SERVER}/metrics",  timeout=3).json()
        analysis_raw = requests.get(f"{SERVER}/analysis", timeout=3).json()

        if metrics_raw:
            df = pd.DataFrame(metrics_raw)
            df["time_label"] = pd.to_datetime(
                df["timestamp"], unit="s"
            ).dt.strftime("%H:%M")

            latest   = df.iloc[-1]
            cpu_val  = round(latest["avg_cpu"],    1)
            mem_val  = round(latest["avg_memory"], 1)
            disk_val = round(latest["avg_disk"],   1)

            score               = health_score(cpu_val, mem_val, disk_val)
            bar_color, badge_cls, score_label = score_color(score)

            cpu_color,  cpu_icon,  cpu_label  = get_color(cpu_val)
            mem_color,  mem_icon,  mem_label  = get_color(mem_val)
            disk_color, disk_icon, disk_label = get_color(disk_val, warn=70, crit=90)

            cpu_arrow,  cpu_style  = trend_arrow(cpu_val,  prev["cpu"])
            mem_arrow,  mem_style  = trend_arrow(mem_val,  prev["memory"])
            disk_arrow, disk_style = trend_arrow(disk_val, prev["disk"])

            min_cpu  = round(df["avg_cpu"].min(),    1)
            max_cpu  = round(df["avg_cpu"].max(),    1)
            min_mem  = round(df["avg_memory"].min(), 1)
            max_mem  = round(df["avg_memory"].max(), 1)
            min_disk = round(df["avg_disk"].min(),   1)
            max_disk = round(df["avg_disk"].max(),   1)

            with placeholder.container():

                # ── Health Score ──────────────────────────────────────────
                st.markdown('<div class="section-header">System Health</div>',
                            unsafe_allow_html=True)
                hcol1, hcol2 = st.columns([4, 1])
                with hcol1:
                    st.markdown(f"""
                    <div style="font-size:15px; font-weight:600; margin-bottom:6px;">
                        Overall Health Score:
                        <span style="color:{bar_color}; font-size:22px; margin: 0 6px;">
                            {score}/100
                        </span>
                        <span class="badge badge-{badge_cls}">{score_label}</span>
                    </div>
                    <div class="health-bar-outer">
                        <div class="health-bar-inner"
                             style="width:{score}%; background:{bar_color};">
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                with hcol2:
                    st.markdown(
                        f'<div class="last-updated" style="text-align:right; margin-top:6px;">'
                        f'Updated<br>{datetime.now().strftime("%H:%M:%S")}</div>',
                        unsafe_allow_html=True
                    )

                st.markdown("---")

                # ── Metric Cards ──────────────────────────────────────────
                st.markdown('<div class="section-header">Current Metrics</div>',
                            unsafe_allow_html=True)
                c1, c2, c3 = st.columns(3)

                cards = [
                    (c1, "CPU Usage",    cpu_val,  cpu_color,  cpu_arrow,  cpu_style,  min_cpu,  max_cpu,  cpu_icon,  cpu_label),
                    (c2, "Memory Usage", mem_val,  mem_color,  mem_arrow,  mem_style,  min_mem,  max_mem,  mem_icon,  mem_label),
                    (c3, "Disk Usage",   disk_val, disk_color, disk_arrow, disk_style, min_disk, max_disk, disk_icon, disk_label),
                ]

                for col_ctx, label, val, color, arrow, astyle, mn, mx, icon, badge in cards:
                    with col_ctx:
                        st.markdown(f"""
                        <div class="metric-card card-{color}">
                            <div class="metric-title">{label}</div>
                            <div class="metric-value">{val}
                                <span style="font-size:16px; opacity:0.5;">%</span>
                            </div>
                            <div class="metric-trend" style="{astyle}">{arrow}</div>
                            <div class="metric-sub">
                                Min <b>{mn}%</b> &nbsp;|&nbsp; Max <b>{mx}%</b>
                                &nbsp;&nbsp;{icon} <b>{badge}</b>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                st.markdown("---")

                # ── Aggregated Stats ──────────────────────────────────────
                st.markdown('<div class="section-header">Aggregated Analysis</div>',
                            unsafe_allow_html=True)
                a1, a2, a3, a4 = st.columns(4)
                a1.metric("Avg CPU",    f"{round(analysis_raw.get('overall_avg_cpu', 0), 2)}%")
                a2.metric("Peak CPU",   f"{round(analysis_raw.get('max_cpu', 0), 2)}%")
                a3.metric("Avg Memory", f"{round(df['avg_memory'].mean(), 2)}%")
                a4.metric("Avg Disk",   f"{round(df['avg_disk'].mean(), 2)}%")

                st.markdown("---")

                # ── Charts ────────────────────────────────────────────────
                st.markdown('<div class="section-header">CPU Usage Over Time</div>',
                            unsafe_allow_html=True)
                st.altair_chart(
                    area_chart_config(df, "avg_cpu", "#3498db", threshold=80),
                    use_container_width=True
                )

                st.markdown('<div class="section-header">Memory Usage Over Time</div>',
                            unsafe_allow_html=True)
                st.altair_chart(
                    area_chart_config(df, "avg_memory", "#9b59b6", threshold=80),
                    use_container_width=True
                )

                st.markdown('<div class="section-header">Disk Usage Over Time</div>',
                            unsafe_allow_html=True)
                st.altair_chart(
                    area_chart_config(df, "avg_disk", "#e67e22", threshold=90),
                    use_container_width=True
                )

            prev = {"cpu": cpu_val, "memory": mem_val, "disk": disk_val}

        else:
            with placeholder.container():
                st.info("⏳ Waiting for data from agents...")

    except Exception as e:
        with placeholder.container():
            st.error(f"❌ Cannot reach server: {e}")

    time.sleep(2)