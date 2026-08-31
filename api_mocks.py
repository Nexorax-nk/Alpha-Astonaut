import random
from datetime import datetime

MOCK_SCANNER = [
    {"symbol": "NVDA", "price": 128.45, "change": 2.1, "rvol": 3.2, "vwap": "+1.5%", "atr": "2.4", "signal": "CALL", "score": 93},
    {"symbol": "TSLA", "price": 198.22, "change": -2.5, "rvol": 2.8, "vwap": "-1.8%", "atr": "3.1", "signal": "PUT", "score": 88},
    {"symbol": "SPY", "price": 542.12, "change": 1.2, "rvol": 2.4, "vwap": "+0.8%", "atr": "1.2", "signal": "CALL", "score": 87},
    {"symbol": "QQQ", "price": 451.33, "change": 0.3, "rvol": 1.1, "vwap": "+0.2%", "atr": "0.9", "signal": "WAIT", "score": 51},
    {"symbol": "AAPL", "price": 215.11, "change": -0.4, "rvol": 0.9, "vwap": "-0.3%", "atr": "1.5", "signal": "WAIT", "score": 42},
]

MOCK_POSITIONS = [
    {
        "symbol": "NVDA", "strike": "182/187 CALL", 
        "entry": 2.14, "current": 2.83, 
        "pnl": 69.0, "roi": 32.2,
        "risk": 214, "maxProfit": 286,
        "timeHeld": "23m"
    },
    {
        "symbol": "SPY", "strike": "540/545 CALL", 
        "entry": 1.85, "current": 1.70, 
        "pnl": -15.0, "roi": -8.1,
        "risk": 185, "maxProfit": 315,
        "timeHeld": "45m"
    },
    {
        "symbol": "TSLA", "strike": "195/190 PUT", 
        "entry": 3.10, "current": 3.55, 
        "pnl": 45.0, "roi": 14.5,
        "risk": 310, "maxProfit": 190,
        "timeHeld": "12m"
    },
    {
        "symbol": "META", "strike": "480/485 CALL", 
        "entry": 4.20, "current": 5.15, 
        "pnl": 95.0, "roi": 22.6,
        "risk": 420, "maxProfit": 80,
        "timeHeld": "1h 5m"
    }
]

MOCK_HISTORY = [
    {"time": "10:32", "symbol": "SPY", "strategy": "Breakout", "entry": 1.20, "exit": 1.81, "pnl": 61, "roi": 50.8},
    {"time": "11:04", "symbol": "NVDA", "strategy": "Catalyst", "entry": 2.10, "exit": 1.71, "pnl": -39, "roi": -18.6},
    {"time": "13:15", "symbol": "TSLA", "strategy": "Reversal", "entry": 3.45, "exit": 4.10, "pnl": 65, "roi": 18.8},
    {"time": "14:22", "symbol": "AAPL", "strategy": "Breakout", "entry": 0.85, "exit": 1.35, "pnl": 50, "roi": 58.8},
]

MOCK_BACKTESTS = [
    {"name": "RSI/EMA Trend", "winRate": 26, "profitFactor": 0.71, "expectancy": -120, "return": -15.2, "selected": False},
    {"name": "ORB (Opening Range)", "winRate": 41, "profitFactor": 0.92, "expectancy": -58, "return": -4.1, "selected": False},
    {"name": "RVOL Breakout", "winRate": 47, "profitFactor": 1.08, "expectancy": 21, "return": 8.5, "selected": False},
    {"name": "Alpha Astronaut (Ensemble AI)", "winRate": 61.4, "profitFactor": 1.63, "expectancy": 74, "return": 34.2, "selected": True},
]

def get_random_log():
    events = [
        {"icon": "🔍", "action": "SCAN", "message": "16 symbols evaluated across NASDAQ and NYSE", "highlight": False},
        {"icon": "📈", "action": "SIGNAL", "message": "NVDA bullish breakout detected on 5m timeframe", "highlight": True},
        {"icon": "📰", "action": "CATALYST", "message": "Groq sentiment positive -> Strong catalyst alignment", "highlight": True},
        {"icon": "📊", "action": "OPTIONS", "message": "182/187 CALL spread selected based on expected move", "highlight": False},
        {"icon": "🛡️", "action": "RISK", "message": "Max loss: $214. Approved within 2% account limit.", "highlight": False},
        {"icon": "⚡", "action": "EXECUTION", "message": "Order submitted to Alpaca API", "highlight": False},
        {"icon": "✅", "action": "FILLED", "message": "4 contracts filled @ $2.14 average", "highlight": True},
        {"icon": "📈", "action": "MONITOR", "message": "Position +28%, trailing stop activated", "highlight": False},
        {"icon": "🔴", "action": "EXIT", "message": "Take-profit triggered. Closing position.", "highlight": False},
        {"icon": "💰", "action": "P&L", "message": "Trade closed for +$276 realized gain.", "highlight": True},
    ]
    event = random.choice(events).copy()
    event["time"] = datetime.now().strftime("%H:%M:%S")
    event["id"] = random.randint(1000, 99999)
    return event

MOCK_ACTIVITY_INITIAL = [get_random_log() for _ in range(3)]
