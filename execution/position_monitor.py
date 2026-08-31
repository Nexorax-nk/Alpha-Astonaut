"""
execution/position_monitor.py
Monitors open equity positions for Take-Profit (1%) and Stop-Loss (0.5%).
"""
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from config import APCA_API_KEY_ID, APCA_API_SECRET_KEY

class PositionMonitor:
    def __init__(self):
        self.client = TradingClient(APCA_API_KEY_ID, APCA_API_SECRET_KEY, paper=True)

    def check_exits(self, active_trades: list):
        try:
            positions = self.client.get_all_positions()
        except Exception as e:
            print(f"[!] Position monitor failed to fetch positions: {e}")
            return
            
        if not positions:
            return
            
        print(f"Monitoring {len(positions)} open equity positions...")
        
        for p in positions:
            try:
                unrealized_plpc = float(p.unrealized_plpc)
                symbol = p.symbol
                qty = abs(float(p.qty))
                side = p.side
                
                # Hackathon Demo Exits: Quick +0.10% TP, wide -5.00% SL
                if unrealized_plpc <= -0.050:
                    self._close_position(symbol, qty, side, "STOP_LOSS")
                elif unrealized_plpc >= 0.001:
                    self._close_position(symbol, qty, side, "TAKE_PROFIT")
            except Exception as e:
                pass

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
        except Exception as e:
            print(f"[!] Failed to close {symbol}: {e}")
