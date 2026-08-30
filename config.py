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

UNIVERSE = ["SPY", "QQQ", "IWM", "NVDA", "AAPL", "MSFT", "TSLA", "AMD"]

STARTING_CAPITAL = 100000.0

# Equity Risk Parameters
MAX_LOSS_PCT_PER_TRADE = 0.005  # Willing to lose 0.5% of total portfolio on a single trade
MAX_TOTAL_PORTFOLIO_RISK_PCT = 0.05
