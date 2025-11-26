# Báo cáo Chart Markers & Equity Curve Implementation

**Ngày:** 27/11/2025  
**Người thực hiện:** Developer  
**Yêu cầu từ:** Chuyên gia (Performance Metrics & Chart Markers)

---

## 1. Tổng quan

Đã triển khai đầy đủ:
1. **Chart Markers** - Hiển thị BUY/SELL signals trên chart
2. **Equity Curve** - Biểu đồ theo dõi equity theo thời gian

---

## 2. Chart Markers - ✅ HOÀN THÀNH

### 2.1 Tính năng

| Tính năng | Trạng thái | Chi tiết |
|-----------|------------|----------|
| BUY markers | ✅ Có | ▲ màu xanh, vị trí belowBar |
| SELL markers | ✅ Có | ▼ màu đỏ, vị trí aboveBar |
| Realtime signals | ✅ Có | Từ WebSocket |
| Historical signals | ✅ Có | Fetch từ /trades/history |
| Tooltip on hover | ✅ Có | Entry, SL, TP, Confidence, R:R |
| Signal overlay | ✅ Có | Hiển thị 5 signals gần nhất |

### 2.2 Visual Components

1. **Markers Overlay** (góc phải trên chart):
   - Hiển thị 5 signals gần nhất
   - BUY: ▲ nền xanh
   - SELL: ▼ nền đỏ
   - Hiển thị giá entry

2. **Tooltip khi hover**:
   - Entry Price, Stop Loss, Take Profit
   - Confidence %, Risk:Reward Ratio

3. **Active Signal Info Bar** (dưới chart)

---

## 3. Equity Curve - ✅ HOÀN THÀNH

### 3.1 Tính năng

| Tính năng | Trạng thái | Chi tiết |
|-----------|------------|----------|
| Area Chart | ✅ Có | lightweight-charts AreaSeries |
| Period selector | ✅ Có | 7d, 30d, 90d, All |
| Color coding | ✅ Có | Xanh nếu tăng, đỏ nếu giảm |
| Start/End values | ✅ Có | Hiển thị equity đầu → cuối |
| API endpoint | ✅ Có | /trades/equity-curve |

### 3.2 Backend API

```python
@router.get("/equity-curve")
async def get_equity_curve(days: int = 7):
    # Returns daily equity values based on trade history
    return {"equity_curve": [
        {"time": "2025-11-20", "equity": 10000, "pnl": 0},
        {"time": "2025-11-21", "equity": 10150, "pnl": 150},
        ...
    ]}
```

### 3.3 Frontend Chart

- **Chart type:** Area chart với gradient fill
- **Colors:** 
  - Positive trend: Green (#2EBD85)
  - Negative trend: Red (#F6465D)
- **Height:** 150px
- **Location:** Trong PerformanceDashboard component

---

## 4. Files đã thay đổi

| File | Thay đổi |
|------|----------|
| `frontend/src/components/CandleChart.tsx` | Markers rendering, trade history fetch, overlay UI |
| `frontend/src/components/PerformanceDashboard.tsx` | Equity Curve chart |
| `src/api/routers/trades.py` | /equity-curve endpoint |

---

## 5. Kiểm tra

- ✅ TypeScript: Không có lỗi
- ✅ Python: Không có lỗi
- ⏳ Runtime: Cần test với data thực tế

---

## 6. Screenshots (Expected)

### Chart Markers:
```
┌─────────────────────────────────────────┐
│  BTC/USDT                    [Markers]  │
│                              ▲ BUY $95k │
│     ╱╲                       ▼ SELL $96k│
│    ╱  ╲    ▼ SELL                       │
│   ╱    ╲  ╱╲                            │
│  ╱      ╲╱  ╲                           │
│ ╱   ▲ BUY    ╲                          │
└─────────────────────────────────────────┘
```

### Equity Curve:
```
┌─────────────────────────────────────────┐
│ Equity Curve        $10,000 → $10,450   │
│ ╭──────────────────────────╮            │
│ │    ╱╲      ╱╲    ╱╲     │            │
│ │   ╱  ╲    ╱  ╲  ╱  ╲    │            │
│ │  ╱    ╲  ╱    ╲╱    ╲   │            │
│ │ ╱      ╲╱              ╲  │            │
│ ╰──────────────────────────╯            │
└─────────────────────────────────────────┘
```

---

---

## 8. CẬP NHẬT THEO GÓP Ý CHUYÊN GIA (27/11/2025)

### 8.1 Equity Curve - Trade-by-Trade Resolution ✅

**Yêu cầu:** Thay đổi từ Daily → Trade-by-Trade resolution

**Đã triển khai:**

| Tính năng | Chi tiết |
|-----------|----------|
| Resolution parameter | `?resolution=trade` (default) hoặc `?resolution=daily` |
| Per-trade updates | Mỗi điểm = equity sau khi trade đóng |
| Trade metadata | Bao gồm trade_id, side, result (WIN/LOSS) |
| Timestamp format | ISO 8601 với giờ:phút:giây |

**API Response mới:**
```json
{
  "equity_curve": [
    {"time": "2025-11-27T10:30:00", "equity": 10000, "pnl": 0, "trade_id": null},
    {"time": "2025-11-27T11:15:00", "equity": 10150, "pnl": 150, "trade_id": "t1", "side": "LONG", "result": "WIN"},
    {"time": "2025-11-27T14:45:00", "equity": 10050, "pnl": -100, "trade_id": "t2", "side": "SHORT", "result": "LOSS"}
  ],
  "resolution": "trade",
  "initial_balance": 10000,
  "current_equity": 10050
}
```

### 8.2 Performance Check - Markers Limit ✅

**Yêu cầu:** Đảm bảo không lag khi zoom/pan với nhiều markers

**Đã triển khai:**
- Giới hạn tối đa **100 markers** trên chart
- Chỉ hiển thị 100 markers gần nhất
- Trade history fetch giới hạn 50 trades

### 8.3 Data Consistency Check ✅

**Yêu cầu:** Equity Curve phải khớp với Portfolio Balance

**Đã triển khai:**
- API trả về `current_equity` để verify
- Frontend log để kiểm tra consistency
- Cùng source data (trade history)

---

## 9. Files đã cập nhật (Lần 2)

| File | Thay đổi |
|------|----------|
| `src/api/routers/trades.py` | Trade-by-trade resolution, metadata |
| `frontend/src/components/PerformanceDashboard.tsx` | Sử dụng resolution=trade |
| `frontend/src/components/CandleChart.tsx` | Giới hạn 100 markers |

---

**Trạng thái: ✅ HOÀN THÀNH - Đã cập nhật theo góp ý chuyên gia**
