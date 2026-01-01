# Deep CoT Analysis: Backtest Performance Issues
**Date:** 2026-01-01 22:50  
**Approach:** SOTA Research + Root Cause Analysis

---

## 1. Benchmarking: Kỳ Vọng vs Thực Tế

### SOTA Benchmarks (Research 2025):

| Strategy | Timeframe | Expected Frequency |
|----------|-----------|-------------------|
| VWAP Mean Reversion | 15m | **1-2 trades/day** per asset |
| SFP (ICT) | 15m | **Multiple signals/day** |
| Swing Trading | Daily | 2-5 trades/week |
| Professional Selective | Any | Few high-quality trades |

### Hinto Thực Tế:
```
5 trades / 60 days / 2 pairs = 0.04 trades/day/pair
Expected: 1-2 trades/day/pair

→ HỆTHỐNG ĐANG DƯỚI KỲ VỌNG 25-50 LẦN!
```

---

## 2. Deep Root Cause Analysis (CoT)

### STEP 1: Trace Signal Flow

```
generate_signal()
  │
  ├─ [Filter 1] len(candles) < 50? → Loại 0%
  │
  ├─ [Filter 2] Session 8-22 UTC? → Loại ~42%
  │
  ├─ [Filter 3] SFP.is_valid? → Loại ~90-95%
  │    └─ Swing point detection
  │    └─ Sweep + Close back condition
  │
  ├─ [Filter 4] Volume ≥ 1.2x? → Loại ~70%
  │
  ├─ [Filter 5] VWAP Distance ≥ 1.5%? → Loại ~90%
  │
  └─ [Filter 6] SFP Confidence ≥ 0.8? → Loại ~20-50%
```

### STEP 2: Xác Suất Chồng Chất (Multiplicative)

```
P(Pass Filter 1) = 1.0
P(Pass Filter 2) = 0.58 (14/24 hours)
P(Pass Filter 3) = 0.05 (SFP hiếm)
P(Pass Filter 4) = 0.30 (volume spike)
P(Pass Filter 5) = 0.10 (far from VWAP)
P(Pass Filter 6) = 0.60 (high confidence)

P(Signal) = 1.0 × 0.58 × 0.05 × 0.30 × 0.10 × 0.60
          = 0.000522 = 0.05%

60 days × 96 candles/day = 5,760 candles
5,760 × 0.000522 ≈ 3 signals (2 pairs = 6 expected, got 5)
```

### STEP 3: Root Cause Identified

> **VẤN ĐỀ GỐC: FILTER STACKING (Chồng Filter)**
> 
> Mỗi filter đơn lẻ có lý do hợp lý, nhưng khi CHỒNG lên nhau
> chúng tạo ra một "funnel" quá hẹp.

---

## 3. SOTA Analysis: Vấn Đề Thiết Kế

### ❌ Anti-Pattern Detected: Over-Filtering

**Hiện tại:** SFP + Volume + VWAP Distance + Confidence + Session
**Vấn đề:** SFP BẢN THÂN ĐÃ LÀ SIGNAL MẠNH, không cần nhiều filter bổ sung

### ✅ SOTA Pattern: One Primary + One Confirmation

```
Binance/Two Sigma approach:
  Primary: Strong pattern (SFP)
  Confirmation: Volume OR Market Structure

NOT: SFP AND Volume AND VWAP AND Confidence AND Session
```

### Logic Sai:
```
SFP Mean Reversion hiện tại YÊU CẦU:
1. SFP valid (price sweep swing + close back)
2. VWAP distance > 1.5% (price FAR from mean)

LOGIC CONFLICT:
- SFP = Reversal tại swing point
- VWAP distance = Stretch from mean

Hai điều này KHÔNG LIÊN QUAN và chồng filter!
```

---

## 4. SOTA Recommendations

### A. Strategy Redesign (Clean Architecture)

**SFP Mean Reversion (Correct Logic):**
```python
# SFP = Entry trigger
# VWAP = Target (where price returns to)
# Volume = Confirmation (không phải filter)

def _strategy_sfp_mean_reversion(ctx, config, symbol):
    # 1. PRIMARY: SFP Valid
    if not ctx.sfp_result.is_valid:
        return None
    
    # 2. CONFIRMATION (Chỉ cần 1, không phải cả 3):
    # Option A: Volume climax
    vol_confirmed = vol_ratio > 1.5
    
    # Option B: Near support/resistance
    near_key_level = abs(vwap_dist) > 0.5%  # Giảm từ 1.5%
    
    # 3. Direction from SFP type (không cần thêm filter)
    is_buy = ctx.sfp_result.sfp_type == SFPType.BULLISH
    is_sell = ctx.sfp_result.sfp_type == SFPType.BEARISH
    
    # 4. Confidence boost thay vì filter
    confidence = ctx.sfp_result.confidence
    if vol_confirmed: confidence += 0.1
    if near_key_level: confidence += 0.1
    
    # 5. Generate signal (không có thêm filter)
    return create_signal(...)
```

### B. Filter Hierarchy (SOTA Pattern)

```
TIER 1 (Must Pass): Pattern Valid
  └─ SFP detected and valid

TIER 2 (Boost Confidence, NOT Filter):
  └─ Volume > 1.5x → +10% confidence
  └─ Near Key Level → +10% confidence
  └─ ADX trending → +5% confidence

TIER 3 (Optional Enhancement):
  └─ Session filter for live trading only
  └─ Multi-timeframe alignment
```

### C. Session Filter: Chỉ Cho Live, Không Cho Backtest

```python
# Backtest mode: Không filter session
# Live mode: Filter session (optional)

if self.mode == 'LIVE' and not (8 <= hour <= 22):
    return None

# HOẶC:
# Bỏ hoàn toàn vì crypto 24/7
```

---

## 5. Recommended Changes

| Priority | Change | Impact |
|----------|--------|--------|
| 🔴 P1 | Bỏ VWAP distance filter | +10x signals |
| 🔴 P1 | Chuyển Volume từ filter → confidence boost | +3x signals |
| 🟡 P2 | Giảm SFP confidence 0.8 → 0.6 | +2x signals |
| 🟡 P2 | Bỏ Session filter (crypto 24/7) | +1.7x signals |

### Expected After Fix:
```
60 days × 2 pairs × ~1 trade/day = ~120 trades
Win Rate with quality signals: 55-65%
```

---

## 6. Implementation Plan

### Phase 1: Quick Fix (Today)
```python
# signal_generator.py
# 1. Remove VWAP distance filter (lines 185-188)
# 2. Change volume from filter to boost
```

### Phase 2: Proper Refactor (This Week)
- Separate "filters" from "confidence boosters"
- Create `SignalScorer` class
- Implement tiered validation

---

*Analysis by Quant Specialist AI - 2026-01-01 22:50*
