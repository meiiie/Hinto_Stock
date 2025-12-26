# 📊 TRADING REQUIREMENTS - Hinto Stock

**Document Version:** 1.0
**Last Updated:** 2025-12-22
**Domain:** Cryptocurrency Futures Trading (Short-term)

---

## 1. BUSINESS CONTEXT

### Market
- **Asset Class:** Cryptocurrency (primarily BTC, ETH)
- **Trading Type:** Futures/Perpetual contracts
- **Exchange:** Binance Futures (primary)
- **Timeframe:** Short-term (minutes to hours)
- **Leverage:** Up to 20x

### Strategy Overview
**Trend Pullback Strategy:**
- Trade WITH the trend, not against it
- Enter on pullbacks to key levels
- Use technical indicators for entry/exit timing

---

## 2. TRADING STRATEGY SPECIFICATIONS

### 2.1 Trend Identification
```markdown
## VWAP Rule
- Price > VWAP → Uptrend → Only LONG
- Price < VWAP → Downtrend → Only SHORT
- Price = VWAP → Neutral → No trade
```

### 2.2 Entry Conditions

#### LONG Entry
| Condition | Indicator | Threshold |
|-----------|-----------|-----------|
| Trend | Price vs VWAP | Price > VWAP |
| Pullback Zone | Bollinger Band | Touch Lower BB or VWAP |
| Momentum Shift | StochRSI | Cross above 20 |
| Volume Confirm | Volume Ratio | Volume > Previous Red Candle |

#### SHORT Entry
| Condition | Indicator | Threshold |
|-----------|-----------|-----------|
| Trend | Price vs VWAP | Price < VWAP |
| Rally Zone | Bollinger Band | Touch Upper BB or VWAP |
| Momentum Shift | StochRSI | Cross below 80 |
| Volume Confirm | Volume Ratio | Volume > Previous Green Candle |

### 2.3 Smart Entry Algorithm
```python
# No market orders - use limit for better fills
def calculate_limit_entry(candle, direction):
    body_size = abs(candle.close - candle.open)
    pullback_ratio = 0.3  # 30% of body
    
    if direction == 'LONG':
        entry = candle.close - (body_size * pullback_ratio)
    else:  # SHORT
        entry = candle.close + (body_size * pullback_ratio)
    
    return entry
```

### 2.4 Exit Strategy

#### Stop Loss Rules
| Method | Calculation | Notes |
|--------|-------------|-------|
| Swing Low/High | Previous swing point | Preferred method |
| ATR-based | Entry ± (ATR × 1.5) | Fallback |
| Percentage | Entry ± 2% | Maximum allowed |

#### Take Profit Rules
| Level | Calculation | Action |
|-------|-------------|--------|
| TP1 | Risk × 1.0 | Close 50% |
| TP2 | Risk × 1.5 | Close 30% + Trail |
| TP3 | Risk × 2.0 | Close remaining |

---

## 3. INDICATOR SPECIFICATIONS

### 3.1 VWAP (Volume Weighted Average Price)
```python
# Reset at market open (00:00 UTC for crypto)
vwap = cumsum(typical_price * volume) / cumsum(volume)
# where typical_price = (high + low + close) / 3
```

### 3.2 Bollinger Bands
```python
# Standard settings
period = 20
std_dev = 2.0

middle_band = SMA(close, period)
upper_band = middle_band + (std_dev * STDDEV(close, period))
lower_band = middle_band - (std_dev * STDDEV(close, period))
```

### 3.3 Stochastic RSI
```python
# Settings
rsi_period = 14
stoch_period = 14
k_period = 3
d_period = 3

rsi = RSI(close, rsi_period)
stoch_rsi_k = SMA(STOCH(rsi, stoch_period), k_period) * 100
stoch_rsi_d = SMA(stoch_rsi_k, d_period)
```

---

## 4. RISK MANAGEMENT RULES

### Position Sizing
```python
def calculate_position_size(account_balance, risk_percent, entry, stop_loss):
    risk_amount = account_balance * risk_percent  # e.g., 1% = 0.01
    risk_per_unit = abs(entry - stop_loss)
    position_size = risk_amount / risk_per_unit
    return position_size
```

