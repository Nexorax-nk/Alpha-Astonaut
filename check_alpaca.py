from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetOrdersRequest
from alpaca.trading.enums import QueryOrderStatus
from config import APCA_API_KEY_ID, APCA_API_SECRET_KEY

def check_account():
    client = TradingClient(APCA_API_KEY_ID, APCA_API_SECRET_KEY, paper=True)
    
    print("=== ALPACA ACCOUNT METRICS ===")
    acct = client.get_account()
    print(f"Status: {acct.status}")
    print(f"Equity: ${acct.equity}")
    print(f"Buying Power: ${acct.buying_power}")
    print(f"Daytrade Count: {acct.daytrade_count}")
    
    print("\n=== RECENT ORDERS (Last 10) ===")
    try:
        req = GetOrdersRequest(status=QueryOrderStatus.ALL, limit=10)
        orders = client.get_orders(req)
        if not orders:
            print("No recent orders found.")
        else:
            for o in orders:
                filled = f"@ ${o.filled_avg_price}" if o.filled_avg_price else ""
                print(f"[{o.status.name}] {o.symbol} {o.side.name} {o.qty} {filled} (Submitted: {o.submitted_at})")
    except Exception as e:
        print(f"Could not fetch orders: {e}")

    print("\n=== ACTIVE POSITIONS ===")
    try:
        positions = client.get_all_positions()
        if not positions:
            print("No active positions.")
        else:
            for p in positions:
                print(f"{p.symbol}: {p.qty} shares | Entry: ${p.avg_entry_price} | Current: ${p.current_price} | PNL: ${p.unrealized_pl} ({float(p.unrealized_plpc)*100:.2f}%)")
    except Exception as e:
        print(f"Could not fetch positions: {e}")

if __name__ == "__main__":
    check_account()
