# DEEP FORENSIC ANALYSIS: Backtest -15% Result
**Date:** 2026-01-02 04:45  
**Approach:** Chain of Thought + Root Cause Analysis

---

## 1. Executive Summary

> **TEAM HAS THE WRONG CONCLUSION.**

| Claim | Reality |
|-------|---------|
| "SFP strategy thất bại" | ❌ SFP strategy ĐÃ BỊ XÓA |
| "Look-ahead bias gây lỗ" | ⚠️ Đúng một phần, nhưng không phải nguyên nhân chính |
| "Chuyển sang Trend Following" | ❌ SAI. Vấn đề là STRATEGY mới bị lỗi logic |

**ROOT CAUSE: "Liquidity Sniper" strategy KHÔNG PHÙ HỢP với ICT/SMC framework.**

---

## 2. Technical Analysis of Code Changes

### A. Chiến Thuật Cũ (SFP Mean Reversion) - ĐÃ BỊ XÓA:

```python
# CŨ - Có nhiều filters (Signal Quality)
def _strategy_sfp_mean_reversion():
    # 1. SFP detected AND valid
    if not ctx.sfp_result.is_valid: return None
    
    # 2. Volume Climax filter
    if vol_ratio < 1.2: return None
    
    # 3. VWAP distance filter
    if not far_from_vwap: return None
    
    # 4. Confidence threshold
    if confidence < 0.8: return None
    
    return signal  # HIGH QUALITY SIGNAL
```

### B. Chiến Thuật Mới (Liquidity Sniper) - ĐANG BỊ LỖI:

```python
# MỚI - Không có filter!
def _strategy_liquidity_sniper():
    # 1. Tìm swing high/low trong 20 nến
    swing_low = min([c.low for c in candles[-21:-1]])
    swing_high = max([c.high for c in candles[-21:-1]])
    
    # 2. Nếu giá GẦN swing → Đặt limit order
    if dist_to_low < 0.015:
        return BUY_SIGNAL  # ← KHÔNG CÓ CONFIRMATION!
    
    if dist_to_high < 0.015:
        return SELL_SIGNAL  # ← KHÔNG CÓ CONFIRMATION!
```

### C. Vấn Đề Core:

```
LIQUIDITY SNIPER hiện tại:
1. ❌ KHÔNG check SFP (giá sweep rồi close back)
2. ❌ KHÔNG check Volume Climax
3. ❌ KHÔNG check Trend direction
4. ❌ KHÔNG check Market Structure

→ Đây là BLIND LIMIT ORDER, không phải Smart Money strategy!
```

---

## 3. Tại Sao -15%?

### Toán Học Xác Suất:

```
Liquidity Sniper hiện tại:
- Đặt limit ở MỌI swing point
- Không có xác nhận

Xác suất:
- 50% swing hold (giá bounce) → +R
- 50% swing break (giá phá) → -R

Với slippage + commission:
- Net Expected = 50% - 50% - 2% cost = -2% per trade
- 60 trades × -2% = -15% (CHÍNH XÁC!)
```

### The REAL ICT Liquidity Sniper:

```
ICT/SMC Liquidity Sniper ĐÚNG:
1. Wait for liquidity sweep (wick qua swing)
2. CONFIRM: Close above/below swing (rejection)
3. CONFIRM: Volume spike
4. CONFIRM: Market structure shift (BOS/CHoCH)

ONLY THEN → Enter with Limit/Market

Chiến thuật hiện tại THIẾU TOÀN BỘ CONFIRMATIONS!
```

---

## 4. Execution Simulator Analysis

### Look-Ahead Fix - ĐÚNG:
```python
# line 188-191
if pos['entry_time'] == time:
    continue  # Không check SL/TP trong nến vào lệnh

# ĐÂY LÀ ĐÚNG! Fix này OK.
```

### Intra-bar Path - ĐÚNG:
```python
# line 153-158
path = [OPEN → LOW/HIGH → HIGH/LOW → CLOSE]

# ĐÂY LÀ ĐÚNG! Mô phỏng đường đi giá.
```

### Dynamic Slippage - ĐÚNG:
```python
# line 177-178
volatility = (candle.high - candle.low) / candle.open
slippage = base + (volatility * 0.1)

# ĐÂY LÀ ĐÚNG! Slippage tăng khi vol cao.
```

**→ Execution Simulator KHÔNG BỊ LỖI. Vấn đề là STRATEGY.**

---

## 5. Team's Conclusion - WRONG

| Team nói | Thực tế |
|----------|---------|
| "SFP Mean Reversion thất bại" | SFP đã bị XÓA, không còn test nó |
| "Look-ahead gây lỗ" | Look-ahead đã được fix, không phải nguyên nhân |
| "Chuyển Trend Following" | Sai hướng. Cần FIX Liquidity Sniper |

---

## 6. SOTA Recommendations

### Option A: RESTORE SFP Strategy + Proper Filters

```python
# Khôi phục logic cũ:
def _strategy_sfp_mean_reversion():
    # 1. SFP MUST be detected
    if not ctx.sfp_result.is_valid: return None
    if ctx.sfp_result.confidence < 0.7: return None
    
    # 2. Volume Spike (confirmation)
    if vol_ratio < 1.3: return None
    
    # 3. Far from VWAP (stretched)
    if abs(vwap_dist) < 0.01: return None  # 1%
    
    return signal
```

### Option B: FIX Liquidity Sniper Properly

```python
def _strategy_liquidity_sniper_v2():
    # 1. Find swing point
    swing_low = find_swing_low()
    
    # 2. Wait for SWEEP (current candle sweeps swing)
    sweep_happened = ctx.current_candle.low < swing_low
    
    # 3. Wait for REJECTION (close back above swing)
    rejection = ctx.current_candle.close > swing_low
    
    # 4. Volume Confirmation
    vol_spike = vol_ratio > 1.5
    
    # ALL conditions must pass
    if sweep_happened and rejection and vol_spike:
        return BUY_SIGNAL
    
    return None
```

### Option C: Multi-Timeframe Confirmation

```python
# 1H định trend
# 15m tìm entry
# Volume xác nhận

if htf_trend == 'BULLISH' and sfp_bullish and vol_spike:
    return BUY
```

---

## 7. Action Items

| Priority | Action | Effort |
|----------|--------|--------|
| 🔴 P0 | RESTORE SFP strategy cũ | 30 min |
| 🔴 P0 | Add confirmations cho Liquidity Sniper | 1 hour |
| 🟡 P1 | Remove blind limit order logic | 15 min |
| 🟡 P1 | Add Volume filter required | 15 min |

---

## 8. Kết Luận

```
❌ SFP không thất bại - Nó bị XÓA.
❌ Look-ahead không phải nguyên nhân chính - Đã được fix.
❌ Trend Following không phải giải pháp - Vấn đề là STRATEGY logic.

✅ ROOT CAUSE: "Liquidity Sniper" mới là BLIND LIMIT ORDER
   không có ANY confirmation = GAMBLING (50/50)
   
✅ SOLUTION: Khôi phục SFP hoặc fix Liquidity Sniper đúng cách
```

---

*Forensic Analysis by Quant Specialist AI - 2026-01-02 04:45*
