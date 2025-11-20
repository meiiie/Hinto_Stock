"""Debug signal alerts"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.domain.entities.candle import Candle
from src.application.signals.signal_generator import SignalGenerator

# Create oversold scenario
candles = []
timestamp = datetime.now() - timedelta(minutes=50)

for i in range(50):
    close_price = 50000 - (i * 150)
    
    if i == 49:
        volume = 300.0
    else:
        volume = 100.0
    
    candle = Candle(
        timestamp=timestamp + timedelta(minutes=i),
        open=close_price + 50,
        high=close_price + 100,
        low=close_price - 100,
        close=close_price,
        volume=volume
    )
    candles.append(candle)

# Generate signal
signal_gen = SignalGenerator()

# Debug: Check RSI analysis directly
rsi_analysis = signal_gen.rsi_monitor.analyze(candles)
print("RSI Analysis:")
print(f"  RSI: {rsi_analysis['rsi']:.2f}")
print(f"  Zone: {rsi_analysis['zone'].value}")
print(f"  Alerts: {len(rsi_analysis['alerts'])} alert(s)")
for alert in rsi_analysis['alerts']:
    print(f"    - {alert.message}")
    print(f"      Severity: {alert.severity}")

# Debug: Print all keys in rsi_analysis
print(f"\nRSI Analysis Keys: {list(rsi_analysis.keys())}")
print(f"Zone type: {type(rsi_analysis['zone'])}")
print(f"Zone value: {rsi_analysis['zone'].value}")
print(f"Alerts type: {type(rsi_analysis['alerts'])}")
print(f"Alerts length: {len(rsi_analysis['alerts'])}")

# Generate signal
signal = signal_gen.generate_signal(candles)

if signal:
    print(f"\nSignal Indicators:")
    print(f"  RSI: {signal.indicators.get('rsi', 0):.2f}")
    print(f"  RSI Zone: {signal.indicators.get('rsi_zone', 'unknown')}")
    print(f"  RSI Alerts: {signal.indicators.get('rsi_alerts', [])}")
    print(f"  All indicator keys: {list(signal.indicators.keys())}")
