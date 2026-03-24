import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import time
import asyncio
from datetime import datetime
from sniper import run_sniper_cycle

st.set_page_config(page_title="Kalshi Swarm Sniper • Engram Demo", layout="wide", initial_sidebar_state="collapsed")

# Read state
if 'is_running' not in st.session_state:
    st.session_state.is_running = False
if 'symbol' not in st.session_state:
    st.session_state.symbol = "BTC"
if 'price' not in st.session_state:
    st.session_state.price = 95230.00
if 'confidence' not in st.session_state:
    st.session_state.confidence = 85
if 'timestamps' not in st.session_state:
    st.session_state.timestamps = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
if 'agent_counts' not in st.session_state:
    st.session_state.agent_counts = [3000, 15000, 10000, 18000, 12000, 38000, 19000, 8000, 15000, 20000, 10000, 12000]
if 'order_log' not in st.session_state:
    st.session_state.order_log = []

# --- CSS INJECTION (VANILLA CSS FOR EXACT MATCH) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Global App Styles */
    .stApp {
        background-color: #FAFAFA;
        font-family: 'Inter', sans-serif !important;
        color: #111827;
    }
    .main .block-container {
        max-width: 1200px;
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }
    header, footer { visibility: hidden; }
    
    /* Typography */
    .nav-text { color: #9CA3AF; font-size: 14px; margin-bottom: 24px; font-weight: 500; }
    .nav-text strong { color: #111827; font-weight: 600; }
    .welcome-text { font-size: 32px; font-weight: 600; color: #111827; margin-bottom: 32px; }
    
    /* Metric Cards */
    .metric-card {
        background-color: #FFFFFF;
        border: 1px solid #F3F4F6;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0px 4px 6px -1px rgba(0, 0, 0, 0.05), 0px 2px 4px -1px rgba(0, 0, 0, 0.03);
        height: 100%;
        position: relative;
    }
    .metric-title {
        font-size: 11px; color: #9CA3AF; text-transform: uppercase; font-weight: 600; letter-spacing: 1px; margin-bottom: 16px;
        display: flex; justify-content: space-between; align-items: center;
    }
    .metric-value-container { display: flex; align-items: baseline; }
    .metric-value { font-size: 30px; font-weight: 700; color: #111827; line-height: 1.2; }
    .metric-sub { font-size: 14px; color: #6B7280; margin-left: 8px; font-weight: 500; }
    .metric-footer {
        margin-top: 24px; font-size: 13px; color: #9CA3AF; display: flex; align-items: center; justify-content: space-between;
    }
    .circle-icon {
        background: #F3F4F6; color: #9CA3AF; padding: 4px; border-radius: 50%; min-width: 24px; min-height: 24px; 
        display: inline-flex; align-items: center; justify-content: center; font-size: 14px; font-weight: 700;
    }
    .badge-positive { color: #10B981; font-weight: 600; font-size: 12px; }
    .badge-neutral { color: #6B7280; font-weight: 600; font-size: 12px; }
    
    /* Chart Card Overrides */
    div[data-testid="stMarkdownContainer"] p {
        margin-bottom: 0 !important;
    }
    /* Eliminate padding between markdown header and Plotly */
    .stPlotlyChart {
        margin-top: -16px !important;
    }
    /* Remove padding around columns slightly */
    div[data-testid="column"] {
        padding: 0 10px !important;
    }

    [data-testid="stDataFrame"] {
        background-color: #FFFFFF;
        border-radius: 8px;
    }

    /* Target the text input and button for bottom controls */
    div[data-testid="stTextInput"] label p { color: #111827; font-weight: 600; font-family: 'Inter'; }
    div[data-testid="stTextInput"] input { border-radius: 8px; border: 1px solid #D1D5DB; }
    .stButton button { 
        background-color: #111827 !important; color: #FFFFFF !important; font-weight: 600; border-radius: 8px; font-family: 'Inter';
        transition: all 0.2s ease; border: none; padding: 8px 16px !important; height: auto !important;
        font-size: 13px !important;
    }
    .stButton button:hover { background-color: #374151 !important; transform: translateY(-1px); box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
</style>
""", unsafe_allow_html=True)

# --- Top Nav & Title Area ---
st.markdown("""
<div class="nav-text">Kalshi Sniper &gt; <strong>Swarm Mode</strong></div>
""", unsafe_allow_html=True)

title_col, input_col, btn_col = st.columns([3, 0.8, 0.8])
with title_col:
    st.markdown(f'<div class="welcome-text" style="margin-bottom:0px;">Live Dashboard: {st.session_state.symbol}</div>', unsafe_allow_html=True)
with input_col:
    st.markdown('<div style="margin-top: 8px;">', unsafe_allow_html=True)
    target_symbol = st.text_input("Asset", value=st.session_state.symbol, label_visibility="collapsed", key="top_symbol_input")
    st.markdown('</div>', unsafe_allow_html=True)
with btn_col:
    st.markdown('<div style="margin-top: 8px;">', unsafe_allow_html=True)
    if st.button("START SNIPER", use_container_width=True):
        st.session_state.symbol = target_symbol
        st.session_state.is_running = True
        st.session_state.cycle = asyncio.run(run_sniper_cycle(st.session_state.symbol))
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- Top Cards ---
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">TARGET PRICE <span style="font-size:16px;">⋯</span></div>
        <div class="metric-value-container">
            <div class="metric-value">${st.session_state.price:,.2f}</div>
        </div>
        <div style="position: absolute; right: 24px; top: 60px; height: 30px; width: 60px; display: flex; align-items: flex-end; gap: 2px;">
            <div style="width: 4px; height: 10px; background: #E5E7EB; border-radius: 2px;"></div>
            <div style="width: 4px; height: 16px; background: #E5E7EB; border-radius: 2px;"></div>
            <div style="width: 4px; height: 24px; background: #E5E7EB; border-radius: 2px;"></div>
            <div style="width: 4px; height: 14px; background: #111827; border-radius: 2px;"></div>
        </div>
        <div class="metric-footer">
            <div class="circle-icon" style="background:#E5E7EB; color:#6B7280; font-size:10px;">●</div>
            <span class="badge-neutral" style="color: #6B7280;">Live Binance Data</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">SWARM CONFIDENCE <span style="font-size:16px;">⋯</span></div>
        <div class="metric-value-container">
            <div class="metric-value">{st.session_state.confidence}</div>
            <div class="metric-sub">% Probability</div>
        </div>
        <div style="position: absolute; right: 24px; top: 60px; height: 30px; width: 60px; display: flex; align-items: flex-end; gap: 2px;">
            <div style="width: 4px; height: 16px; background: #E5E7EB; border-radius: 2px;"></div>
            <div style="width: 4px; height: 28px; background: #111827; border-radius: 2px;"></div>
            <div style="width: 4px; height: 10px; background: #E5E7EB; border-radius: 2px;"></div>
            <div style="width: 4px; height: 20px; background: #E5E7EB; border-radius: 2px;"></div>
        </div>
        <div class="metric-footer">
            <div class="circle-icon" style="background:#E5E7EB; color:#6B7280; font-size:10px;">➔</div>
            <span class="badge-neutral" style="color: #6B7280;">>70% Required for Trade</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">KALSHI ORDERS <span style="font-size:16px;">⋯</span></div>
        <div class="metric-value-container">
            <div class="metric-value">{len(st.session_state.order_log)}</div>
            <div class="metric-sub">Filled Orders</div>
        </div>
        <div class="metric-footer" style="justify-content: space-between;">
            <div class="circle-icon" style="background:#E5E7EB; color:#6B7280; font-size:10px;">✓</div>
            <span class="badge-neutral" style="color: #6B7280;">Connected to Engram</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.write("") # Vertical spacing

# --- Order Log Card (Using Premium Chart Design) ---
st.markdown(f"""
<div style="background-color: #FFFFFF; border: 1px solid #F3F4F6; border-bottom: none; border-radius: 16px 16px 0 0; padding: 24px 24px 0 24px; box-shadow: 0px -2px 6px -1px rgba(0, 0, 0, 0.02); margin-top: 16px;">
    <div style="font-size: 11px; color: #9CA3AF; text-transform: uppercase; font-weight: 600; letter-spacing: 1px; margin-bottom: 24px; display: flex; justify-content: space-between;">
        ORDER EXECUTION LOG <span style="background: #F3F4F6; border-radius: 50%; width: 18px; height: 18px; display: inline-flex; align-items: center; justify-content: center; font-size: 10px; color: #9CA3AF;">ℹ</span>
        <span style="font-size:16px;">⋯</span>
    </div>
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
        <div style="font-size: 20px; font-weight: 600; color: #6B7280; display: flex; align-items: baseline; gap: 8px;">
            Total Fills : <span style="font-size: 32px; font-weight: 700; color: #111827;">{len(st.session_state.order_log)}</span>
        </div>
        <div style="display: flex; align-items: center; gap: 32px;">
            <div style="display: flex; gap: 16px;">
                <div style="font-size: 12px; color: #9CA3AF; font-weight: 600; text-transform: uppercase; display: flex; align-items: center;"><span style="display:inline-block; width:8px; height:8px; border-radius:50%; background:#F3F4F6; margin-right:8px; border: 1px solid #E5E7EB;"></span> REQUESTED</div>
                <div style="font-size: 12px; color: #111827; font-weight: 600; text-transform: uppercase; display: flex; align-items: center;"><span style="display:inline-block; width:8px; height:8px; border-radius:50%; background:#111827; margin-right:8px;"></span> EXECUTED</div>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Table display inside the card
def highlight_filled(row):
    status = str(row.get('Status', '')).lower()
    if status == 'filled' or status == 'success':
        return ['background-color: #f0fdf4; color: #166534'] * len(row)
    return [''] * len(row)

df = pd.DataFrame(st.session_state.order_log)
if not df.empty:
    st.dataframe(df.style.apply(highlight_filled, axis=1), use_container_width=True, height=350)
else:
    st.dataframe(pd.DataFrame(columns=['Time', 'Symbol', 'Side', 'Confidence', 'Status']), use_container_width=True, height=350)

# Close the visual container of the card
st.markdown("""
<div style="background-color: #FFFFFF; border: 1px solid #F3F4F6; border-top: none; border-radius: 0 0 16px 16px; height: 16px; margin-top: -10px; box-shadow: 0px 4px 6px -1px rgba(0, 0, 0, 0.05); margin-bottom: 20px;"></div>
""", unsafe_allow_html=True)


# Redundant log section hidden/removed per user request

st.write("") # Padding for bottom visibility

# Cyclic updates if running
if st.session_state.is_running:
    if 'cycle' in st.session_state and st.session_state.cycle:
        cycle = st.session_state.cycle
        report = cycle.get('report', {})
        order = cycle.get('order', {})
        
        st.session_state.confidence = report.get('confidence', st.session_state.confidence)
        
        # Mock updating the dashboard data 
        st.session_state.price += 15.50
        agents = report.get('num_agents', int(st.session_state.agent_counts[-1] * 1.05))
        
        # Shift data
        now_str = datetime.now().strftime("%b %Y").upper()
        if now_str not in st.session_state.timestamps:
            st.session_state.timestamps.append(now_str)
            st.session_state.timestamps.pop(0)
            
        st.session_state.agent_counts.append(agents)
        st.session_state.agent_counts.pop(0)
        
        # Append order log
        if order:
            st.session_state.order_log.append({
                'Time': datetime.now().strftime("%H:%M:%S"),
                'Symbol': st.session_state.symbol,
                'Side': report.get('market_direction', 'yes').upper(),
                'Confidence': f"{st.session_state.confidence}%",
                'Status': order.get('status', 'filled').upper()
            })
            st.session_state.order_log = st.session_state.order_log[-10:]
            
        st.session_state.cycle = None
    
    time.sleep(30)
    st.session_state.cycle = asyncio.run(run_sniper_cycle(st.session_state.symbol))
    st.rerun()
