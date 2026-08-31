"""
engine/quant_signal_v3.py
Momentum Scalper + Trend Follower Hybrid (Hackathon Optimized)

Entry logic uses a 2-of-3 condition system:
  1. Trend:    Price > 21-EMA (uptrend confirmation)
  2. Momentum: RSI between 40-70 (room to run, not overbought)
  3. Volume:   RVOL > 0.5 (institutional interest present)

Direction is always BULLISH (long-only) for simplicity and
because the US market has a structural upward bias.
"""
import pandas as pd
import pandas_ta as ta
import numpy as np

class QuantSignalEngineV3:
    def __init__(self, params=None):
        self.params = params or {
            "ema_fast": 9,
            "ema_slow": 21,
            "rsi_low": 40,
            "rsi_high": 70,
            "rvol_thresh": 0.5
        }

    def add_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        if len(df) < 50:
            return df
            
        df = df.copy()
        
        # Ensure timezone
        if df.index.tzinfo is None:
            df.index = df.index.tz_localize('UTC').tz_convert('America/New_York')
        else:
            df.index = df.index.tz_convert('America/New_York')
            
        # Core Indicators
        df['RSI'] = ta.rsi(df['close'], length=14)
        df['EMA_Fast'] = ta.ema(df['close'], length=self.params['ema_fast'])
        df['EMA_Slow'] = ta.ema(df['close'], length=self.params['ema_slow'])
        
        # Relative Volume
        df['vol_sma'] = df['volume'].rolling(window=20).mean()
        df['RVOL'] = df['volume'] / df['vol_sma']
        
        # VWAP Proxy
        df['date'] = df.index.date
        df['typical_price'] = (df['high'] + df['low'] + df['close']) / 3
        df['VWAP'] = (df['typical_price'] * df['volume']).groupby(df['date']).cumsum() / df['volume'].groupby(df['date']).cumsum()
        df.drop(columns=['date', 'typical_price'], inplace=True, errors='ignore')
        
        return df

    def calculate_score(self, historical_slice: pd.DataFrame) -> dict:
        """
        2-of-3 entry system. Returns BULLISH if at least 2 conditions are met.
        """
        required_cols = ['RSI', 'EMA_Fast', 'EMA_Slow', 'RVOL']
        if len(historical_slice) < 5:
            return {"direction": "NEUTRAL", "is_valid": False, "score": 0, "conditions": []}
        
        # Check all required columns exist and have valid data
        for col in required_cols:
            if col not in historical_slice.columns:
                return {"direction": "NEUTRAL", "is_valid": False, "score": 0, "conditions": []}
            
        curr = historical_slice.iloc[-1]
        
        # Skip if any indicator is NaN
        if any(pd.isna(curr.get(col)) for col in required_cols):
            return {"direction": "NEUTRAL", "is_valid": False, "score": 0, "conditions": []}
        
        conditions_met = []
        score = 0
        
        # Condition 1: TREND — Price above 21-EMA
        if curr['close'] > curr['EMA_Slow']:
            conditions_met.append("TREND")
            score += 33
            
        # Condition 2: MOMENTUM — RSI between 40-70 (has room to run)
        if self.params['rsi_low'] <= curr['RSI'] <= self.params['rsi_high']:
            conditions_met.append("MOMENTUM")
            score += 34
            
        # Condition 3: VOLUME — Relative volume > threshold
        if curr['RVOL'] > self.params['rvol_thresh']:
            conditions_met.append("VOLUME")
            score += 33
            
        # Need at least 2 of 3
        is_valid = len(conditions_met) >= 2
        
        return {
            "direction": "BULLISH" if is_valid else "NEUTRAL",
            "is_valid": is_valid,
            "score": score,
            "conditions": conditions_met
        }
