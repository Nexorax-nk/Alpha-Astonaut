"""
engine/risk_manager.py
Position sizing for pure Equities based on Account Equity and Stop Loss.
"""
from alpaca.trading.client import TradingClient
from config import APCA_API_KEY_ID, APCA_API_SECRET_KEY, STARTING_CAPITAL
from config import MAX_LOSS_PCT_PER_TRADE

class RiskManager:
    def __init__(self):
        self.client = TradingClient(APCA_API_KEY_ID, APCA_API_SECRET_KEY, paper=True)

    def calculate_position_size(self, current_price: float, stop_loss_pct: float) -> int:
        """
        Calculates position size using a Fractional Kelly Criterion limit.
        Base Edge: Win Rate = 55.6%, Reward/Risk = 1.0
        Kelly % = W - ((1 - W) / R) = 0.556 - 0.444 = 11.2%
        Half-Kelly Limit = 5.6% 
        """
        if current_price <= 0 or stop_loss_pct <= 0:
            return 0
            
        try:
            account = self.client.get_account()
            equity = float(account.portfolio_value)
            buying_power = float(account.buying_power)
        except Exception:
            equity = STARTING_CAPITAL
            buying_power = STARTING_CAPITAL
            
        # Hard cap risk at 2.0% of portfolio per trade (Aggressive compounding but under Half-Kelly)
        max_dollar_risk = equity * min(0.02, MAX_LOSS_PCT_PER_TRADE * 4) 
        dollar_risk_per_share = current_price * stop_loss_pct
        
        shares_to_buy = int(max_dollar_risk // dollar_risk_per_share)
        
        # Ensure we don't exceed buying power
        if (shares_to_buy * current_price) > buying_power:
            shares_to_buy = int(buying_power // current_price)
            
        print(f"  [KELLY CRITERION] Sizing for ${max_dollar_risk:.2f} total risk ({max_dollar_risk/equity:.1%} of account).")
        return shares_to_buy

    def check_portfolio_limits(self, new_trade_cost: float) -> bool:
        try:
            account = self.client.get_account()
            equity = float(account.portfolio_value)
            positions = self.client.get_all_positions()
            
            total_invested = sum([abs(float(p.market_value)) for p in positions])
            
            # Hackathon Max P&L Mode: Allow up to 98% of buying power to be deployed
            return (total_invested + new_trade_cost) <= (equity * 0.98)
        except Exception:
            return True
