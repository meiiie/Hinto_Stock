
import sys
import asyncio
import os
from datetime import datetime

# Add project root to path
sys.path.append(os.getcwd())

from src.infrastructure.di_container import DIContainer
from src.domain.entities.trading_signal import TradingSignal, SignalType, SignalStatus

async def test_persistence():
    print("🚀 Starting Persistence Test...")
    
    # 1. Get Container & Service
    container = DIContainer()
    signal_service = container.get_signal_lifecycle_service()
    repo = signal_service.repo
    print(f"📂 Repository DB Path: {repo.db_path}")
    
    # 2. Create Dummy Signal
    test_id = f"TEST-{int(datetime.now().timestamp())}"
    signal = TradingSignal(
        id=test_id,
        symbol="BTCUSDT",
        signal_type=SignalType.BUY,
        status=SignalStatus.PENDING,
        confidence=0.95,
        price=50000.0,
        entry_price=50000.0,
        stop_loss=49000.0,
        tp_levels={'tp1': 51000.0},
        position_size=0.1,
        risk_reward_ratio=2.0,
        generated_at=datetime.now(),
        indicators={'rsi': 30},
        reasons=['Test Signal']
    )
    
    # 3. Call Register Signal
    print(f"💾 Saving Signal {test_id}...")
    saved_signal = signal_service.register_signal(signal)
    
    if saved_signal:
        print("✅ Signal registered successfully!")
    else:
        print("❌ Signal registration failed!")
        return

    # 4. Verify from Repository
    print("🔍 Verifying from DB...")
    # Note: Using private method or sql directly if public method doesn't exist for fetching by ID
    # But let's try getting history
    history = repo.get_history(limit=10)
    found = any(s.id == test_id for s in history)
    
    if found:
        print("✅ Signal FOUND in Database!")
    else:
        print("❌ Signal NOT FOUND in Database History!")
        print(f"History IDs: {[s.id for s in history]}")

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(test_persistence())
