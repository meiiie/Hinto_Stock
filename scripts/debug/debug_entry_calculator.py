"""Debug entry price calculator"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.domain.entities.candle import Candle
from src.infrastructure.indicators.swing_point_detector import SwingPointDetector
from src.application.services.entry_price_calculator import EntryPriceCalculator
import logging

logging.basicConfig(level=logging.DEBUG)

# Create test candles
base_time = datetime.now()
candles = []
prices = [
    105, 104, 103, 102, 101,  # Declining
    100,  # Swing low (index 5)
    101, 102, 103, 104, 105,  # Rising
    106  # Extra candle
]

for i, price in enumerate(prices):
    candle = Candle(
        timestamp=base_time + timedelta(minutes=i),
        open=price,
        high=price + 1.0,
        low=price - 1.0,
        close=price,
        volume=1000.0
    )
    candles.append(candle)

print("Candles:")
for i, c in enumerate(candles):
    print(f"  {i}: high={c.high:.1f}, low={c.low:.1f}, close={c.close:.1f}")

detector = SwingPointDetector(lookback=5)

print(f"\nLooking for swing low...")
swing_low = detector.find_recent_swing_low(candles)

if swing_low:
    print(f"✅ Found swing low: ${swing_low.price:.2f} at index {swing_low.index}")
else:
    print(f"❌ No swing low found")

print(f"\nLooking for swing high...")
swing_high = detector.find_recent_swing_high(candles)

if swing_high:
    print(f"✅ Found swing high: ${swing_high.price:.2f} at index {swing_high.index}")
else:
    print(f"❌ No swing high found")


print("\n" + "="*60)
print("Testing Entry Price Calculator")
print("="*60)

calculator = EntryPriceCalculator(
    offset_pct=0.001,
    max_ema_distance_pct=0.005,
    swing_lookback=5
)

ema7 = 99.5
print(f"\nEMA(7): ${ema7:.2f}")

result = calculator.calculate_entry_price(
    direction='BUY',
    candles=candles,
    ema7=ema7
)

if result:
    print(f"\n✅ Entry Price Result:")
    print(f"   Entry Price: ${result.entry_price:.2f}")
    print(f"   Swing Price: ${result.swing_price:.2f}")
    print(f"   EMA(7) Distance: {result.ema7_distance_pct:.3%}")
    print(f"   Is Valid: {result.is_valid}")
else:
    print(f"\n❌ No entry calculated")
