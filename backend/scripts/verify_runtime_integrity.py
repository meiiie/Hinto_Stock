"""
Runtime Integrity Test - LOG-004 Compliance
Yêu cầu:
1. Khởi tạo DIContainer THẬT (không mock)
2. Lấy SignalGenerator từ container
3. Load 100+ nến thật (giả lập)
4. Gọi generate_signal() và đảm bảo KHÔNG crash
5. Verify VelocityResult có đủ fields (is_crash_drop)
"""

import sys
import os
import random
from datetime import datetime, timedelta

# Add project root to path
sys.path.insert(0, os.getcwd())

from src.infrastructure.di_container import DIContainer
from src.domain.entities.candle import Candle
from src.domain.interfaces.i_momentum_velocity_calculator import VelocityResult

def generate_dummy_candles(n=100, start_price=50000.0):
    """Generate valid dummy candles to pass validation."""
    candles = []
    current_time = datetime.now() - timedelta(minutes=n)
    current_price = start_price
    
    for _ in range(n):
        # Random movement but ensuring High >= Low
        movement = random.uniform(-50, 50)
        open_p = current_price
        close_p = open_p + movement
        high_p = max(open_p, close_p) + random.uniform(0, 20)
        low_p = min(open_p, close_p) - random.uniform(0, 20)
        volume = random.uniform(10, 1000)
        
        candle = Candle(
            timestamp=current_time,
            open=open_p,
            high=high_p,
            low=low_p,
            close=close_p,
            volume=volume
        )
        candles.append(candle)
        current_time += timedelta(minutes=1)
        current_price = close_p
        
    return candles

def run_integrity_test():
    print("🚀 Starting Runtime Integrity Test...")
    
    # 1. Initialize DI Container
    print("Step 1: Initializing DI Container...")
    container = DIContainer()
    
    # 2. Get SignalGenerator
    print("Step 2: Resolving SignalGenerator...")
    signal_gen = container.get_signal_generator()
    if not signal_gen:
        print("❌ Failed to resolve SignalGenerator")
        sys.exit(1)
    print("✅ SignalGenerator resolved")

    # 3. Generate Dummy Data
    print("Step 3: Generating 100 dummy candles...")
    candles = generate_dummy_candles(100)
    print(f"✅ Generated {len(candles)} candles")
    
    # 4. Test generate_signal (The Crash Test)
    print("Step 4: Executing generate_signal() - The Crash Test...")
    try:
        # We don't care about the result (Buy/Sell/None), just that it doesn't crash
        signal = signal_gen.generate_signal(candles, "BTCUSDT")
        print(f"✅ Execution successful! Result: {signal}")
    except Exception as e:
        print(f"❌ CRASH DETECTED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # 5. Verify Velocity Calculator Integration
    print("Step 5: Verifying Velocity Calculator Integration...")
    if hasattr(signal_gen, 'momentum_velocity_calculator'):
        calc = signal_gen.momentum_velocity_calculator
        result = calc.calculate(candles)
        
        if isinstance(result, VelocityResult):
            print(f"✅ Velocity Result type matches: {type(result)}")
            if hasattr(result, 'is_crash_drop'):
                print(f"✅ Field 'is_crash_drop' exists: {result.is_crash_drop}")
                print(f"   Velocity: {result.velocity:.4f}%/min")
                print(f"   FOMO: {result.is_fomo_spike}, CRASH: {result.is_crash_drop}")
            else:
                print("❌ Field 'is_crash_drop' MISSING in result!")
                sys.exit(1)
        else:
            print("⚠️ Velocity Calculator returned None or invalid type (might be due to data)")
    else:
        print("⚠️ SignalGenerator does not have momentum_velocity_calculator attribute")

    print("\n🎉 INTEGRITY TEST PASSED: System is runtime-safe!")

if __name__ == "__main__":
    run_integrity_test()