### Risk Limits
| Parameter | Value | Enforcement |
|-----------|-------|-------------|
| Risk per trade | 1% of balance | Hard limit |
| Daily loss limit | 5% of balance | Auto-pause trading |
| Max drawdown | 15% of starting | Alert + review |
| Max leverage | 20x | System cap |

### Game Theory Enhancements
```markdown
## Stop Loss Jitter
- Add random noise to SL placement
- Avoid obvious levels (round numbers, recent lows)
- Range: ±0.1% of calculated SL

## Adaptive Exit
- Strong trend (ADX > 30): Trail loosely, aim for TP2/TP3
- Weak trend (ADX < 25): Take quick profit at TP1
```

---

## 5. SIGNAL QUALITY REQUIREMENTS

### Signal Scoring
| Factor | Weight | Scoring |
|--------|--------|---------|
| Trend alignment | 30% | 0-100 |
| Pullback quality | 20% | 0-100 |
| Momentum strength | 20% | 0-100 |
| Volume confirmation | 15% | 0-100 |
| Pattern match (L2) | 15% | 0-100 |

### Minimum Thresholds
```python
MIN_SIGNAL_SCORE = 60  # Below this, no trade
HIGH_QUALITY_SCORE = 80  # Full position size
LOW_QUALITY_SCORE = 60  # 50% position size
```

---

## 6. DATA REQUIREMENTS

### Real-time Data
| Data Type | Update Frequency | Latency Requirement |
|-----------|------------------|---------------------|
| Price tick | Per trade | < 100ms |
| Order book | 100ms | < 200ms |
| Candle | Per close | < 500ms |

### Historical Data
| Interval | History Required | Retention |
|----------|------------------|-----------|
| 1m | 7 days | Rolling |
| 5m | 30 days | Rolling |
| 15m | 90 days | Rolling |
| 1H | 1 year | Archive |

### Indicator Warm-up
| Indicator | Minimum Candles |
|-----------|-----------------|
| VWAP | 1 (reset daily) |
| Bollinger Bands | 20 |
| StochRSI | 28 (14+14) |
| ADX | 28 |

---

## 7. TRADING SYMBOLS

### Primary Pairs
| Symbol | Base | Quote | Priority |
|--------|------|-------|----------|
| BTCUSDT | BTC | USDT | 🔴 Primary |
| ETHUSDT | ETH | USDT | 🟡 Secondary |

### Symbol Properties
```python
SYMBOL_CONFIG = {
    'BTCUSDT': {
        'tick_size': 0.1,
        'lot_size': 0.001,
        'min_notional': 10,  # USDT
        'max_leverage': 125,
    },
    'ETHUSDT': {
        'tick_size': 0.01,
        'lot_size': 0.001,
        'min_notional': 10,
        'max_leverage': 100,
    }
}
```

---

## 8. OPERATIONAL HOURS

### Trading Sessions
| Session | UTC Time | Characteristics |
|---------|----------|-----------------|
| Asia | 00:00-08:00 | Lower volatility |
| Europe | 08:00-16:00 | Moderate activity |
| US | 13:00-22:00 | High volatility |
| Overlap | 13:00-16:00 | Peak volume |

### Best Trading Windows
```markdown
✅ Recommended:
- US Open (13:00-15:00 UTC)
- London Open (08:00-10:00 UTC)

⚠️ Caution:
- Weekend (low liquidity)
- Major news events
- Exchange maintenance
```

---

## 9. ALERT REQUIREMENTS

### Must-have Alerts
| Alert Type | Condition | Priority |
|------------|-----------|----------|
| Signal Generated | New valid signal | 🔴 High |
| Order Filled | Trade executed | 🔴 High |
| Stop Loss Hit | Position closed at loss | 🔴 High |
| Take Profit Hit | Position closed at profit | 🟢 Normal |
| Risk Limit | Daily loss exceeded | 🔴 Critical |
| Connection Lost | Exchange disconnect | 🔴 Critical |

---

## 10. VERSION HISTORY

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-12-22 | Initial trading requirements |

---

**IMPORTANT:** This document defines the trading domain for all agents. Any deviation requires approval from the trading strategy owner.
