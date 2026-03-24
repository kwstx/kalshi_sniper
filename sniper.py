import os
import requests
import streamlit as st
from dotenv import load_dotenv
import plotly.graph_objects as go
import ccxt
from datetime import datetime

# Load environment variables
load_dotenv()

# Configuration
ENGRAM_URL = os.getenv("ENGRAM_BASE_URL")
KALSHI_BASE = os.getenv("KALSHI_BASE_URL")
DEMO_MODE = os.getenv("DEMO_MODE") == "true"

# The code automatically uses demo environment for safe testing 
# and switches to live only when the user changes the flag and fills a real token.
if DEMO_MODE:
    st.info("Running in DEMO mode")
else:
    st.warning("Running in LIVE mode")
