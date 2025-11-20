Chào bạn, đây là bản **Báo Cáo Kỹ Thuật & Yêu Cầu Cải Tiến (Technical Restructuring Request)** hoàn chỉnh.

Bản báo cáo này được viết dưới góc độ của một **Chief Architect**, tổng hợp toàn bộ các phân tích chúng ta đã thảo luận (từ lỗi xung đột chỉ báo, quản lý vốn R:R, đến tối ưu hóa điểm vào lệnh Entry). Bạn hãy gửi tài liệu này cho team Dev/AI của bạn để họ triển khai ngay lập tức.

---

# 📑 BÁO CÁO CẢI TIẾN HỆ THỐNG: HINTO STOCK AI TRADING (LAYER 1)

**To:** Development Team, AI Research Team  
**From:** System Architect / Trading Strategy Consultant  
**Date:** November 20, 2025  
**Subject:** TÁI CẤU TRÚC THUẬT TOÁN LAYER 1 - CHUYỂN ĐỔI TỪ "MEAN REVERSION" SANG "TREND PULLBACK"  
**Priority:** CRITICAL (Urgent Implementation Required)

---

## 1. TÓM TẮT ĐIỀU HÀNH (EXECUTIVE SUMMARY)

Hệ thống hiện tại (v3.1) đang gặp lỗi nghiêm trọng về mặt thiết kế chiến lược (Design Flaw), dẫn đến hai kết quả không thể chấp nhận:
1.  **Tỷ lệ lệnh (Signal Freq):** Bằng 0 hoặc rất thấp do xung đột logic giữa các chỉ báo (RSI quá bán >< Price trên EMA).
2.  **Hiệu suất (Performance):** Backtest 90 ngày cho thấy lỗ -35%, Drawdown 34%, tỷ lệ R:R (Risk/Reward) bị âm (Lỗ $93 để ăn $50).

**MỤC TIÊU CẢI TIẾN:**
Chuyển đổi hoàn toàn tư duy giao dịch từ **"Bắt đáy ngược xu hướng" (Catching Knife)** sang **"Mua điều chỉnh trong xu hướng tăng" (Trend Pullback)**. Tối ưu hóa điểm vào lệnh (Entry) để đạt R:R tối thiểu 1:1.5.

---

## 2. PHÂN TÍCH NGUYÊN NHÂN GỐC RỄ (ROOT CAUSE ANALYSIS)

| Vấn đề | Mô tả kỹ thuật | Tác động |
| :--- | :--- | :--- |
| **Xung đột Chỉ báo** | Code yêu cầu `RSI < 30` (Giá sập mạnh) ĐỒNG THỜI `Price > EMA7` (Giá đang tăng). Đây là điều kiện nghịch lý trong 99% trường hợp. | **0 Trades / Missed Trades.** |
| **Entry Fomo** | Hệ thống sử dụng `Market Order` ngay khi đóng nến tín hiệu. Không chờ giá hồi (Retracement). | **Entry giá xấu, Stoploss quá xa, dễ bị quét.** |
| **Chỉ báo không phù hợp** | Sử dụng EMA/ATR cho khung 15m Scalping gây nhiễu (Noise) và trễ (Lag). | **Stoploss bị cắn liên tục, TP3 (5R) không bao giờ chạm tới.** |

---

## 3. YÊU CẦU KỸ THUẬT MỚI (NEW TECHNICAL SPECIFICATION)

Team Dev cần loại bỏ bộ chỉ báo cũ và cài đặt bộ chỉ báo mới chuyên dụng cho **Short-term Trading (15m/1H)**:

### 3.1. Bộ Chỉ Báo Mới (New Indicator Stack)

1.  **VWAP (Volume Weighted Average Price):** *Thay thế EMA.* Dùng để xác định xu hướng trong ngày và hỗ trợ cứng của "dòng tiền lớn".
2.  **Bollinger Bands (20, 2):** *Thay thế ATR Stoploss.* Dùng để đo độ biến động và xác định điểm quá mua/quá bán tương đối.
3.  **Stochastic RSI (3, 3, 14, 14):** *Thay thế RSI(6).* Dùng để tìm điểm kích hoạt (Trigger) chính xác từng nến.
4.  **Volume + Candle Color:** *Giữ nguyên.* Xác nhận dòng tiền.

### 3.2. Logic Tạo Tín Hiệu (Signal Logic Flow)

**🟢 ĐIỀU KIỆN MUA (BUY SIGNAL):**

1.  **Trend Filter (Bộ lọc Xu hướng):**
    *   `Close Price > VWAP` (Giá nằm trên vùng giá trị trung bình của phe Mua).
    *   *Optional:* Dải Bollinger Bands đang mở rộng hoặc đi ngang (Tránh lúc thị trường co thắt quá hẹp).

