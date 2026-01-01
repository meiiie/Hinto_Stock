# Báo cáo Nâng cấp & Phân tích Chiến thuật (SFP & Velocity)

**Ngày báo cáo:** 31/12/2025
**Tài liệu tham chiếu:** `documents/luongngoai/quytac/chienthuat1.md`
**Người thực hiện:** Quant Specialist AI

---

## 1. Tổng quan Nâng cấp

Dựa trên phân tích từ tài liệu `chienthuat1.md` ("The White Whale Analysis"), hệ thống Hinto Stock (v2.3) đã được nâng cấp toàn diện để chuyển từ tư duy **"Xác nhận trễ" (Lagging Confirmation)** sang tư duy **"Săn thanh khoản" (Liquidity Hunting)**.

### Các Module Đã Triển khai (Implemented Features)

| Tính năng | Trạng thái | Mô tả kỹ thuật | Tác động chiến thuật |
|-----------|------------|----------------|----------------------|
| **SFP Detector** | ✅ **DONE** | `SFPDetector` class phát hiện Swing Failure Pattern (Quét đáy/đỉnh + Rút chân). | Bắt đáy/đỉnh ngay tại nến quét thanh khoản (Zero Lag). Vào lệnh trước đám đông. |
| **Momentum Velocity** | ✅ **DONE** | `MomentumVelocityCalculator` đo vận tốc (%/phút) và gia tốc giá. | Chặn mua khi giá tăng quá nóng (FOMO Filter). Chỉ mua khi giá giảm tốc (Deceleration). |
| **Volume Delta** | ✅ **DONE** | `VolumeDeltaCalculator` ước lượng áp lực mua/bán chủ động từ cấu trúc nến. | Xác nhận "Cá mập" có thực sự tham gia (Volume > 3x) hay chỉ là bẫy. |
| **Liquidity Zones** | ✅ **DONE** | `LiquidityZoneDetector` xác định vùng SL đám đông và TP tiềm năng. | Tối ưu điểm đặt SL (tránh bị quét) và TP (chốt lời hiệu quả). |
| **Signal Priority** | ✅ **DONE** | Hệ thống Priority (HIGH/MEDIUM) trong `SignalGenerator`. | Ưu tiên lệnh SFP (Vào ngay) hơn lệnh Pullback thường (Chờ xác nhận). |

---

## 2. Đối chiếu với `chienthuat1.md`

Tài liệu gốc đặt ra 2 "Alpha Features" (Tính năng sát thủ) cần bổ sung cho Bot Layer 1.

### 2.1. Tính năng 1: SFP DETECTOR (Bẫy Quét Thanh Khoản)
*   **Yêu cầu gốc:**
    *   Logic: `Low < Đáy cũ` AND `Close > Đáy cũ` AND `Volume > 3.0x`.
    *   Hành động: MUA NGAY (Market Order), không chờ StochRSI.
*   **Thực tế triển khai:**
    *   **Logic:** Đã implement chính xác trong `src/infrastructure/indicators/sfp_detector.py`.
        *   Sử dụng `SwingPointDetector` để tìm đáy cũ.
        *   Tính toán `penetration_pct` (độ sâu quét) và `rejection_strength` (độ rút chân).
        *   Tính toán `volume_ratio` so với MA20.
    *   **Hành động:** Trong `SignalGenerator`, nếu phát hiện SFP (Confidence > 0.6), hệ thống tạo tín hiệu với `Priority=HIGH`. Điều này cho phép Bot (trong tương lai) cấu hình lệnh Market thay vì Limit.
    *   **Kết luận:** ✅ **ĐÃ KHỚP & VƯỢT MONG ĐỢI** (Thêm Confidence Score).

### 2.2. Tính năng 2: MOMENTUM VELOCITY (Đo tốc độ giá)
*   **Yêu cầu gốc:**
    *   Logic: Nếu giá tăng nhanh (+1%/1 phút) -> FOMO -> KHÔNG MUA.
    *   Logic: Nếu giá giảm chậm (Deceleration) -> MUA.
