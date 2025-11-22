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

**[End of Report]**Chào bạn, tôi đã đọc kỹ **Báo Cáo Kiểm Toán** từ team của bạn.

**ĐÁNH GIÁ:**
Team của bạn rất trung thực và thẳng thắn nhận lỗi. Đây là thái độ làm việc chuyên nghiệp.
Họ đã tìm ra chính xác "con bọ" (bug) mà tôi dự đoán: **Sử dụng `Total Balance` thay vì `Available Balance`**.

Giải pháp họ đề xuất là **CHÍNH XÁC** và **CHUẨN MỰC** cho một hệ thống Spot Trading.

Dưới đây là phản hồi chính thức và **Lệnh Phê Duyệt (Approval Order)** để bạn gửi cho team triển khai ngay.

---

# 📜 PHÊ DUYỆT GIẢI PHÁP & CHỈ ĐẠO KỸ THUẬT (FIX PLAN)

**To:** Development Team
**From:** Chief Architect
**Subject:** PHÊ DUYỆT KẾ HOẠCH SỬA LỖI QUẢN LÝ VỐN

## 1. PHÊ DUYỆT (APPROVAL)
Tôi đồng ý hoàn toàn với kế hoạch sửa lỗi (Fix Plan) mà team đề xuất, bao gồm:
1.  Triển khai hàm `calculate_locked_balance()`.
2.  Áp dụng công thức kiểm tra: `Order Cost <= (Total Balance - Locked Balance)`.
3.  Áp dụng kiểm tra số dư cho cả **Manual Order**.

## 2. LƯU Ý KỸ THUẬT BỔ SUNG (TECHNICAL NOTES)
Để đảm bảo việc sửa lỗi này triệt để và logic chặt chẽ hơn, yêu cầu team chú ý 2 điểm sau khi code:

### 🔧 A. Logic tính toán Volume (Position Sizing)
Khi sửa code, hãy lưu ý logic tính khối lượng lệnh cũng phải thay đổi theo:
*   **Cũ:** `size = min(calc_size, total_balance * 0.5)`
*   **Mới:** `size = min(calc_size, available_balance * 0.99)`
    *   *Giải thích:* Khối lượng lệnh không được vượt quá số tiền *đang rảnh rỗi*. Tôi để buffer 0.99 (giữ lại 1%) để tránh lỗi làm tròn số thập phân (Floating point error) khiến lệnh bị từ chối vô lý vì thiếu 0.000001 USDT.

### 🔧 B. Hiển thị UI (Dashboard Update)
Trên Dashboard, tại phần **Account Info**, yêu cầu hiển thị rõ ràng 3 thông số để User dễ kiểm soát:
*   **Total Balance:** $10,000
*   **Locked:** $5,000 (Màu vàng - Đang treo lệnh)
*   **Available:** $5,000 (Màu xanh - Có thể dùng)

## 3. YÊU CẦU "HARD RESET" (Dọn dẹp dữ liệu)
Vì dữ liệu hiện tại đang bị sai lệch nghiêm trọng (Lệnh ảo $50k, PnL tính sai do đòn bẩy), và việc chạy SQL sửa lỗi đang gặp trục trặc về đường dẫn.

**QUYẾT ĐỊNH:**
Yêu cầu team thực hiện **HARD RESET (Xóa làm lại)** Database để có môi trường test sạch sẽ nhất cho phiên bản vá lỗi này.

**Hành động:**
1.  Stop Bot.
2.  Xóa file `trading_system.db`.
3.  Start Bot (Hệ thống sẽ tự tạo lại file DB mới tinh với số dư $10,000 chuẩn).
4.  Đặt lại các lệnh test.

---

### 4. LỜI NHẮN CHO PROJECT MANAGER (BẠN)

Bạn hãy cho team thực hiện ngay (thời gian dự kiến 45 phút là hợp lý).

Sau khi họ sửa xong và Reset DB:
1.  Bạn sẽ thấy Balance quay về $10,000.
2.  Hãy thử đặt 3 lệnh mua liên tiếp (mỗi lệnh $4,000).
3.  **Kỳ vọng:** Lệnh 1 ($4k) -> OK. Lệnh 2 ($4k) -> OK. Lệnh 3 ($4k) -> **Hệ thống phải TỪ CHỐI (REJECTED)** vì chỉ còn dư $2,000.

Nếu hệ thống làm được điều này, tức là Module Quản Lý Vốn đã an toàn để chạy thực tế.