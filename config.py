"""
config.py
Global configuration, API credentials, and strict risk limits.
"""
import os
from dotenv import load_dotenv

load_dotenv()

APCA_API_KEY_ID = os.getenv("APCA_API_KEY_ID")
APCA_API_SECRET_KEY = os.getenv("APCA_API_SECRET_KEY")
APCA_API_BASE_URL = os.getenv("APCA_API_BASE_URL", "https://paper-api.alpaca.markets")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Expanded universe: Large-cap liquid tech + ETFs for maximum opportunity
UNIVERSE = [
    "SPY", "QQQ", "IWM",           # ETFs (always liquid)
    "NVDA", "AAPL", "MSFT", "TSLA", "AMD",  # Original picks
    "META", "GOOG", "AMZN", "NFLX"           # Added for more signals
]

STARTING_CAPITAL = 100000.0

# --- Risk Parameters ---
MAX_LOSS_PCT_PER_TRADE = 0.015     # Risk 1.5% of portfolio per trade
MAX_TOTAL_PORTFOLIO_RISK_PCT = 0.06  # Max 6% total portfolio risk across all positions
MAX_CONCURRENT_POSITIONS = 4        # No more than 4 stocks held at once
MAX_SINGLE_POSITION_PCT = 0.25      # No more than 25% of equity in one stock

# --- Exit Thresholds (Hyper-Scalping Mode) ---
TAKE_PROFIT_PCT = 0.004             # +0.4% take profit (rapid lock-in)
STOP_LOSS_PCT = 0.003               # -0.3% stop loss (tight risk)
TRAILING_STOP_ACTIVATION_PCT = 0.002  # Activate trailing stop at +0.2%
TRAILING_STOP_PCT = 0.001           # Trail by 0.1%

# --- Scan Timing ---
SCAN_INTERVAL_MARKET_OPEN = 60      # 60 seconds during market hours
SCAN_INTERVAL_MARKET_CLOSED = 300   # 5 minutes when market is closed
