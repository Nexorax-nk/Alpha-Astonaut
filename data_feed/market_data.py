"""
data_feed/market_data.py
Fetches historical and real-time market data from Alpaca.
"""
from datetime import datetime, timedelta
import pandas as pd
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
from alpaca.data.enums import DataFeed
from config import APCA_API_KEY_ID, APCA_API_SECRET_KEY, UNIVERSE

class MarketDataClient:
    def __init__(self):
        self.client = StockHistoricalDataClient(APCA_API_KEY_ID, APCA_API_SECRET_KEY)

    def get_bars(self, symbols: list, timeframe_mins: int, days_back: int = 5) -> dict:
        """
        Fetches historical bars for a list of symbols.
        Returns a dict mapping symbol to a pandas DataFrame.
        """
        end_dt = datetime.now()
        start_dt = end_dt - timedelta(days=days_back)
        
        request_params = StockBarsRequest(
            symbol_or_symbols=symbols,
            timeframe=TimeFrame(amount=timeframe_mins, unit=TimeFrameUnit.Minute),
            start=start_dt,
            end=end_dt,
            feed=DataFeed.IEX
        )
        
        try:
            bars = self.client.get_stock_bars(request_params)
            # Convert to DataFrames
            result = {}
            for symbol in symbols:
                if symbol in bars.data:
                    df = pd.DataFrame([bar.model_dump() for bar in bars.data[symbol]])
                    df['timestamp'] = pd.to_datetime(df['timestamp'])
                    df.set_index('timestamp', inplace=True)
                    result[symbol] = df
            return result
        except Exception as e:
            print(f"Error fetching data: {e}")
            return {}

if __name__ == "__main__":
    mdc = MarketDataClient()
    bars = mdc.get_bars(["SPY"], 5, days_back=1)
    if "SPY" in bars:
        print(bars["SPY"].tail())
