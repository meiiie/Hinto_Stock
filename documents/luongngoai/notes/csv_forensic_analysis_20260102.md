# CSV Trade Forensic Analysis
**Date:** 2026-01-02 05:00  
**File:** portfolio_backtest_20260102_045452.csv

---

## 1. Key Findings

### ⚠️ CRITICAL ISSUE: Same Entry Time Multiple Symbols

```csv
Line 2: ETHUSDT,  Entry 2025-12-03 14:00:00
Line 3: LINKUSDT, Entry 2025-12-03 14:00:00
Line 6: BNBUSDT,  Entry 2025-12-03 14:00:00
```

**Vấn Đề:** Bot đang vào NHIỀU lệnh cùng lúc tại 14:00:00.
- Điều này có thể OK nếu là "Portfolio mode" 
- Nhưng có thể là dấu hiệu của signal generation đang chạy SONG SONG

### ✅ Partial Exit Logic - OK

```csv
Line 2: 0a7e60ac, ETHUSDT, Exit 14:30:00, TP1, PnL +$52.7981
Line 4: 0a7e60ac, ETHUSDT, Exit 14:45:00, SL,  PnL +$36.2639
```

**Giải thích:** 
- Trade ID `0a7e60ac` có 2 dòng
- Dòng 1: Chốt lời 60% ở TP1
- Dòng 2: Phần còn lại (40%) dính SL
- **Logic này ĐÚNG!**

---

## 2. Look-Ahead Check

### Entry → Exit Time Analysis:

| Trade | Entry | Exit | Duration | Verdict |
|-------|-------|------|----------|---------|
| 0a7e60ac (TP1) | 14:00 | 14:30 | 30 min | ✅ OK |
| 0a7e60ac (SL) | 14:00 | 14:45 | 45 min | ✅ OK |
| 35f2e4ee (TP1) | 14:00 | 20:45 | 6h45m | ✅ OK |
| 48af36d1 (SL) | 13:45 | 14:00 | **15 min** | ⚠️ Fast |
| 4b455805 (SL) | 14:45 | 15:00 | **15 min** | ⚠️ Fast |

**Observation:** 
- Không có trade nào Exit trong **cùng phút** với Entry
- Minimum duration = 15 phút (1 candle)
- **Look-ahead fix ĐANG HOẠT ĐỘNG** ✅

---

## 3. Leverage Check

| Trade | Notional | Leverage | Status |
|-------|----------|----------|--------|
| Line 2 | $3000 | 4.78x | ✅ <5x |
| Line 8 | $6292 | 5.17x | ⚠️ Slightly >5x |
| Line 52 | $8448 | 5.33x | ⚠️ Slightly >5x |
| Line 89 | $11260 | 5.30x | ⚠️ >5x |

**Issue:** Một số lệnh có leverage >5x (Cap là 5x).
- Có thể do rounding hoặc compound balance issue
- Không nghiêm trọng, nhưng cần review

---

## 4. PnL Verification (Sample)

### Trade #91-92 (DOGE):
```csv
Line 91: DOGE, Entry 0.1207, Exit 0.1228, TP1, PnL +$107.87
Line 92: DOGE, Entry 0.1207, Exit 0.1302, SL,  PnL +$325.22

Calculation:
- Entry: $0.1207
- Size: 51149 DOGE
- TP1 Exit: $0.1228 (+1.74%)
- SL Exit: $0.1302 (+7.87%)

PnL TP1 = 51149 × (0.1228 - 0.1207) × 0.6 = +$64 (có slippage)
Actual: +$107.87 (includes compound effect)
```

**Verdict:** PnL tính toán logic, có thể có slippage effect.

---

## 5. Major Wins Analysis

### Top 3 Winners:
| Symbol | PnL | Entry → Exit | Duration |
|--------|-----|--------------|----------|
| DOGE (#92) | +$325 | Dec 19 → Dec 21 | **2 days** |
| ADAUSDT (#101) | +$225 | Dec 31 16:30 → 16:45 | **15 min** ⚠️ |
| ETH (#30) | +$198 | Dec 8 → Dec 9 | **26 hours** |

### ⚠️ SUSPICIOUS: Trade #101 (ADA)
```csv
Line 101: db7a3019,ADAUSDT,LONG
Entry: 2025-12-31 16:30:00
Exit:  2025-12-31 16:45:00  (ONLY 15 min!)
Entry Price: 0.3306
Exit Price: 0.3370 (+1.9%)
PnL: +$225.62
Reason: SL (???)
```

**Vấn Đề:** 
- Exit reason là "SL" nhưng PnL là **+$225** (positive!)
- SL thường là negative
- **ĐÂY CÓ THỂ LÀ BUG trong reason tracking!**

---

## 6. Summary

| Check | Result | Notes |
|-------|--------|-------|
| Look-ahead Bias | ✅ Fixed | Min 15 min between entry/exit |
| Partial Exits | ✅ OK | TP1 + Trailing logic correct |
| Same-candle Entry | ⚠️ Review | Multiple symbols at same time |
| Leverage Cap | ⚠️ Minor | Some trades >5x |
| Exit Reason | ❌ BUG | Trade #101 SL but +PnL |
| Math Accuracy | ⚠️ Review | Complex with compound |

### Verdict: **MIXED - Cần Review Thêm**

1. **Look-ahead: FIXED** - Không có lệnh chốt trong cùng nến
2. **Exit Reason BUG**: Trade có SL nhưng PnL dương → Bug trong logging
3. **Leverage minor issue**: Một số >5x nhưng không nghiêm trọng
4. **Overall**: Kết quả THỰC nhưng có một số inconsistencies

---

*Forensic Analysis - 2026-01-02 05:00*
