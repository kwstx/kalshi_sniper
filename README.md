# Kalshi Sniper

A prediction market trading tool with MiroFish and Engram integration.

## Getting Started

Follow these steps to set up and run the project:

### 1. Configure Environment Variables

The project uses environment variables for configuration. A `.env.example` file is provided in the root directory.

1.  Copy `.env.example` to `.env`.
2.  Open `.env` and fill in your own keys:
    *   `KALSHI_TOKEN`: Your Kalshi demo or live token.
    *   `X_BEARER_TOKEN`: Your Twitter (X) bearer token.
    *   `MIROFISH_BASE_URL`: The URL for the MiroFish service (default: `http://localhost:5001`).
    *   `ENGRAM_BASE_URL`: The URL for the Engram translator (default: `http://localhost:8000`).
    *   `DEMO_MODE`: Set to `true` for demo with mock funds, or `false` for live trading.
    *   `KALSHI_BASE_URL`: Set to `https://demo-api.kalshi.com/trade-api/v2` for demo, or `https://trading-api.kalshi.com/v2` for real small-money trades.

### 2. Install Dependencies

Ensure you have your virtual environment activated and run:
```bash
pip install -r requirements.txt
```

### 3. Run the Sniper
```bash
streamlit run sniper.py
```

