# Strategy Guidelines

## Current Strategy: Trend Pullback

### Overview
A momentum-based strategy that enters on pullbacks within established trends.

### Entry Conditions (4 of 5 required in strict mode)

| # | Condition | Indicator | Threshold |
|---|-----------|-----------|-----------|
| 1 | **Trend** | Price > VWAP | Bullish bias |
| 2 | **Setup** | Near Lower BB or VWAP | Pullback zone |
| 3 | **Trigger** | StochRSI Cross Up | K crosses above D, K < 80 |
| 4 | **Candle** | Green candle | Close > Open |
| 5 | **Volume** | Volume Spike | Ratio > 1.5x MA |

### Exit Rules
- **Stop Loss:** ATR-based (3x ATR from entry)
- **Take Profit:** 3 levels (1.5R, 2.5R, 3.5R)
- **Trailing:** Move to breakeven at 0.8% profit, trail at 1.2%

### Filters Applied
| Filter | Threshold | Purpose |
|--------|-----------|---------|
| ADX | > 20 | Reject choppy markets |
| R:R Ratio | ≥ 0.8 | Minimum risk/reward |
| Volume Climax | < 4.0x | Reject extreme volume |
| Spread | < 0.10% | Reject illiquid conditions |

---

## Strategy Development Roadmap

### Layer 1: Core Signals ✅
- VWAP trend detection
- Bollinger Bands pullback zones
- StochRSI entry triggers
- ATR-based stop loss

### Layer 2: Candle Pattern Confirmation 🔜
- Engulfing patterns
- Pin bars
- Inside bars
- Doji reversals

### Layer 3: Multi-Timeframe Analysis 📋
- HTF trend alignment (1h, 4h)
- LTF entry precision (5m, 15m)
- Confluence scoring

---

## Strategy Change Log

| Date | Change | Rationale | Impact |
|------|--------|-----------|--------|
| 2025-12-20 | Reduced ADX threshold to 20 | More signal opportunities | +30% signals |
| 2025-12-22 | Fixed R:R check in enrichment | Prevent invalid signals | Quality ↑ |
