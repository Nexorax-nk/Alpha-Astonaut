"""
execution/order_router.py
Submits Alpaca Equity Orders.
"""
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from config import APCA_API_KEY_ID, APCA_API_SECRET_KEY

class OrderRouter:
    def __init__(self):
        self.client = TradingClient(APCA_API_KEY_ID, APCA_API_SECRET_KEY, paper=True)

    def submit_trade(self, symbol: str, direction: str, quantity: int, price: float) -> dict:
        if quantity <= 0:
            return {"status": "REJECTED", "reason": "Zero quantity"}

        print(f"\n>>> EXECUTING PURE EQUITY TRADE <<<")
        print(f"[{symbol}] {direction}")
        print(f"Qty: {quantity} shares @ ~${price:.2f}")
        print(f"Total Value: ${quantity * price:.2f}\n")
        
        side = OrderSide.BUY if direction == "BULLISH" else OrderSide.SELL
        
        try:
            req = MarketOrderRequest(
                symbol=symbol,
                qty=quantity,
                side=side,
                time_in_force=TimeInForce.DAY
            )
            order = self.client.submit_order(req)
            return {"status": "FILLED_MOCK", "order_id": str(order.id)}
        except Exception as e:
            print(f"[!] Order execution failed: {e}")
            return {"status": "FAILED", "reason": str(e)}
