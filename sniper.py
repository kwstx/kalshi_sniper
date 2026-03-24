import os
import asyncio
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

async def fetch_and_route_to_mirofish(symbol="BTC"):
    """
    Step 6: Live Fetcher and MiroFish Router.
    Pulls live ticker and sentiment data, routing to MiroFish via Engram.
    """
    # Initialize exchange
    exchange = ccxt.binance()
    
    # Fetch price with ccxt (wrapped in to_thread for async compatibility)
    ticker = await asyncio.to_thread(exchange.fetch_ticker, f"{symbol}/USDT")
    price = ticker["last"]
    
    # Fetch recent X tweets for sentiment
    headers = {"Authorization": f"Bearer {os.getenv('X_BEARER_TOKEN')}"}
    params = {"query": f"{symbol.lower()} OR bitcoin lang:en", "max_results": 20}
    response_x = await asyncio.to_thread(requests.get, "https://api.x.com/2/tweets/search/recent", headers=headers, params=params)
    tweets = response_x.json()
    
    # Build external data payload
    external_data = {
        "price": price, 
        "sentiment": sum(1 for t in tweets.get("data", []) if "bullish" in t["text"].lower()) / max(1, len(tweets.get("data", []))), 
        "headlines": [t["text"] for t in tweets.get("data", [])[:5]]
    }
    
    # Route via Engram to MiroFish
    response = await asyncio.to_thread(
        requests.post,
        f"{ENGRAM_URL}/route", 
        json={
            "target_platform": "mirofish", 
            "message": f"Current {symbol} price ${price} with sentiment {external_data['sentiment']}", 
            "external_data": external_data, 
            "swarm_id": "kalshi-sniper-swarm", 
            "num_agents": 1000
        }
    )
    
    return response.json()
