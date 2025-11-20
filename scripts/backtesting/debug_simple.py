"""Quick test to see actual RSI values and why no signals."""
import sys
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.backtesting.data_loader import HistoricalDataLoader
from src.infrastructure.indicators.talib_calculator import TALibCalculator

# Load data
loader = HistoricalDataLoader()
end = datetime.now()
start = end - timedelta(days=7)

candles = loader.load_candles(
    symbol='BTCUSDT',
    timeframe='15m',
    start_date=start,
    end_date=end
)

print(f"Loaded {len(candles)} candles")

# Calculate RSI
df = pd.DataFrame({
    'open': [c.open for c in candles],
    'high': [c.high for c in candles],
    'low': [c.low for c in candles],
    'close': [c.close for c in candles],
    'volume': [c.volume for c in candles]
})

talib_calc = TALibCalculator()
indicators = talib_calc.calculate_all(df)

# Analyze RSI distribution
rsi_values = indicators['rsi_6'].dropna()
print(f"\n📊 RSI Statistics (last 7 days):")
print(f"  Min RSI: {rsi_values.min():.1f}")
print(f"  Max RSI: {rsi_values.max():.1f}")
print(f"  Mean RSI: {rsi_values.mean():.1f}")
print(f"  Median RSI: {rsi_values.median():.1f}")
print(f"\n  RSI < 30 count: {(rsi_values < 30).sum()} / {len(rsi_values)} ({(rsi_values < 30).sum()/len(rsi_values)*100:.1f}%)")
print(f"  RSI > 70 count: {(rsi_values > 70).sum()} / {len(rsi_values)} ({(rsi_values > 70).sum()/len(rsi_values)*100:.1f}%)")
print(f"  RSI < 40 count: {(rsi_values < 40).sum()} / {len(rsi_values)} ({(rsi_values < 40).sum()/len(rsi_values)*100:.1f}%)")
print(f"  RSI > 60 count: {(rsi_values > 60).sum()} / {len(rsi_values)} ({(rsi_values > 60).sum()/len(rsi_values)*100:.1f}%)")

print(f"\n💡 RECOMMENDATION:")
if (rsi_values < 30).sum() == 0 and (rsi_values > 70).sum() == 0:
    print("  ❌ NO RSI oversold/overbought in 7 days!")
    print("  → Need to RELAX conditions: Use RSI < 40 for BUY, RSI > 60 for SELL")
    print("  → Or remove RSI as REQUIRED condition")
else:
    print("  ✅ RSI extremes exist, check other conditions (volume, EMA)")
