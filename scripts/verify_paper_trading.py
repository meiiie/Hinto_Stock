import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import datetime
from src.infrastructure.persistence.sqlite_order_repository import SQLiteOrderRepository
from src.application.services.paper_trading_service import PaperTradingService
from src.domain.entities.trading_signal import TradingSignal, SignalType

def verify():
    print("Starting Paper Trading Verification...")
    
    # 1. Setup
    repo = SQLiteOrderRepository()
    service = PaperTradingService(repo)
    
    # Clear existing orders for clean test (optional, or just ignore)
    # For safety, let's just print current count
    initial_count = len(repo.get_active_orders())
    print(f"Initial active orders: {initial_count}")
    
    # 2. Create Signal
    signal = TradingSignal(
        signal_type=SignalType.BUY,
        confidence=0.9,
        timestamp=datetime.now(),
        price=50000.0,
        entry_price=50000.0,
        stop_loss=49000.0,
        tp_levels={'tp1': 51000.0, 'tp2': 52000.0},
        reasons=["Test Signal"]
    )
    
    print(f"\nSending Signal: BUY @ 50000 (SL: 49000, TP: 51000)")
    service.on_signal_received(signal, "BTCUSDT")
    
    # 3. Verify Pending
    active_orders = repo.get_active_orders()
    if len(active_orders) > initial_count:
        print("Order Created Successfully")
        order = active_orders[-1]
        print(f"   ID: {order.id}")
        print(f"   Status: {order.status}")
    else:
        print("Order Creation Failed")
        return

    # 4. Match Entry (Price drops to 49990 to fill Buy Limit at 50000)
    print("\nMarket moves to 49990 (Low)")
    service.process_market_data(current_price=49995, high=50050, low=49990)
    
    order = repo.get_order(order.id)
    if order.status == 'FILLED':
        print("Order Filled Successfully")
    else:
        print(f"Order Fill Failed (Status: {order.status})")
        return

    # 5. Match TP (Price rises to 51005)
    print("\nMarket moves to 51005 (High)")
    service.process_market_data(current_price=51000, high=51005, low=50500)
    
    order = repo.get_order(order.id)
    if order.status == 'CLOSED':
        print("Order Closed Successfully")
        print(f"   Exit Reason: {order.exit_reason}")
        print(f"   PnL: ${order.pnl:.2f}")
        
        if order.pnl > 0:
             print("PnL is Positive")
        else:
             print("PnL is Incorrect")
    else:
        print(f"Order Close Failed (Status: {order.status})")
        return

    # 6. Check Balance
    balance = repo.get_account_balance()
    print(f"\nFinal Account Balance: ${balance:.2f}")
    print("Verification Complete!")

if __name__ == "__main__":
    verify()
