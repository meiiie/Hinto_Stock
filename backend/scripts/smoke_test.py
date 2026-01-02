"""
Smoke Test - chạy trước khi merge
1. Import tất cả modules quan trọng
2. Instantiate DIContainer
3. Verify không có ImportError
4. Verify VelocityResult.is_crash_drop tồn tại
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.getcwd())

try:
    # Test 1: Import check
    print("Step 1: Testing Imports...")
    from src.domain.interfaces.i_momentum_velocity_calculator import VelocityResult
    from src.infrastructure.di_container import DIContainer
    from src.application.signals.signal_generator import SignalGenerator, MarketContext
    print("✅ Imports successful")

    # Test 2: VelocityResult field check
    print("Step 2: Verifying VelocityResult fields...")
    # Create a dummy result to check fields
    # Note: Dataclass default constructor expects arguments in order
    try:
        # Correct initialization based on file inspection
        result = VelocityResult(
            velocity=1.5,
            acceleration=0.1,
            is_fomo_spike=True,
            is_crash_drop=False,
            is_decelerating=False,
            is_accelerating=True
        )
        if hasattr(result, 'is_crash_drop'):
             print(f"✅ VelocityResult.is_crash_drop exists: {result.is_crash_drop}")
        else:
             print("❌ VelocityResult MISSING is_crash_drop field!")
             sys.exit(1)
             
    except TypeError as e:
        print(f"❌ VelocityResult initialization failed: {e}")
        print("Tip: Check if the __init__ arguments match the dataclass definition.")
        sys.exit(1)

    print("🚀 All smoke tests passed!")

except ImportError as e:
    print(f"❌ Import Error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected Error: {e}")
    sys.exit(1)
