"""
engine/equity_pricer.py
Simple live price fetcher for Equities to bypass options friction entirely.
"""
from alpaca.data.historical.stock import StockHistoricalDataClient
from alpaca.data.requests import StockLatestQuoteRequest
from config import APCA_API_KEY_ID, APCA_API_SECRET_KEY

class EquityPricer:
    def __init__(self):
        self.data_client = StockHistoricalDataClient(APCA_API_KEY_ID, APCA_API_SECRET_KEY)

    def get_live_price(self, symbol: str) -> dict:
        try:
            req = StockLatestQuoteRequest(symbol_or_symbols=[symbol])
            quotes = self.data_client.get_stock_latest_quote(req)
            quote = quotes.get(symbol)
            if not quote:
                return {"is_valid": False, "reason": "No live quote available."}
                
            price = quote.ask_price if quote.ask_price > 0 else quote.bid_price
            if price <= 0:
                return {"is_valid": False, "reason": "Live price is 0 (Market Closed)."}
                
            return {
                "symbol": symbol,
                "price": price,
                "is_valid": True
            }
        except Exception as e:
            return {"is_valid": False, "reason": f"Quote API Error: {e}"}
