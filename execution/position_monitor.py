"""
execution/position_monitor.py
Monitors open equity positions with proper exit logic:
  - Take Profit:   +1.5% → close immediately
  - Stop Loss:     -0.8% → close immediately
  - Trailing Stop: At +1.0%, move stop to breakeven (+0.1%)
  - EOD Close:     Liquidate everything at 3:50 PM ET
"""
from datetime import datetime
import pytz
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from config import (
    APCA_API_KEY_ID, APCA_API_SECRET_KEY,
    TAKE_PROFIT_PCT, STOP_LOSS_PCT,
    TRAILING_STOP_ACTIVATION_PCT, TRAILING_STOP_PCT
)

ET = pytz.timezone('America/New_York')

class PositionMonitor:
    def __init__(self):
        self.client = TradingClient(APCA_API_KEY_ID, APCA_API_SECRET_KEY, paper=True)
        # Track trailing stops: symbol -> adjusted stop level (as a P&L percentage)
        self._trailing_stops = {}

    def check_exits(self, active_trades: list):
        try:
            positions = self.client.get_all_positions()
        except Exception as e:
            print(f"[!] Position monitor failed to fetch positions: {e}")
            return
            
        if not positions:
            self._trailing_stops.clear()
            return
            
        now_et = datetime.now(ET)
        is_eod = now_et.hour == 15 and now_et.minute >= 50
        
        print(f"Monitoring {len(positions)} open equity positions...")
        
        # Clean up trailing stops for symbols we no longer hold
        held_symbols = {p.symbol for p in positions}
        self._trailing_stops = {s: v for s, v in self._trailing_stops.items() if s in held_symbols}
        
        for p in positions:
            try:
                unrealized_plpc = float(p.unrealized_plpc)
                symbol = p.symbol
                qty = abs(float(p.qty))
                side = p.side
                
                # 1. EOD Liquidation — close everything at 3:50 PM ET
                if is_eod:
                    print(f"  [EOD] Closing {symbol} ({unrealized_plpc*100:+.2f}%) — end of day liquidation")
                    self._close_position(symbol, qty, side, "EOD_LIQUIDATION")
                    continue
                
                # 2. Hard Stop Loss
                if unrealized_plpc <= -STOP_LOSS_PCT:
                    print(f"  [SL] {symbol} hit stop loss at {unrealized_plpc*100:+.2f}%")
                    self._close_position(symbol, qty, side, "STOP_LOSS")
                    continue
                    
                # 3. Hard Take Profit
                if unrealized_plpc >= TAKE_PROFIT_PCT:
                    print(f"  [TP] {symbol} hit take profit at {unrealized_plpc*100:+.2f}%")
                    self._close_position(symbol, qty, side, "TAKE_PROFIT")
                    continue
                
                # 4. Trailing Stop Logic
                if unrealized_plpc >= TRAILING_STOP_ACTIVATION_PCT:
                    # Activate or update trailing stop
                    trail_level = unrealized_plpc - TRAILING_STOP_PCT
                    current_trail = self._trailing_stops.get(symbol, 0)
                    
                    if trail_level > current_trail:
                        self._trailing_stops[symbol] = trail_level
                        print(f"  [TRAIL] {symbol} trailing stop updated to {trail_level*100:+.2f}%")
                
                # Check if trailing stop is hit
                if symbol in self._trailing_stops:
                    if unrealized_plpc <= self._trailing_stops[symbol]:
                        print(f"  [TRAIL-EXIT] {symbol} trailing stop triggered at {unrealized_plpc*100:+.2f}%")
                        self._close_position(symbol, qty, side, "TRAILING_STOP")
                        continue
                        
            except Exception as e:
                print(f"  [!] Error monitoring {p.symbol}: {e}")

    def force_close_all(self):
        """Force close all positions. Used for EOD liquidation."""
        try:
            positions = self.client.get_all_positions()
            for p in positions:
                qty = abs(float(p.qty))
                self._close_position(p.symbol, qty, p.side, "FORCE_CLOSE")
            self._trailing_stops.clear()
        except Exception as e:
            print(f"[!] Force close all failed: {e}")

    def _close_position(self, symbol: str, qty: float, current_side: str, reason: str):
        print(f">>> CLOSING {symbol} ({qty} shares) due to {reason} <<<")
        
        close_side = OrderSide.SELL if current_side == "long" else OrderSide.BUY
        
        try:
            req = MarketOrderRequest(
                symbol=symbol,
                qty=qty,
                side=close_side,
                time_in_force=TimeInForce.DAY
            )
            self.client.submit_order(req)
            # Clean up trailing stop
            self._trailing_stops.pop(symbol, None)
        except Exception as e:
            print(f"[!] Failed to close {symbol}: {e}")
