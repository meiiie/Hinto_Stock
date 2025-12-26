# Indicator Library

## Available Indicators in System

### Trend Indicators

| Indicator | Implementation | Parameters | Usage |
|-----------|----------------|------------|-------|
| **VWAP** | `vwap_calculator.py` | Reset: Daily | Trend direction, support/resistance |
| **EMA (7, 25, 50)** | `talib_calculator.py` | Periods: 7, 25, 50 | Trend strength, crossovers |
| **ADX** | `adx_calculator.py` | Period: 14, Threshold: 25 | Trend strength filter |

### Volatility Indicators

| Indicator | Implementation | Parameters | Usage |
|-----------|----------------|------------|-------|
| **Bollinger Bands** | `bollinger_calculator.py` | Period: 20, Std: 2 | Volatility bands, mean reversion |
| **ATR** | `atr_calculator.py` | Period: 14 | Stop loss, position sizing |

### Momentum Indicators

| Indicator | Implementation | Parameters | Usage |
|-----------|----------------|------------|-------|
| **RSI** | `talib_calculator.py` | Period: 6 | Overbought/oversold |
| **StochRSI** | `stoch_rsi_calculator.py` | RSI: 14, Stoch: 14, K: 3, D: 3 | Entry trigger |

### Volume Indicators

| Indicator | Implementation | Parameters | Usage |
|-----------|----------------|------------|-------|
| **Volume Spike** | `volume_spike_detector.py` | MA: 20, Threshold: 1.5x | Confirmation |
| **Volume SMA** | `talib_calculator.py` | Period: 20 | Baseline volume |

---

## Indicator Formulas

### VWAP (Volume Weighted Average Price)
```
VWAP = Sum(Typical Price × Volume) / Sum(Volume)
Typical Price = (High + Low + Close) / 3
```
**Resets:** Daily at 00:00 UTC

### Bollinger Bands
```
Middle Band = SMA(Close, 20)
Upper Band = Middle + (2 × StdDev(Close, 20))
Lower Band = Middle - (2 × StdDev(Close, 20))
```

### StochRSI
```
RSI = 100 - (100 / (1 + RS))
RS = Average Gain / Average Loss

StochRSI = (RSI - Lowest(RSI, 14)) / (Highest(RSI, 14) - Lowest(RSI, 14)) × 100
K = SMA(StochRSI, 3)
D = SMA(K, 3)
```

### ADX (Average Directional Index)
```
+DI = (Smoothed +DM / ATR) × 100
-DI = (Smoothed -DM / ATR) × 100
DX = |+DI - -DI| / (+DI + -DI) × 100
ADX = SMA(DX, 14)
```
**Interpretation:**
- ADX > 25: Strong trend
- ADX < 20: Weak/no trend
- ADX rising: Trend strengthening

### ATR (Average True Range)
```
True Range = max(High - Low, |High - Prev Close|, |Low - Prev Close|)
ATR = SMA(True Range, 14)
```

---

## Indicator Signal Interpretation

### Entry Signals
| Condition | Indicator | Signal |
|-----------|-----------|--------|
| Price > VWAP | VWAP | Bullish bias |
| Price at Lower BB | Bollinger | Pullback zone |
| StochRSI K crosses D | StochRSI | Entry trigger |
| Volume > 1.5x MA | Volume | Confirmation |
| ADX > 20 | ADX | Trend valid |

### Exit Signals
| Condition | Indicator | Action |
|-----------|-----------|--------|
| Price hits Stop | ATR-based | Exit loss |
| Price hits TP1/TP2/TP3 | R:R levels | Partial/full exit |
| StochRSI oversold | StochRSI | Consider exit |
