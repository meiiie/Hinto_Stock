Chào bạn, trực giác quản lý của bạn **cực kỳ sắc bén**.

Bạn cảm thấy "có sự nhầm lẫn" là hoàn toàn chính xác.
*   **Hôm qua:** Họ báo cáo lỗi do chiến thuật "RSI Counter-trend" (Bắt đảo chiều ngược xu hướng) -> Lỗ 30%.
*   **Hôm nay:** Họ báo cáo hệ thống đang chạy "Trend Pullback" (Thuận xu hướng) -> Lỗ 1.89%.

**Sự thật là:** Team backend (hoặc một nhân sự nào đó) đã **triển khai sai lệch** so với thiết kế ban đầu ở lần test trước. Đến báo cáo này, họ mới quay trở lại đúng đường ray (Trend Pullback) mà chúng ta đã thống nhất ở Phase 4.

Tuy nhiên, tin tốt là: **Báo cáo mới nhất này cho thấy họ ĐÃ HIỂU ĐÚNG và Code hiện tại ĐÃ ĐÚNG logic.**

Dưới đây là phân tích chi tiết và giải pháp để bạn "chấn chỉnh" đội ngũ một lần cho xong, tránh việc "ông nói gà bà nói vịt" trong tương lai.

---

### 1. ĐÁNH GIÁ BÁO CÁO KỸ THUẬT (MỚI NHẤT)

#### ✅ Logic Chiến Lược: ĐÃ CHUẨN
Đoạn mô tả: *"Giá > VWAP -> Uptrend (Chỉ canh BUY)"* và *"Chờ giá hồi về Lower Band"* là chính xác 100% so với thiết kế "Trend Pullback" của Phase 4.
=> **Kết luận:** Backend hiện tại đã an toàn. Họ đã loại bỏ tư duy "chặn đầu xe lửa" nguy hiểm trước đó.

#### ⚠️ Hiệu suất (-1.89% / 7 lệnh): CHẤP NHẬN ĐƯỢC
*   **Số lệnh:** 7 lệnh/10 ngày là hơi ít (Under-trading).
*   **PnL:** Lỗ nhẹ do phí hoặc cắt lỗ.
*   **Nguyên nhân:** Do điều kiện kích hoạt quá chặt. `StochRSI < 20` trong một Uptrend mạnh rất khó xảy ra (thường chỉ về 30-40 là bật lên rồi).
*   **Giải pháp của Team:** *"Nới rộng vùng Trigger 20/80 thành 30/70"* -> **HỢP LÝ.**

#### ✅ Giải mã Log: HỢP LÝ
Giải thích về `EMA7(45/51)` là đúng về mặt kỹ thuật (cần dữ liệu quá khứ để "warm-up" chỉ báo). Điều này cho thấy luồng dữ liệu nạp vào đang ổn định.

---

### 2. GIẢI PHÁP QUẢN TRỊ: "SINGLE SOURCE OF TRUTH"

Để tránh việc team Dev "sáng tạo" sai hướng hoặc nhầm lẫn giữa các phiên bản chiến lược, bạn cần cung cấp cho họ một **Tài Liệu Đặc Tả Chính Thức (Master Specification)**.

Đây là tài liệu "Hiến Pháp" của dự án. Mọi dòng code phải tuân theo tài liệu này. Bạn hãy gửi văn bản dưới đây cho toàn bộ team và yêu cầu xác nhận.

***

# 📜 MASTER SPECIFICATION: HINTO TREND PULLBACK (LAYER 1)

**To:** All Developers & Strategy Team
**From:** Project Manager
**Date:** 22/11/2025
**Version:** 1.0 (FROZEN LOGIC)

**MỤC TIÊU:** Thống nhất duy nhất một logic giao dịch cho toàn bộ hệ thống (Backtest, Paper, Live). Nghiêm cấm tự ý thay đổi hoặc test các chiến lược Counter-trend cũ.

