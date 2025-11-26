# Phản hồi Chuyên gia - 26/11/2025 (Chiều)

## Trạng thái: ✅ APPROVED

**APPROVED. PROCEED TO DAY 27/11 PLAN.**

## Chỉ đạo kỹ thuật

### 1. Chart Markers
- Implement visual markers cho **50 trades gần nhất**
- **KHÔNG** load full history để bảo toàn performance
- Sử dụng `series.setMarkers()` từ lightweight-charts

### 2. Performance Dashboard
- Implement **Equity Curve Chart**
- **CRITICAL:** Cần visualize stability, không chỉ final PnL

### 3. Stability Check (Ưu tiên)
- Prioritize **WebSocket Auto-reconnect**
- Simulate network failure
- Đảm bảo 'Live' indicator chuyển Đỏ → Xanh tự động khi reconnect

### 4. Ghi chú về UI
- Inline styles được chấp nhận như temporary fix
- **Focus on Logic & Data Visualization today**

---

## Kế hoạch ngày 27/11/2025

### Ưu tiên 1: WebSocket Auto-reconnect
- [ ] Implement reconnection logic (5s interval)
- [ ] Update ConnectionStatus component
- [ ] Test với network failure simulation

### Ưu tiên 2: Chart Markers (Last 50 trades)
- [ ] Fetch last 50 trades từ API
- [ ] Sử dụng `series.setMarkers()` 
- [ ] Mũi tên xanh (BUY) / đỏ (SELL)

### Ưu tiên 3: Equity Curve Chart
- [ ] API endpoint cho equity history
- [ ] Line chart hiển thị equity theo thời gian
- [ ] Tích hợp vào Performance Dashboard
