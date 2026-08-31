"""
engine/risk_manager.py
Position sizing and portfolio risk management for the hackathon agent.

Key rules:
- Max 4 concurrent positions
- Max 25% of equity in any single position
- Risk 1.5% of portfolio per trade
- Provides helper to detect duplicate positions
"""
from alpaca.trading.client import TradingClient
from config import (
    APCA_API_KEY_ID, APCA_API_SECRET_KEY, STARTING_CAPITAL,
    MAX_LOSS_PCT_PER_TRADE, MAX_CONCURRENT_POSITIONS, MAX_SINGLE_POSITION_PCT
)

class RiskManager:
    def __init__(self):
        self.client = TradingClient(APCA_API_KEY_ID, APCA_API_SECRET_KEY, paper=True)

    def get_account_state(self):
        """Fetch account equity and buying power once per cycle to reduce API calls."""
        try:
            account = self.client.get_account()
            return {
                "equity": float(account.portfolio_value),
                "buying_power": float(account.buying_power),
                "cash": float(account.cash)
            }
        except Exception:
            return {
                "equity": STARTING_CAPITAL,
                "buying_power": STARTING_CAPITAL,
                "cash": STARTING_CAPITAL
            }

    def get_open_position_symbols(self) -> set:
        """Returns the set of symbols we currently hold. Used for duplicate detection."""
        try:
            positions = self.client.get_all_positions()
            return {p.symbol for p in positions}
        except Exception:
            return set()

    def get_position_count(self) -> int:
        """Returns the number of currently held positions."""
        try:
            positions = self.client.get_all_positions()
            return len(positions)
        except Exception:
            return 0

    def calculate_position_size(self, current_price: float, stop_loss_pct: float) -> int:
        """
        Calculate position size based on risk-per-trade and account equity.
        Ensures no single position exceeds MAX_SINGLE_POSITION_PCT of equity.
        """
        if current_price <= 0 or stop_loss_pct <= 0:
            return 0
            
        acct = self.get_account_state()
        equity = acct["equity"]
        buying_power = acct["buying_power"]
        
        # Dollar risk per trade
        max_dollar_risk = equity * MAX_LOSS_PCT_PER_TRADE
        dollar_risk_per_share = current_price * stop_loss_pct
        
        shares_from_risk = int(max_dollar_risk // dollar_risk_per_share)
        
        # Cap by max single position size (25% of equity)
        max_position_value = equity * MAX_SINGLE_POSITION_PCT
        shares_from_position_cap = int(max_position_value // current_price)
        
        # Cap by buying power
        shares_from_buying_power = int(buying_power // current_price)
        
        shares = min(shares_from_risk, shares_from_position_cap, shares_from_buying_power)
        
        # Must be at least 1 share
        if shares <= 0:
            return 0
            
        trade_value = shares * current_price
        print(f"  [RISK] {shares} shares @ ${current_price:.2f} = ${trade_value:.2f} "
              f"({trade_value/equity:.1%} of equity, risking ${shares * dollar_risk_per_share:.2f})")
        return shares

    def can_open_new_position(self) -> bool:
        """Check if we're under the max concurrent positions limit."""
        count = self.get_position_count()
        if count >= MAX_CONCURRENT_POSITIONS:
            print(f"  [RISK] At max positions ({count}/{MAX_CONCURRENT_POSITIONS}). Skipping.")
            return False
        return True

    def check_portfolio_limits(self, new_trade_cost: float) -> bool:
        """Ensure total invested doesn't exceed portfolio limits."""
        try:
            acct = self.get_account_state()
            equity = acct["equity"]
            positions = self.client.get_all_positions()
            
            total_invested = sum([abs(float(p.market_value)) for p in positions])
            
            # Allow up to 95% of equity to be deployed
            return (total_invested + new_trade_cost) <= (equity * 0.95)
        except Exception:
            return True