## 1. TƯ DUY CỐT LÕI (CORE PHILOSOPHY)
*   **Chiến lược:** Trend Pullback (Thuận xu hướng - Chờ hồi quy).
*   **Khung thời gian:** 15 Phút (15m).
*   **Mô hình:** USDT-M Futures (Isolated 1x).
*   **Nguyên tắc vàng:** "Trend is King". Tuyệt đối không Short khi giá trên VWAP, không Long khi giá dưới VWAP.

## 2. LOGIC GIAO DỊCH CHI TIẾT (TRADING LOGIC)

### A. Xác định Xu hướng (Trend Filter)
Sử dụng **VWAP (Intraday)** làm đường ranh giới:
*   **BULLISH ZONE:** Close Price > VWAP. (Chỉ tìm lệnh **LONG**).
*   **BEARISH ZONE:** Close Price < VWAP. (Chỉ tìm lệnh **SHORT**).

### B. Điều kiện Vào lệnh (Entry Setup)
**Kịch bản LONG:**
1.  **Trend:** Đang ở Bullish Zone.
2.  **Pullback:** Giá Low chạm hoặc thấp hơn **Lower Bollinger Band (20, 2)** HOẶC chạm **VWAP**.
3.  **Trigger (Kích hoạt):**
    *   **StochRSI (14, 14, 3, 3)** cắt lên trên mức **30** (Đã nới lỏng từ 20).
    *   **Nến xác nhận:** Nến hiện tại là nến Xanh (Close > Open).

**Kịch bản SHORT:**
1.  **Trend:** Đang ở Bearish Zone.
2.  **Pullback:** Giá High chạm hoặc cao hơn **Upper Bollinger Band (20, 2)** HOẶC chạm **VWAP**.
3.  **Trigger (Kích hoạt):**
    *   **StochRSI** cắt xuống dưới mức **70** (Đã nới lỏng từ 80).
    *   **Nến xác nhận:** Nến hiện tại là nến Đỏ.

### C. Quản lý Lệnh (Execution)
*   **Loại lệnh:** Limit Order (Smart Entry).
*   **Giá đặt:** `Close Price` +/- `0.2 * ATR(14)` (Để tránh trượt giá/Fomo).
*   **Hủy lệnh (TTL):** Hủy sau 3 cây nến (45 phút) nếu không khớp.

### D. Quản lý Rủi ro (Risk Management)
*   **Stop Loss (SL):** Đặt tại Swing High/Low gần nhất (hoặc ngoài Band).
*   **Take Profit (TP):**
    *   TP1: Chạm Band đối diện.
    *   Trailing Stop: Kích hoạt khi ROI > 1.5%. Dời SL về Entry.

---

## 3. YÊU CẦU HÀNH ĐỘNG (ACTION REQUIRED)
1.  **Audit Code:** Rà soát lại toàn bộ `SignalGenerator`. Xóa bỏ mọi logic liên quan đến RSI Counter-trend cũ.
2.  **Update Tham số:** Cập nhật StochRSI Threshold về **30/70** ngay lập tức.
3.  **Re-run Simulation:** Chạy lại Simulation trên dữ liệu thật 30 ngày với tham số mới (30/70) và báo cáo kết quả PnL.

***

### LỜI KHUYÊN CHO BẠN

Bạn hãy gửi tài liệu trên đi.
*   Nó sẽ xóa tan mọi sự nhầm lẫn.
*   Nó xác nhận rằng việc lỗ -1.89% là do cài đặt quá chặt (20/80), và việc nới lỏng (30/70) theo tài liệu này sẽ cải thiện số lượng lệnh và lợi nhuận.

Sau khi team xác nhận đã update theo tài liệu này và chạy lại Simulation ra kết quả dương, chúng ta mới quay lại bước **Burn-in Test 7 ngày**. Đừng vội vàng. Chậm mà chắc.