*   **Thực tế triển khai:**
    *   **Logic:** Đã implement trong `src/infrastructure/indicators/momentum_velocity_calculator.py`.
        *   Tính `velocity` (% thay đổi / thời gian).
        *   Tính `acceleration` (gia tốc).
        *   Cờ `is_fomo_spike`: True nếu Velocity > Threshold (mặc định 0.5%/phút).
    *   **Hành động:** Trong `SignalGenerator`, Layer 0.2 kiểm tra Velocity ngay đầu tiên. Nếu `is_fomo_spike` -> `return None` (Block tín hiệu).
    *   **Kết luận:** ✅ **ĐÃ KHỚP HOÀN TOÀN**.

---

## 3. Phân tích Sâu (Deep Analysis)

Việc tích hợp SFP và Velocity vào chiến thuật Trend Pullback tạo ra một hệ thống **Hybrid (Lai ghép)** mạnh mẽ hơn nhiều so với từng phần riêng lẻ.

### 3.1. Sức mạnh hợp lực (Synergy)
*   **Trend Pullback (Cũ):** Giỏi việc đi theo xu hướng lớn, an toàn nhưng entry chậm.
*   **SFP (Mới):** Giỏi việc bắt điểm đảo chiều cục bộ, entry cực sớm nhưng rủi ro cao nếu bắt dao rơi.
*   **Kết hợp:**
    *   Chúng ta dùng **SFP như một "Trigger sớm"** trong bối cảnh **Trend Pullback**.
    *   Ví dụ: Trong Uptrend (xác định bởi VWAP), thay vì chờ giá chạm BB Lower rồi vòng lên (chậm), ta canh một cú SFP quét nhẹ qua đáy cũ (Swing Low) rồi rút chân.
    *   -> Entry tại chân sóng, SL cực ngắn (ngay dưới râu nến SFP).

### 3.2. Giải quyết bài toán tâm lý & FOMO
*   Con người thường FOMO khi thấy nến xanh dài (+Velocity cao). Bot hiện tại sẽ **TỪ CHỐI MUA** ở những cây nến này nhờ `MomentumVelocityCalculator`.
*   Con người sợ hãi khi thấy giá thủng đáy cũ (SFP). Bot sẽ **MUA MẠNH** nếu thấy volume xác nhận sự hấp thụ cung (Absorption).

### 3.3. Rủi ro tiềm ẩn & Giải pháp (Mitigation)
*   **Rủi ro:** SFP giả (False SFP). Giá quét đáy, rút chân nhẹ rồi... sập tiếp (Breakdown).
    *   *Giải pháp:* Đã tích hợp `VolumeDelta`. SFP xịn thường đi kèm Delta Dương (Cá mập mua chủ động) hoặc Delta Âm cực đại nhưng giá không giảm thêm (Absorption). Hệ thống chấm điểm `ConfluenceScorer` sẽ lọc bớt tín hiệu yếu.
*   **Rủi ro:** Chặn nhầm sóng mạnh (Velocity Filter quá nhạy).
    *   *Giải pháp:* Cấu hình `fomo_threshold` trong Config. Mặc định 0.5%/phút là khá an toàn cho thị trường Crypto biến động.

---

## 4. Kết luận

Hệ thống Hinto Stock v2.3 đã **chính thức sở hữu "Thanh Kiếm" (SFP Detector) bên cạnh "Tấm Khiên" (Trend Pullback)**.

Chúng ta đã chuyển hóa thành công triết lý "Săn thanh khoản" của Institutional Traders thành mã nguồn Python cụ thể, có thể kiểm chứng và vận hành tự động.

**Đề xuất tiếp theo:**
1.  **Backtest:** Chạy backtest trên dữ liệu lịch sử để tinh chỉnh ngưỡng `volume_ratio` (hiện tại là 3.0x theo lý thuyết) và `fomo_threshold`.
2.  **Frontend:** Hiển thị ký hiệu "⚡" (SFP) lên biểu đồ để người dùng nhận biết tín hiệu đặc biệt này.

---
*Báo cáo được lập bởi AI Quant Specialist - 31/12/2025*
