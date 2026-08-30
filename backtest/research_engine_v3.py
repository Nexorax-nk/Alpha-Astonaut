"""
backtest/research_engine_v3.py
Test the Deep ITM Options strategy.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from data_feed.market_data import MarketDataClient
from engine.quant_signal_v3 import QuantSignalEngineV3
from backtest.options_simulator import OptionsSimulator

def test_v3_itm(slippage=0.02):
    print(f"Testing Deep ITM Options with {slippage*100:.1f}% options friction...")
    
    mdc = MarketDataClient()
    symbols = ["SPY", "QQQ", "IWM", "NVDA", "AAPL", "MSFT", "TSLA", "AMD"]
    data_dict = mdc.get_bars(symbols, timeframe_mins=15, days_back=60)
    
    qse = QuantSignalEngineV3()
    sim = OptionsSimulator(slippage_pct=slippage)
    
    wins = 0
    losses = 0
    total_pnl = 0.0
    
    for symbol, df in data_dict.items():
        if len(df) < 50:
            continue
            
        df_eval = qse.add_indicators(df.copy())
        df_eval['hist_vol'] = df_eval['close'].pct_change().rolling(20).std() * (252*26)**0.5
        
        in_position = False
        trade = None
        
        for i in range(50, len(df_eval)):
            current_time = df_eval.index[i]
            current_S = df_eval['close'].iloc[i]
            
            if in_position:
                days_elapsed = (current_time - trade["entry_time"]).total_seconds() / 86400.0
                current_value = sim.calculate_itm_exit_value(trade, current_S, days_elapsed)
                
                pct_pnl = (current_value - trade["debit_paid"]) / trade["debit_paid"]
                
                # Live agent uses +30% TP, -15% SL on the option itself
                exit_reason = None
                if pct_pnl >= 0.30: exit_reason = "TP"
                elif pct_pnl <= -0.15: exit_reason = "SL"
                elif current_time.tz_convert('America/New_York').hour == 15 and current_time.tz_convert('America/New_York').minute >= 45: exit_reason = "EOD"
                
                if exit_reason:
                    trade_pnl = pct_pnl # We track % return per trade to compare with equity
                    total_pnl += trade_pnl
                    if trade_pnl > 0: wins += 1
                    else: losses += 1
                    in_position = False
                continue
                
            historical_slice = df_eval.iloc[:i+1]
            signal = qse.calculate_score(historical_slice)
            
            if signal["is_valid"]:
                vol = df_eval['hist_vol'].iloc[i]
                if pd.isna(vol) or vol <= 0: vol = 0.25
                
                trade = sim.price_itm_option(current_S, signal["direction"], days_to_expiry=14, volatility=vol)
                if trade:
                    trade["entry_time"] = current_time
                    in_position = True

    total_trades = wins + losses
    win_rate = wins / total_trades if total_trades > 0 else 0
    expectancy = total_pnl / total_trades if total_trades > 0 else 0
    
    print(f"\n--- DEEP ITM OPTIONS RESULTS ---")
    print(f"Total Trades: {total_trades}")
    print(f"Win Rate: {win_rate:.1%}")
    print(f"Expectancy (Avg % Return/Trade): {expectancy*100:.2f}%")
    print(f"Total Cumulative Return: {total_pnl*100:.2f}%")

if __name__ == "__main__":
    test_v3_itm(slippage=0.02) # Realistic 2% slippage on liquid ITM options (SPY/QQQ)
    test_v3_itm(slippage=0.05) # Harsh 5% slippage
