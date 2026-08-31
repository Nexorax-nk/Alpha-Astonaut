"""
main_loop.py
Autonomous continuous execution agent (Hackathon — Momentum Scalper).

Architecture:
  Flask web server (main thread) — serves dashboard API + keeps Render alive
  Trading agent (background thread) — scans every 60s during market hours

Market Hours Guard:
  - Only trades 9:35 AM – 3:50 PM ET (skip first 5min for opening volatility)
  - Forces EOD liquidation at 3:50 PM ET
  - Sleeps 5 minutes outside market hours

Catalyst is a BOOSTER, not a BLOCKER:
  - If Groq says BULLISH + high strength → 50% position size boost
  - If Groq says BEARISH → skip the trade
  - If Groq fails or says NEUTRAL → trade anyway on technicals
"""
import time
import os
import csv
import threading
from datetime import datetime
import pytz
from flask import Flask, jsonify
from flask_cors import CORS
from config import (
    UNIVERSE, SCAN_INTERVAL_MARKET_OPEN, SCAN_INTERVAL_MARKET_CLOSED,
    STOP_LOSS_PCT
)
from data_feed.market_data import MarketDataClient
from data_feed.news_feed import NewsFeedClient
from engine.quant_signal_v3 import QuantSignalEngineV3
from engine.catalyst_groq import CatalystEngine
from engine.equity_pricer import EquityPricer
from engine.risk_manager import RiskManager
from execution.order_router import OrderRouter
from execution.position_monitor import PositionMonitor

ET = pytz.timezone('America/New_York')

