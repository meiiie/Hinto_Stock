"""Debug RSI calculation"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.domain.entities.candle import Candle
from src.application.analysis.rsi_monitor import RSIMonitor

# Create strong uptrend
candles = []
timestamp = datetime.now() - timedelta(minutes=50)

for i in range(50):
    close_price = 50000 + (i * 150) + (i * i * 2)
    
    candle = Candle(
        timestamp=timestamp + timedelta(minutes=i),
        open=close_price - 50,
        high=close_price + 100,
        low=close_price - 100,
        close=close_price,
        volume=100.0
    )
    candles.append(candle)

# Analyze RSI
rsi_monitor = RSIMonitor(period=6)
rsi_analysis = rsi_monitor.analyze(candles)

print("RSI Analysis:")
print(f"  RSI: {rsi_analysis['rsi']:.2f}")
print(f"  Zone: {rsi_analysis['zone'].value}")
print(f"  is_overbought: {rsi_analysis['is_overbought']}")
print(f"  is_oversold: {rsi_analysis['is_oversold']}")
print(f"  is_neutral: {rsi_analysis['is_neutral']}")
