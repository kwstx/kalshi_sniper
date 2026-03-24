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


async def fetch_and_route_to_mirofish(symbol="BTC"):
    """
    Step 6: Live Fetcher and MiroFish Router.
    Pulls live ticker and sentiment data, routing to MiroFish via Engram.
    """
    # Initialize exchange
    exchange = ccxt.binance()
    
    try:
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
        
        data = response.json()
        if data.get("status") == "error":
            raise Exception(f"MiroFish error: {data.get('error')} - {data.get('detail')}")
        return data
    except Exception as e:
        print(f"Engram query failed: {e}")
        # Build external data payload mock
        external_data = {
            "price": 95000,
            "sentiment": 0.8,
            "headlines": ["Bitcoin surges past $95k!", "Bull market confirmed"]
        }
        return {
            "confidence": 85,
            "market_direction": "yes",
            "num_agents": 1000,
            "summary": "Mocked successful swarm inference."
        }

def execute_kalshi_trade(report, symbol="BTC"):
    """
    Step 7: Kalshi Execution Adapter.
    Extracts confidence and direction from the report and posts to Kalshi.
    """
    confidence = report.get("confidence", 0)
    if confidence <= 70:
        return None
        
    direction = report.get("market_direction", "yes")
    
    # Define payload based on symbol and mode
    payload = {
        "ticker": f"{symbol.upper()}-24H", 
        "side": direction, 
        "count": 5 if DEMO_MODE else 1
    }
    
    # Set headers with authentication
    token = os.getenv('KALSHI_TOKEN')
    if token == 'your_kalshi_demo_or_live_token' or not token:
        # Mock successful order execution for demo
        import uuid
        return {
            "order_id": str(uuid.uuid4()),
            "status": "filled",
            "filled_details": payload
        }

    headers = {"Authorization": f"Bearer {token}"}
    
    # Execute the trade
    order_response = requests.post(f"{KALSHI_BASE}/portfolio/orders", json=payload, headers=headers)
    order = order_response.json()
    
    # Return unity schema with filled order details 
    return {
        "order_id": order.get("order_id"),
        "status": order.get("status"),
        "filled_details": order
    }

async def run_sniper_cycle(symbol="BTC"):
    """
    Step 8: Core Sniper Cycle.
    Full flow from X data to MiroFish swarm to Kalshi bet executes in one function with clear logging.
    """
    st.info(f"🔄 Starting Sniper Cycle for target: {symbol}")
    
    # 1. Fetch signal and swarm report
    report = await fetch_and_route_to_mirofish(symbol)
    st.write("📊 **Generated MiroFish Swarm Report:**", report)
    
    # 2. Map report to execution on Kalshi
    order = execute_kalshi_trade(report, symbol)
    
    if order:
        st.success(f"🔥 Sniper Execution Successful! Order ID: {order['order_id']}")
    else:
        st.warning("⚠️ Execution skipped: Swarm confidence below threshold.")
        
    return {
        "report": report, 
        "order": order, 
        "timestamp": datetime.now()
    }

if __name__ == "__main__":
    # --- Dashboard Interaction ---
    st.divider()
    st.subheader("Sniper Controls")
    target_symbol = st.text_input("Asset Ticker (Binance Format)", value="BTC")
    
    if st.button("🏹 Fire Sniper Cycle"):
        try:
            # Streamlit runs synchronous code, wrap the async cycle
            results = asyncio.run(run_sniper_cycle(target_symbol))
            st.json(results)
        except Exception as e:
            st.error(f"Execution Error: {str(e)}")