def setup_ledger():
    log_file = "logs/trade_ledger.csv"
    os.makedirs("logs", exist_ok=True)
    if not os.path.isfile(log_file):
        with open(log_file, "w", newline="") as csvfile:
            fieldnames = ["timestamp", "ticker", "direction", "catalyst", "decision", "reason", "price", "qty"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
    return log_file

def log_decision(log_file, symbol, direction, cat_valid, decision, reason, price=0, qty=0):
    with open(log_file, "a", newline="") as csvfile:
        fieldnames = ["timestamp", "ticker", "direction", "catalyst", "decision", "reason", "price", "qty"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writerow({
            "timestamp": datetime.now().isoformat(),
            "ticker": symbol,
            "direction": direction,
            "catalyst": str(cat_valid),
            "decision": decision,
            "reason": reason,
            "price": price,
            "qty": qty
        })

def is_market_open() -> bool:
    """Check if US equity market is currently in trading hours."""
    now = datetime.now(ET)
    # Weekdays only
    if now.weekday() >= 5:
        return False
    # Market hours: 9:30 AM - 4:00 PM ET
    market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
    market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)
    return market_open <= now <= market_close

def is_trading_window() -> bool:
    """
    Narrower than market open:
    - Skip first 5 minutes (opening volatility)
    - Stop entering new trades at 3:50 PM (leave time for EOD exits)
    """
    now = datetime.now(ET)
    if now.weekday() >= 5:
        return False
    trade_start = now.replace(hour=9, minute=35, second=0, microsecond=0)
    trade_end = now.replace(hour=15, minute=50, second=0, microsecond=0)
    return trade_start <= now <= trade_end

def run_agent():
    print("=" * 50)
    print("ALPHA ASTRONAUT — MOMENTUM SCALPER v2.0")
    print("=" * 50)
    
    mdc = MarketDataClient()
    nfc = NewsFeedClient()
    qse = QuantSignalEngineV3()
    ce = CatalystEngine()
    ep = EquityPricer()
    rm = RiskManager()
    router = OrderRouter()
    pm = PositionMonitor()
    ledger = setup_ledger()
    
    scan_count = 0
    
    while True:
        now = datetime.now(ET)
        scan_count += 1
        
        # --- MARKET HOURS GUARD ---
        if not is_market_open():
            if scan_count % 12 == 1:  # Print every ~1 hour when closed
                print(f"\n[{now.strftime('%H:%M:%S ET')}] Market CLOSED. Waiting...")
            time.sleep(SCAN_INTERVAL_MARKET_CLOSED)
            continue
        
        print(f"\n{'='*60}")
        print(f"--- SCAN #{scan_count}: {now.strftime('%Y-%m-%d %H:%M:%S ET')} ---")
        print(f"{'='*60}")
        
        # 1. POSITION MONITOR — Check exits on every cycle
        pm.check_exits([])
        
        # If we're past the trading window (3:50 PM), don't open new positions
        if not is_trading_window():
            print("[WINDOW] Outside trading window. Monitoring only.")
            time.sleep(SCAN_INTERVAL_MARKET_OPEN)
            continue
        
        # 2. CHECK CAPACITY — Can we open new positions?
        if not rm.can_open_new_position():
            print("[FULL] At max positions. Monitoring exits only.")
            time.sleep(SCAN_INTERVAL_MARKET_OPEN)
            continue
        
        # 3. GET CURRENTLY HELD SYMBOLS — Duplicate protection
        held_symbols = rm.get_open_position_symbols()
        if held_symbols:
            print(f"Currently holding: {', '.join(held_symbols)}")
        
        # 4. FETCH MARKET DATA
        print(f"Fetching 5m bars for {len(UNIVERSE)} symbols...")
        try:
            bars = mdc.get_bars(UNIVERSE, timeframe_mins=5, days_back=2)
        except Exception as e:
            print(f"[!] Market data fetch failed: {e}")
            time.sleep(SCAN_INTERVAL_MARKET_OPEN)
            continue
        
        best_setup = None  # Track the highest-scoring signal this cycle
        
        for symbol, df in bars.items():
            # Skip if we already hold this stock
            if symbol in held_symbols:
                print(f"  {symbol}: SKIP (already holding)")
                continue
                
            print(f"  {symbol}: ", end="")
            
            # 5. QUANT SIGNAL
            try:
                df_eval = qse.add_indicators(df)
                signal = qse.calculate_score(df_eval)
            except Exception as e:
                print(f"ERROR ({e})")
                continue
            
            if not signal["is_valid"]:
                print(f"NO SETUP (score={signal['score']}, conditions={signal.get('conditions', [])})")
                continue
            
            print(f"SIGNAL! score={signal['score']}, conditions={signal['conditions']}")
            
            # Keep the best setup from this scan
            if best_setup is None or signal['score'] > best_setup['score']:
                best_setup = {
                    "symbol": symbol,
                    "signal": signal,
                    "df_eval": df_eval,
                    "score": signal['score']
                }
        
        # 6. EXECUTE THE BEST SETUP (one trade per scan cycle for discipline)
        if best_setup is None:
            print("\nNo valid setups found this cycle.")
            time.sleep(SCAN_INTERVAL_MARKET_OPEN)
            continue
            
        symbol = best_setup["symbol"]
        direction = best_setup["signal"]["direction"]
        df_eval = best_setup["df_eval"]
        
        print(f"\n>> BEST SETUP: {symbol} ({direction}, score={best_setup['score']})")
        
        # 7. CATALYST CHECK (booster, not blocker)
        catalyst_boost = 1.0
        try:
            news = nfc.get_latest_news(symbol)
            cat = ce.analyze_news(symbol, news)
            
            cat_direction = cat.get("direction", "NEUTRAL")
            cat_strength = cat.get("catalystStrength", 0)
            
            if cat_direction == "BEARISH":
                print(f"  CATALYST BEARISH — Skipping trade for safety.")
                log_decision(ledger, symbol, direction, False, "REJECTED", "Bearish catalyst")
                time.sleep(SCAN_INTERVAL_MARKET_OPEN)
                continue
            
            if cat_direction == "BULLISH" and cat_strength > 70:
                catalyst_boost = 1.5
                print(f"  CATALYST BOOST! Strength={cat_strength}, sizing +50%")
            else:
                print(f"  Catalyst neutral/weak (strength={cat_strength}). Trading on technicals.")
        except Exception as e:
            print(f"  Catalyst check failed ({e}). Trading on technicals only.")
        
        # 8. LIVE PRICING
        quote = ep.get_live_price(symbol)
        if not quote["is_valid"]:
            price = df_eval['close'].iloc[-1]
            print(f"  [!] Live quote unavailable, using last close: ${price:.2f}")
        else:
            price = quote["price"]
            print(f"  Live price: ${price:.2f}")
        
        # 9. POSITION SIZING
        qty = rm.calculate_position_size(price, STOP_LOSS_PCT)
        
        # Apply catalyst boost
        if catalyst_boost > 1.0:
            boosted_qty = int(qty * catalyst_boost)
            print(f"  [BOOST] {qty} → {boosted_qty} shares (catalyst boost)")
            qty = boosted_qty
        
        if qty <= 0:
            print("  REJECTED: Risk engine assigned 0 shares.")
            log_decision(ledger, symbol, direction, True, "REJECTED", "Risk limit reached")
            time.sleep(SCAN_INTERVAL_MARKET_OPEN)
            continue
            
        if not rm.check_portfolio_limits(qty * price):
            print("  REJECTED: Portfolio exposure limit reached.")
            log_decision(ledger, symbol, direction, True, "REJECTED", "Portfolio exposure")
            time.sleep(SCAN_INTERVAL_MARKET_OPEN)
            continue
        
        # 10. EXECUTE TRADE
        print(f"\n{'*'*40}")
        print(f"  EXECUTING: BUY {qty} x {symbol} @ ~${price:.2f}")
        print(f"{'*'*40}")
        
        res = router.submit_trade(symbol, direction, qty, price)
        log_decision(ledger, symbol, direction, True, "EXECUTED", res["status"], price, qty)
        
        print(f"\nScan complete. Next scan in {SCAN_INTERVAL_MARKET_OPEN}s...")
        time.sleep(SCAN_INTERVAL_MARKET_OPEN)


# ============================================================
# FLASK WEB SERVER (main thread) — Dashboard API + Render keepalive
# ============================================================
app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "Alpha Astronaut is running!"

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetPortfolioHistoryRequest, GetOrdersRequest
from alpaca.trading.enums import QueryOrderStatus
from config import APCA_API_KEY_ID, APCA_API_SECRET_KEY

@app.route('/api/performance')
def get_performance():
    try:
        client = TradingClient(APCA_API_KEY_ID, APCA_API_SECRET_KEY, paper=True)
        req = GetPortfolioHistoryRequest(period="1W", timeframe="1H")
        history = client.get_portfolio_history(req)
        
        data = []
        for i in range(len(history.timestamp)):
            ts = datetime.fromtimestamp(history.timestamp[i])
            equity = history.equity[i]
            if equity is not None:
                data.append({"time": ts.strftime("%m-%d %H:00"), "pnl": round(equity, 2)})
        return jsonify(data)
    except Exception as e:
        return jsonify([])

@app.route('/api/trades')
def get_trades():
    trades = []
    try:
        with open("logs/trade_ledger.csv", "r") as f:
            reader = csv.DictReader(f)
            trades = list(reader)
        trades.reverse()
    except Exception:
        pass
    return jsonify(trades)

@app.route('/api/stats')
def get_stats():
    """Pull REAL stats from Alpaca account."""
    try:
        client = TradingClient(APCA_API_KEY_ID, APCA_API_SECRET_KEY, paper=True)
        account = client.get_account()
        positions = client.get_all_positions()
        
        # Count orders
        req = GetOrdersRequest(status=QueryOrderStatus.ALL, limit=100)
        orders = client.get_orders(req)
        filled_orders = [o for o in orders if str(o.status) == "OrderStatus.FILLED"]
        
        equity = float(account.equity)
        pnl = equity - 100000.0
        
        return jsonify({
            "total_trades": len(filled_orders),
            "status": "Active",
            "equity": equity,
            "pnl": round(pnl, 2),
            "pnl_pct": round((pnl / 100000.0) * 100, 2),
            "buying_power": float(account.buying_power),
            "open_positions": len(positions),
        })
    except Exception as e:
        return jsonify({"total_trades": 0, "status": "Error", "error": str(e)})

@app.route('/api/positions')
def get_positions():
    """Pull REAL live positions from Alpaca."""
    try:
        client = TradingClient(APCA_API_KEY_ID, APCA_API_SECRET_KEY, paper=True)
        positions = client.get_all_positions()
        result = []
        for p in positions:
            result.append({
                "symbol": p.symbol,
                "qty": float(p.qty),
                "entry": float(p.avg_entry_price),
                "current": float(p.current_price),
                "pnl": float(p.unrealized_pl),
                "roi": round(float(p.unrealized_plpc) * 100, 2),
                "market_value": float(p.market_value),
                "side": str(p.side)
            })
        return jsonify(result)
    except Exception as e:
        return jsonify([])

@app.route('/api/orders')
def get_orders():
    """Pull REAL recent orders from Alpaca."""
    try:
        client = TradingClient(APCA_API_KEY_ID, APCA_API_SECRET_KEY, paper=True)
        req = GetOrdersRequest(status=QueryOrderStatus.ALL, limit=20)
        orders = client.get_orders(req)
        result = []
        for o in orders:
            result.append({
                "symbol": o.symbol,
                "side": str(o.side),
                "qty": str(o.qty),
                "status": str(o.status),
                "filled_price": str(o.filled_avg_price) if o.filled_avg_price else None,
                "submitted_at": str(o.submitted_at),
                "filled_at": str(o.filled_at) if o.filled_at else None,
            })
        return jsonify(result)
    except Exception as e:
        return jsonify([])

# Keep mock endpoints for dashboard screens that use them
from api_mocks import MOCK_SCANNER, MOCK_BACKTESTS, MOCK_ACTIVITY_INITIAL, get_random_log

@app.route('/api/scanner')
def get_scanner():
    return jsonify(MOCK_SCANNER)

@app.route('/api/live_positions')
def get_live_positions():
    """Now returns REAL positions instead of mocks."""
    return get_positions()

@app.route('/api/trade_history')
def get_trade_history():
    return get_trades()

@app.route('/api/backtests')
def get_backtests():
    return jsonify(MOCK_BACKTESTS)

@app.route('/api/activity_log')
def get_activity_log():
    return jsonify(MOCK_ACTIVITY_INITIAL)

@app.route('/api/activity_log_stream')
def get_activity_stream():
    return jsonify(get_random_log())

def start_bot_thread():
    bot_thread = threading.Thread(target=run_agent)
    bot_thread.daemon = True
    bot_thread.start()

if __name__ == "__main__":
    start_bot_thread()
    # Bind to Render's dynamic port
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
