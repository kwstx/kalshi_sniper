import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import time
import asyncio
from datetime import datetime
from sniper import run_sniper_cycle

st.set_page_config(page_title="Kalshi Swarm Sniper • Engram Demo", layout="wide")

# Apply dark terminal CSS
st.markdown("""
<style>
    .stApp {
        background-color: #0E1117;
        color: #00FF00;
        font-family: 'Courier New', Courier, monospace;
    }
    h1, h2, h3 {
        color: #00FF00 !important;
    }
    .stButton>button {
        background-color: #00FF00;
        color: #000000;
        font-weight: bold;
        border: 2px solid #00FF00;
        font-size: 20px;
    }
    .stButton>button:hover {
        background-color: #000000;
        color: #00FF00;
        border: 2px solid #00FF00;
    }
    [data-testid="stDataFrame"] {
        background-color: #1E1E1E;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State
if 'is_running' not in st.session_state:
    st.session_state.is_running = False
if 'symbol' not in st.session_state:
    st.session_state.symbol = "BTC"
if 'price' not in st.session_state:
    st.session_state.price = 0.00
if 'confidence' not in st.session_state:
    st.session_state.confidence = 0
if 'timestamps' not in st.session_state:
    st.session_state.timestamps = []
if 'agent_counts' not in st.session_state:
    st.session_state.agent_counts = []
if 'order_log' not in st.session_state:
    st.session_state.order_log = []

symbol = st.session_state.symbol
price = st.session_state.price
confidence = st.session_state.confidence
timestamps = st.session_state.timestamps
agent_counts = st.session_state.agent_counts

# Top Live Ticker
st.subheader(f"LIVE {symbol} • ${price:.2f} • Swarm Active")

col1, col2 = st.columns([1, 1])

with col1:
    # Central Radial Confidence Gauge
    gauge_fig = go.Figure(go.Indicator(
        mode="gauge+number", 
        value=confidence, 
        title={'text': "Swarm Confidence", 'font': {'color': 'white'}},
        gauge={
            "axis": {"range": [0,100], "tickcolor": "white"}, 
            "steps": [
                {"range": [0,50], "color": "red"},
                {"range": [50,70], "color": "yellow"},
                {"range": [70,100], "color": "lime"}
            ],
            "bar": {'color': "white"}
        }
    ))
    gauge_fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"})
    st.plotly_chart(gauge_fig, use_container_width=True)

with col2:
    # Right-side Real-time Swarm Agent Count Line Chart
    line_fig = go.Figure(go.Scatter(
        x=timestamps, 
        y=agent_counts,
        mode='lines+markers',
        line=dict(color='lime', width=3),
        marker=dict(size=8, color='white')
    ))
    line_fig.update_layout(
        title={'text': "Active Swarm Agents", 'font': {'color': 'white'}},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={'color': "white"},
        xaxis=dict(showgrid=False, color="white"),
        yaxis=dict(showgrid=True, gridcolor="gray", color="white")
    )
    st.plotly_chart(line_fig, use_container_width=True)

st.markdown("### Order Log")
# Bottom order-log table with green highlighting on filled rows
def highlight_filled(row):
    status = str(row.get('Status', '')).lower()
    if status == 'filled' or status == 'success':
        return ['background-color: darkgreen; color: lime'] * len(row)
    return [''] * len(row)

df = pd.DataFrame(st.session_state.order_log)
if not df.empty:
    st.dataframe(df.style.apply(highlight_filled, axis=1), use_container_width=True)
else:
    st.dataframe(pd.DataFrame(columns=['Time', 'Symbol', 'Side', 'Confidence', 'Status']), use_container_width=True)

st.divider()

if st.button("START SNIPER", type="primary", use_container_width=True):
    st.session_state.is_running = True
    st.session_state.cycle = asyncio.run(run_sniper_cycle(st.session_state.symbol))
    st.rerun()

if st.session_state.is_running:
    # Setup data from latest cycle
    if 'cycle' in st.session_state and st.session_state.cycle:
        cycle = st.session_state.cycle
        report = cycle.get('report', {})
        order = cycle.get('order', {})
        
        st.session_state.confidence = report.get('confidence', st.session_state.confidence)
        
        # We append to list and prune to keep memory low
        now_str = datetime.now().strftime("%H:%M:%S")
        st.session_state.timestamps.append(now_str)
        st.session_state.timestamps = st.session_state.timestamps[-20:]
        
        # If Engram/Mirofish logic returned num_agents
        agents = report.get('num_agents', len(st.session_state.agent_counts)*10 + 100)
        st.session_state.agent_counts.append(agents)
        st.session_state.agent_counts = st.session_state.agent_counts[-20:]
        
        # Append order log
        if order:
            st.session_state.order_log.append({
                'Time': now_str,
                'Symbol': st.session_state.symbol,
                'Side': report.get('market_direction', 'yes'),
                'Confidence': st.session_state.confidence,
                'Status': order.get('status', 'filled')
            })
            st.session_state.order_log = st.session_state.order_log[-10:]
            
        # Optional: pull dummy price or real one from report if piped back
        # In sniper.py fetch_and_route_to_mirofish hasn't piped 'external_data' back in final report, 
        # so this is just default or mock logic to make the dashboard feel real.
        st.session_state.price += 1.5 
        
        st.session_state.cycle = None # Prevent re-logging the same order if rerun

    time.sleep(30)
    st.session_state.cycle = asyncio.run(run_sniper_cycle(st.session_state.symbol))
    st.rerun()