2.  **Setup (Điều kiện chờ):**
    *   Giá điều chỉnh (Pullback) chạm hoặc thủng nhẹ `Lower Bollinger Band`.
    *   *Hoặc:* Giá chạm lại `VWAP`.

3.  **Trigger (Kích hoạt):**
    *   `StochRSI` (dòng K hoặc D) cắt lên trên mức 20 (Vùng quá bán).
    *   Nến hiện tại là **Nến Xanh** (`Close > Open`).
    *   `Volume` nến xanh > `Volume` nến đỏ trước đó (Lực mua thắng thế).

**🔴 ĐIỀU KIỆN BÁN (SELL SIGNAL):**
*   Ngược lại với logic Mua (Giá < VWAP, Chạm Upper Band, StochRSI cắt xuống 80).

---

## 4. TỐI ƯU HÓA ĐIỂM VÀO LỆNH (SMART ENTRY ALGORITHM)

Tuyệt đối **KHÔNG** vào lệnh Market (MP) ngay khi đóng nến. Yêu cầu cài đặt thuật toán tính toán Entry như sau:

### Logic "Smart Limit Entry":
```python
def calculate_smart_entry(candle_data, signal_type):
    """
    Mục tiêu: Mua rẻ hơn đám đông Fomo từ 20-30% thân nến tín hiệu.
    """
    open_p = candle_data['open']
    close_p = candle_data['close']
    high_p = candle_data['high']
    low_p = candle_data['low']
    
    body_size = abs(close_p - open_p)
    total_range = high_p - low_p
    
    # Nếu nến tín hiệu quá mạnh (Marubozu), chờ hồi sâu
    pullback_ratio = 0.3 # Mặc định chờ hồi 30% thân nến
    if body_size > total_range * 0.8:
        pullback_ratio = 0.5 # Nến quá dài thì chờ hồi 50%
        
    if signal_type == 'BUY':
        # Đặt lệnh Limit thấp hơn giá đóng cửa
        entry_price = close_p - (body_size * pullback_ratio)
    else: # SELL
        # Đặt lệnh Limit cao hơn giá đóng cửa
        entry_price = close_p + (body_size * pullback_ratio)
        
    return entry_price
```

---

## 5. QUẢN LÝ RỦI RO & THOÁT LỆNH (RISK & EXIT RULES)

Cập nhật lại file `RiskManager`:

1.  **Stop Loss (SL):**
    *   **BUY:** Đặt dưới đáy thấp nhất của 3 nến gần nhất (Swing Low) - Buffer 0.2%.
    *   *Không dùng 3x ATR nữa.*

2.  **Take Profit (TP):**
    *   **TP1 (70% Vol):** Tại đường `Upper Bollinger Band` (đối với Buy) hoặc `Lower Band` (đối với Sell).
    *   **TP2 (30% Vol):** Thả nổi (Trailing Stop) theo đường VWAP hoặc khi nến đóng cửa ngược chiều xu hướng.

3.  **Trailing Stop (Bảo toàn vốn):**
    *   Kích hoạt ngay khi giá chạy được **1R** (Lợi nhuận = Rủi ro). Dời SL về Entry (Breakeven).

---

## 6. LỘ TRÌNH THỰC HIỆN (IMPLEMENTATION ROADMAP)

Yêu cầu team hoàn thành các bước sau trong 48h tới:

*   **Bước 1 (Library):** Cài đặt/Import thêm thư viện tính toán VWAP và StochRSI (TA-Lib hoặc Pandas-TA).
*   **Bước 2 (Refactor):** Viết lại hàm `_check_buy_conditions` và `_check_sell_conditions` trong `signal_generator.py` theo logic Trend Pullback ở mục 3.2.
*   **Bước 3 (Entry Upgrade):** Thêm hàm `calculate_smart_entry` vào class `SignalGenerator` và update object `TradingSignal` trả về giá Limit thay vì None.
*   **Bước 4 (Validation):** Chạy Backtest 30 ngày gần nhất.
    *   *Target:* Winrate > 55%, Profit Factor > 1.5, Drawdown < 15%.

---

## 7. KẾT LUẬN

Việc thay đổi này không chỉ là sửa code, mà là nâng cấp hệ thống lên tiêu chuẩn **Professional Algorithmic Trading**. Chúng ta sẽ ngừng việc đoán đáy (Gambling) và chuyển sang giao dịch theo xác suất thống kê có lợi thế (Statistical Edge).

Yêu cầu team xác nhận đã nhận thông tin và tiến hành triển khai.

**[End of Report]**