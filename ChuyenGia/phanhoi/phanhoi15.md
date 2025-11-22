Chào bạn, việc bạn cung cấp ảnh chụp màn hình thực tế từ Binance Futures là **cực kỳ giá trị**. Nó là "tiêu chuẩn vàng" (Gold Standard) để chúng ta đối chiếu.

Dựa trên 2 ảnh bạn gửi, tôi nhận thấy giao diện Paper Trading hiện tại của chúng ta còn thiếu một số chỉ số **tinh tế nhưng quan trọng** giúp trader ra quyết định nhanh.

Dưới đây là bản **Đánh giá & Yêu cầu Kỹ thuật Tổng hợp (Final Comprehensive Spec)**. Bản này bao gồm cả các yêu cầu trước đó và bổ sung thêm các tính năng từ ảnh Binance bạn vừa gửi. Hãy gửi bản này cho Team Dev để họ làm một lần cho chuẩn.

---

# 📑 CHỈ THỊ KỸ THUẬT: NÂNG CẤP GIAO DIỆN PAPER TRADING (BINANCE-LIKE)

**To:** Antigravity (Lead Developer) & Frontend Team
**From:** Chief Architect
**Date:** 21/11/2025
**Subject:** ĐỒNG BỘ HÓA UI/UX THEO TIÊU CHUẨN BINANCE FUTURES

## 1. PHÂN TÍCH KHOẢNG CÁCH (GAP ANALYSIS)
So sánh giữa giao diện Binance thực tế và Dashboard hiện tại:

| Chỉ số / Tính năng | Binance Futures | Hinto Paper Trading (Hiện tại) | Đánh giá |
| :--- | :--- | :--- | :--- |
| **Visual Side** | Thanh màu Xanh (Long) / Đỏ (Short) cạnh Symbol | Cột text "LONG/SHORT" | ❌ Binance trực quan hơn. |
| **Size** | Hiển thị cả Coin (0.658 BTC) | Hiển thị USDT ($15,000) | ⚠️ Cần cả 2 để rõ ràng. |
| **Break Even Price** | **Có (Giá hòa vốn)** | **Không** | ❌ Thiếu. Trader cần biết giá nào thì bắt đầu lãi (sau phí). |
| **Margin Mode** | Hiển thị "Isolated" / "Cross" | Không hiển thị | ⚠️ Nên thêm text "Isolated" cho chuẩn. |
| **Action Buttons** | Nút "Market", "Limit", "Reverse" ngay trên dòng | Không (Chỉ xem) | ❌ Cần nút "Close Market" để cắt lệnh khẩn cấp. |
| **TP/SL Display** | Nút "Add" hoặc hiển thị số | Hiển thị số thập phân quá dài | ❌ Cần làm tròn số đẹp. |

---

## 2. YÊU CẦU NÂNG CẤP CHI TIẾT (TECHNICAL REQUIREMENTS)

Yêu cầu team cập nhật lại `PaperPortfolioComponent` và `PaperTradingService` để hiển thị các cột sau trong bảng **Positions**:

### A. Cấu trúc Bảng (Table Columns) - Từ trái qua phải:

1.  **Symbol (Kèm Visual):**
    *   Hiển thị: `BTCUSDT`
    *   **Yêu cầu UI:** Thêm một vạch màu (Color Bar) bên trái Symbol. Xanh lá nếu Long, Đỏ nếu Short. (Giống ảnh 1).
    *   Badge: Thêm tag nhỏ `1x` (Leverage) và `Isolated`.

2.  **Size (Quy mô):**
    *   Hiển thị dòng 1: Số lượng Coin (VD: `0.658 BTC`) - *Tô màu theo chiều Long/Short*.
    *   Hiển thị dòng 2 (nhỏ hơn): Giá trị USDT (VD: `$54,500`).

3.  **Entry Price:** Giá vào lệnh trung bình.

4.  **Break-Even Price (Giá Hòa Vốn) - 🆕 MỚI:**
    *   *Logic:* Vì Paper Trading không mất phí thật, tạm thời `BreakEven = Entry Price`.
    *   *Nâng cao (Optional):* `Entry Price * (1 + 0.04% phí giả lập)`.
    *   *Tác dụng:* Giúp trader biết khi nào thực sự an toàn.

5.  **Mark Price:** Giá thị trường hiện tại (Cần update realtime).

6.  **Margin (Ký quỹ):**
    *   Hiển thị số tiền thực tế bị lock. VD: `9,500 USDT`.

7.  **PnL (ROI %):**
    *   Hiển thị: `+86.19 USDT (+3.15%)`.
    *   **Quan trọng:** Tô màu nền (Background) hoặc màu chữ đậm. Xanh lá tươi cho lãi, Đỏ tươi cho lỗ. Font chữ phải to, rõ ràng.

8.  **TP / SL:**
    *   Làm tròn 2 chữ số thập phân.
    *   Ví dụ: `83,500.00 / 81,200.00`.

9.  **Actions (Hành động) - 🆕 MỚI:**
    *   Thêm nút bấm **"Close All"** (Đóng ngay giá thị trường) ở cột cuối cùng.
    *   *Logic:* Khi bấm, gửi lệnh bán Market vào Engine để thoát vị thế ngay lập tức. Dùng cho trường hợp khẩn cấp.

### B. Bảng Open Orders (Lệnh Chờ)
*   Như yêu cầu trước: Cần hiển thị danh sách lệnh Limit đang chờ khớp (Entry, TP, SL chờ).

---

## 3. MẪU GIAO DIỆN MONG MUỐN (WIREFRAME)

Team Dev hãy tưởng tượng mỗi dòng trong bảng Positions sẽ trông như thế này (Mô phỏng Streamlit):

```text
| Symbol       | Size           | Entry / BE    | Mark Price | Margin    | PnL (ROI%)        | TP / SL           | Action |
|--------------|----------------|---------------|------------|-----------|-------------------|-------------------|--------|
| 🟢 BTCUSDT   | 0.658 BTC      | 82,825.70     | 82,967.30  | 2,714.00  | +86.19 (+3.15%)   | 84,000 / 81,000   | [Close]|
| 1x Isolated  | ($54,589)      | (82,825.70)   |            |           | (Color: Green)    |                   |        |
```

## 4. HƯỚNG DẪN THỰC HIỆN (IMPLEMENTATION NOTES)

1.  **Thư viện UI:** Sử dụng `st.column_config` của Streamlit để format số liệu đẹp mắt (thêm prefix `$`, suffix `%`, làm tròn).
2.  **Logic Break-Even:** Tạm thời gán `BreakEven = EntryPrice`.
3.  **Nút Close:** Sử dụng `st.button("Close", key=order_id)` và gọi hàm `paper_service.close_position(id)`.

---

### LỜI NHẮN CHO BẠN

Với bản yêu cầu bổ sung này (kết hợp từ ảnh Binance), hệ thống của bạn sẽ có giao diện **90% giống sàn thật**.
*   Trader nhìn vào sẽ thấy quen thuộc.
*   Thông tin đầy đủ (đặc biệt là nút **Close Market** cứu hộ).

Bạn hãy chuyển văn bản này cho team và yêu cầu họ hoàn thiện (Polish) giao diện trong vòng **24h tới** trước khi chạy Burn-in Test.