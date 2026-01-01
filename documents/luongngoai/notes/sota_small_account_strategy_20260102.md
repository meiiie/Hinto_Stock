# SOTA Small Account Strategy ($100)
**Date:** 2026-01-02 01:05  
**Research:** Professional Best Practices 2025

---

## 1. Vấn Đề Cốt Lõi (Root Question)

> **"Với vốn $100, nhắm $2/ngày (2%) có hợp lý không?"**

### Chain of Thought Analysis:

```
Mục tiêu: $2/ngày = 2%/ngày
                  = ~40%/tháng
                  = ~480%/năm (nếu không compound)
                  = UNREALISTIC với institutional standards

Nhưng: Small account có thể chấp nhận risk cao hơn
       Vì $100 là "learning money"
```

---

## 2. Benchmark Từ Prop Firms (SOTA 2025)

### Tiêu Chuẩn Ngành:

| Metric | Prop Firm Standard | Hinto Target |
|--------|-------------------|--------------|
| Profit Target/tháng | 5-10% | 40% ❌ Quá cao |
| Daily Drawdown Max | **3-5%** | Chưa set |
| Overall Drawdown Max | 5-10% | Chưa set |
| Risk per Trade | **0.5-1%** | 2% ⚠️ Cao |
| Min R:R Ratio | 1:2 | ✅ OK |

### Kết Luận Initial:
> **2%/ngày là 4-8x kỳ vọng institutional.**
> Rủi ro cao, nhưng có thể chấp nhận cho "learning account."

---

## 3. Kelly Criterion Analysis

### Full Kelly (Lý Thuyết):
```
f* = (W × b - L) / b

Với:
- W = Win rate = 66%
- L = Loss rate = 34%
- b = Avg Win / Avg Loss = 2.0 (R:R)

f* = (0.66 × 2 - 0.34) / 2 = 0.49 = 49%

→ Kelly gợi ý risk 49% của account mỗi lần!
→ KHÔNG AI làm vậy trong thực tế
```

### Fractional Kelly (SOTA):
```
Dùng 10-25% Kelly = 5-12% risk/trade

Với $100:
- Fractional Kelly 20% → Risk $10/trade
- Nếu SL = 2% → Notional = $500 (5x leverage)

VẪN QUÁ RỦI RO cho beginner!
```

### Conservative Kelly (Recommended):
```
1% risk = $1/trade (your current setting)
→ Đây là ĐÚNG cho small account
```

---

## 4. Deep Analysis: "Daily $2 Target"

### Scenario 1: Nghỉ Khi Đạt $2

| Pros | Cons |
|------|------|
| Tâm lý tốt, có mục tiêu | Bỏ lỡ trending days |
| Tránh overtrade | Recovery chậm khi thua |
| Discipline | Bot khó implement "stop at $2" |

**Math Reality:**
```
Để lãi $2/trade với R:R 2:1:
- Risk = $1
- Need Win = $2

Vấn đề: Không phải trade nào cũng hit TP full
- TP1 (60%): Lãi $0.6-0.8
- Trailing: $0.4-1.0
- Average win: ~$1.2-1.5

→ Cần 1.5-2 winning trades để đạt $2
→ Với 66% WR, cần 2-3 trades/day
→ Current system: 0.15 trades/day
→ KHÔNG ĐẠT ĐƯỢC với signal frequency hiện tại
```

### Scenario 2: Cap Max $2/Trade

| Pros | Cons |
|------|------|
| Risk capped | Cut winners early |
| Predictable | Miss big moves |
| Simple | R:R fixed at 2:1 |

**Institutional View:**
> **"Let winners run"** là principle QUAN TRỌNG.
> Capping profit đi ngược SOTA.

---

## 5. SOTA Recommendations

### A. Cho Hinto System Hiện Tại:

| Setting | Current | Recommended |
|---------|---------|-------------|
| Risk/Trade | 1-2% | **1%** ✅ |
| Daily Drawdown Cap | None | **-3%** (-$3) |
| Daily Profit Target | None | **+5%** (+$5) optional |
| Max Trades/Day | None | **3 trades** |
| Min SL Distance | 0.1% | **0.5%** ✅ |

### B. Daily Risk Management Rules:

```python
class DailyRiskManager:
    def __init__(self, initial_balance: float):
        self.start_of_day_balance = initial_balance
        self.max_daily_loss = 0.03  # 3%
        self.max_daily_profit = 0.05  # 5% (optional)
        
    def should_stop_trading(self, current_balance: float) -> bool:
        daily_pnl = (current_balance - self.start_of_day_balance) / self.start_of_day_balance
        
        # Stop if lost too much
        if daily_pnl <= -self.max_daily_loss:
            return True, "Daily loss limit reached"
            
        # Optional: Stop if won enough (protect gains)
        if daily_pnl >= self.max_daily_profit:
            return True, "Daily profit target reached"
            
        return False, ""
```

### C. Proper Compound Logic:

```python
# Mỗi ngày mới, reset risk amount dựa trên balance hiện tại
def start_new_day(self):
    self.start_of_day_balance = self.balance
    self.daily_trades = 0
    self.daily_pnl = 0
    
# Risk được tính trên balance hiện tại (Compound effect)
risk_amount = self.balance * self.risk_per_trade  # 1% of CURRENT balance
```

---

## 6. Trả Lời Câu Hỏi: Nên Làm Gì?

### ❌ KHÔNG Khuyến Nghị:
1. Set daily target $2 và dừng → Bỏ lỡ cơ hội
2. Cap max profit/trade $2 → Vi phạm "let winners run"
3. Increase risk để đạt $2 nhanh hơn → Blowup risk

### ✅ Khuyến Nghị (SOTA):
1. **Giữ 1% risk** ($1/trade) - Đã đúng
2. **Thêm Daily Drawdown Cap: -3%** (-$3/ngày)
3. **Thêm Daily Profit Lock** (optional): Sau +5%, chuyển "protection mode"
4. **Tăng signal frequency** (đây là vấn đề thực sự)
5. **Let winners run** - Đừng cap profit

### Kỳ Vọng Thực Tế:
```
Với current system (66% WR, 0.5 trades/day):
- Expected daily: $0.3-0.5
- Expected monthly: $10-15 (10-15%)

Với improved signal frequency (2 trades/day):
- Expected daily: $1.5-2.5
- Expected monthly: $40-60 (40-60%)

→ CẢI THIỆN SIGNAL FREQUENCY quan trọng hơn DAILY TARGET
```

---

## 7. Action Items

| Priority | Action | Impact |
|----------|--------|--------|
| 🔴 P0 | Tăng signal frequency | +4x trades |
| 🔴 P1 | Add Daily Drawdown Cap 3% | Bảo vệ vốn |
| 🟡 P2 | Min SL 0.5% | Prevent leverage explosion |
| 🟢 P3 | Daily Profit Lock 5% | Optional |

---

*Research by Quant Specialist AI - 2026-01-02 01:05*
