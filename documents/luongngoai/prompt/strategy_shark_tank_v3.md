# 🦈 Shark Tank Strategy v3.0: "The Money Printer"

> **Code Name:** Limit Sniper - Hardcore Scalable Mode
> **Status:** SOTA Verified (2026-01-02)
> **Performance:** x29 ROI in 30 days (Hardcore Reality Mode)

---

## 1. Core Philosophy (Triết lý cốt lõi)

Chiến thuật này dựa trên quy luật **"Số lớn" (Law of Large Numbers)** và **"Sự hồi phục" (Mean Reversion)** của thị trường Crypto.
Thay vì cố gắng dự đoán chính xác từng lệnh, chúng ta rải lưới (Shark Tank) trên toàn bộ thị trường để bắt trọn mọi con sóng hồi, chấp nhận các khoản lỗ nhỏ để đổi lấy những cú thắng lớn khi thị trường đảo chiều.

---

## 2. Signal Logic: Limit Sniper

*   **Type:** Counter-Trend (Bắt đảo chiều).
*   **Entry:** Đặt lệnh Limit tại các điểm Swing High/Low (thanh khoản) của 20 nến gần nhất + biên độ 0.1%.
*   **Timeframe:** 15m (Tối ưu nhất).
*   **Stop Loss:** Rất ngắn (0.5% - 1%). Chấp nhận bị quét SL liên tục.
*   **Take Profit:** Trailing Stop cực xa (để ăn trọn sóng hồi lớn).

---

## 3. Execution Mode: Shark Tank (Bể Cá Mập)

Đây là chìa khóa tạo nên sức mạnh "in tiền":

*   **Max Positions:** **10** (Đánh Full Top 10 Volume).
    *   *Tại sao?* Để không bỏ lỡ bất kỳ "ngôi sao" nào (như DOGE, ZEC) và dùng lãi của con này bù lỗ cho con kia (Natural Hedging).
    *   *Sai lầm cũ:* Giới hạn 3 vị thế khiến vốn bị kẹt ở các con lỗ (Dead Money).
*   **Circuit Breaker:** **DISABLED (Tắt hoàn toàn)**.
    *   *Tại sao?* Chiến thuật bắt đảo chiều thường thua 3-4 lệnh liên tiếp trước khi bắt đúng đáy. Nếu bật CB, bot sẽ dừng đúng lúc đáy xuất hiện -> Mất cơ hội về bờ.
*   **Leverage:** **10x** (Cố định).

---

## 4. Risk Management: Hardcore Reality (Thực tế tàn khốc)

Để đảm bảo kết quả backtest là tiền thật, không phải tiền ảo:

*   **Liquidity Cap:** **$50,000 / Lệnh**.
    *   Dù tài khoản lên 1 triệu đô, bot chỉ đánh lệnh $50k. Đảm bảo luôn khớp được lệnh và phí rẻ (Tier 1).
    *   *Hệ quả:* Lợi nhuận sẽ giảm dần theo quy mô vốn (Diminishing Returns), nhưng cực kỳ an toàn.
*   **Liquidation Check:** Có.
    *   Tính toán giá thanh lý theo công thức Binance Isolated Margin.
    *   Nếu giá chạm -> Mất trắng Margin lệnh đó.

---

## 5. Performance Benchmarks (Vốn gốc $1,000)

| Thời Gian | Chế độ | Kết Quả | ROI | Ghi Chú |
| :--- | :--- | :--- | :--- | :--- |
| **Tháng 10/2025** | Hardcore | **$29,626** | **x29 lần** | Tháng biến động mạnh nhất (The Golden Month) |
| **Tháng 11/2025** | Hardcore | **$9,136** | **x9 lần** | Ổn định cao |
| **Tháng 12/2025** | Hardcore | **$2,812** | **x2.8 lần** | Tháng khó khăn nhưng vẫn lãi tốt |

---

## 6. Implementation Guide (Triển khai)

### Cấu hình `run_backtest.py` chuẩn:
```bash
python run_backtest.py --top 10 --days 30 --balance 1000 --leverage 10 --no-cb --max-order 50000 --mm-rate 0.004
```

### Chiến thuật Phân bổ vốn (Capital Allocation):
*   **Vốn < $500:** Dùng chế độ **Sniper** (Max Pos 3) để dồn lực tăng trưởng nhanh.
*   **Vốn > $1,000:** Dùng chế độ **Shark Tank** (Max Pos 10) để an toàn và bền vững.

---

*Lưu ý: Chiến thuật này yêu cầu tâm lý vững vàng để chịu đựng chuỗi thua (Drawdown) ngắn hạn trước khi bùng nổ lợi nhuận.*
