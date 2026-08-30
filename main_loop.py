"""
main_loop.py
Autonomous continuous execution agent (Hackathon Optimized PURE EQUITY).
"""
import time
import os
import csv
import threading
from datetime import datetime
from flask import Flask
from config import UNIVERSE
from data_feed.market_data import MarketDataClient
from data_feed.news_feed import NewsFeedClient
from engine.quant_signal_v3 import QuantSignalEngineV3
from engine.catalyst_groq import CatalystEngine
from engine.equity_pricer import EquityPricer
from engine.risk_manager import RiskManager
from execution.order_router import OrderRouter
from execution.position_monitor import PositionMonitor

def setup_ledger():
    log_file = "logs/trade_ledger.csv"
    os.makedirs("logs", exist_ok=True)
    if not os.path.isfile(log_file):
        with open(log_file, "w", newline="") as csvfile:
            fieldnames = ["timestamp", "ticker", "direction", "catalyst", "decision", "reason"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
    return log_file

def log_decision(log_file, symbol, direction, cat_valid, decision, reason):
    with open(log_file, "a", newline="") as csvfile:
        fieldnames = ["timestamp", "ticker", "direction", "catalyst", "decision", "reason"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writerow({
            "timestamp": datetime.now().isoformat(),
            "ticker": symbol,
            "direction": direction,
            "catalyst": str(cat_valid),
            "decision": decision,
            "reason": reason
        })

def run_agent():
    print("========================================")
    print("ALPHA ASTRONAUT - PURE EQUITY EXECUTION AGENT")
    print("========================================")
    
    mdc = MarketDataClient()
    nfc = NewsFeedClient()
    qse = QuantSignalEngineV3()
    ce = CatalystEngine()
    ep = EquityPricer()
    rm = RiskManager()
    router = OrderRouter()
    pm = PositionMonitor()
    ledger = setup_ledger()
    
    STOP_LOSS_PCT = 0.005 # 0.50% stop loss for Absolute Peak RR
    
    while True:
        current_time = datetime.now()
        print(f"\n--- SCAN START: {current_time.strftime('%Y-%m-%d %H:%M:%S')} ---")
        
        # 1. Position Monitor
        pm.check_exits([])
        
        # 2. Market Data
        print(f"Fetching 5m bars for universe...")
        bars = mdc.get_bars(UNIVERSE, timeframe_mins=5, days_back=2)
        
        for symbol, df in bars.items():
            print(f"Evaluating {symbol}...", end=" ")
            
            # 3. Quant Setup
            df_eval = qse.add_indicators(df)
            signal = qse.calculate_score(df_eval)
            
            if not signal["is_valid"]:
                print("NO SETUP")
                continue
                
            direction = signal["direction"]
            print(f"QUANT {direction} DETECTED! Checking catalyst...")
            
            # 4. Catalyst Confirmation
            news = nfc.get_latest_news(symbol)
            cat = ce.analyze_news(symbol, news)
            
            if cat.get("direction", "NEUTRAL") != direction and cat.get("direction") != "NEUTRAL":
                print(f"  REJECTED: Catalyst contradicts ({cat.get('direction')})")
                log_decision(ledger, symbol, direction, False, "REJECTED", "Contradictory News")
                continue
            if not cat.get("catalystStrength", 0) > 50:
                print(f"  REJECTED: No credible fresh catalyst.")
                log_decision(ledger, symbol, direction, False, "REJECTED", "Weak Catalyst")
                continue
                
            print("  CATALYST CONFIRMED. Fetching live equity quote...")
            
            # 5. Live Pricing
            quote = ep.get_live_price(symbol)
            if not quote["is_valid"]:
                # If market is closed, use the last close from the dataframe as a fallback for testing
                price = df_eval['close'].iloc[-1]
                print(f"  [!] Live quote failed (Market Closed?), using last close: ${price:.2f}")
            else:
                price = quote["price"]
                
            # 6. Risk Engine
            qty = rm.calculate_position_size(price, STOP_LOSS_PCT)
            if qty <= 0:
                print("  REJECTED: Risk engine assigned 0 position size.")
                log_decision(ledger, symbol, direction, True, "REJECTED", "Risk limit reached")
                continue
                
            if not rm.check_portfolio_limits(qty * price):
                print("  REJECTED: Max portfolio exposure reached.")
                log_decision(ledger, symbol, direction, True, "REJECTED", "Portfolio Exposure")
                continue
                
            # 7. EXECUTE
            res = router.submit_trade(symbol, direction, qty, price)
            log_decision(ledger, symbol, direction, True, "EXECUTED", res["status"])
            
        print("\nScan complete. Sleeping for 5 minutes...")
        time.sleep(300)

# --- HACKATHON RENDER.COM FREE TIER TRICK ---
# Render puts free services to sleep if they don't bind to a web port.
# We spin up a fake web server and run the bot in a background thread.
app = Flask(__name__)

@app.route('/')
def keep_alive():
    return "Alpha Astronaut is RUNNING 24/7!"

def start_bot_thread():
    bot_thread = threading.Thread(target=run_agent)
    bot_thread.daemon = True
    bot_thread.start()

if __name__ == "__main__":
    start_bot_thread()
    # Bind to Render's dynamic port
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
