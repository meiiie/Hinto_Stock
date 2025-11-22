Chào bạn, quan sát của bạn rất chính xác và cực kỳ nhạy bén.

Bạn đang nhìn thấy một "quả bom nổ chậm" trong hệ thống. Vấn đề bạn chỉ ra không phải là "lỗi vặt", mà là lỗ hổng nghiêm trọng trong **Logic Quản Lý Vòng Đời Lệnh (Order Lifecycle Management)**.

Là Chief Architect, tôi nhìn vào ảnh và thấy ngay 2 vấn đề chí mạng cần xử lý ngay lập tức trước khi hệ thống này có thể chạy thật:

### 1. PHÂN TÍCH ẢNH & VẤN ĐỀ

#### ❌ Vấn đề 1: "Zombie Orders" (Lệnh thây ma) - *Đúng như bạn lo ngại*
*   **Hiện tượng:** Trong bảng "Open Orders" có tới **5 lệnh SHORT** đang chờ cùng lúc.
*   **Rủi ro:** Đây là các lệnh cũ do Bot sinh ra ở các nến trước nhưng chưa khớp.
    *   Nếu thị trường giật mạnh lên (Spike) -> Cả 5 lệnh này có thể khớp cùng lúc.
    *   **Hậu quả:** Bạn sẽ vào một vị thế Short khổng lồ đúng lúc giá đang tăng mạnh (Trend đảo chiều). Đây là cách nhanh nhất để cháy tài khoản.
*   **Nguyên nhân:** Thiếu cơ chế **Hủy lệnh cũ (Cancellation Logic)** hoặc **Time-to-Live (TTL)**. Một tín hiệu Short ở nến 15m trước chỉ có giá trị trong 15m đó. Sang nến mới, nếu chưa khớp thì phải HỦY NGAY.

#### ❌ Vấn đề 2: Over-leveraging (Vượt quá vốn) - *Lỗi logic nghiêm trọng*
*   **Bằng chứng:**
    *   Wallet Balance: **~$10,549**
    *   Open Positions: Có 2 lệnh, mỗi lệnh Margin ~$10,022. Tổng cộng **~$20,000**.
    *   Available: $0.00.
*   **Phân tích:** Bạn đang chơi Spot/Futures 1x, tức là có 10 đồng chỉ được mua 10 đồng. Tại sao hệ thống lại cho phép mở vị thế lên tới 20 đồng (Gấp đôi vốn)?
*   **Nguyên nhân:** Hệ thống kiểm tra số dư bị sai (Race Condition) hoặc không trừ Locked Margin của lệnh đầu tiên khi xét duyệt lệnh thứ 2.

---

### 2. YÊU CẦU BÁO CÁO TỪ TEAM

Để sửa dứt điểm, tôi cần team của bạn cung cấp một báo cáo tập trung vào **Luồng Quản Lý Lệnh**. Bạn hãy gửi yêu cầu này cho họ:

***

**YÊU CẦU BÁO CÁO: QUY TRÌNH QUẢN LÝ VÒNG ĐỜI LỆNH (ORDER LIFECYCLE)**

**To:** Antigravity (Lead Developer)
**From:** Project Manager
**Subject:** RÀ SOÁT CƠ CHẾ HỦY LỆNH & QUẢN LÝ MARGIN

**Mô tả vấn đề:**
Trên Dashboard hiện tại xuất hiện tình trạng "Order Stacking" (5 lệnh chờ cùng lúc) và "Over-Margin" (Mở vị thế gấp đôi vốn thực tế).

**Yêu cầu Team giải trình và đề xuất giải pháp cho các câu hỏi sau:**

**1. Cơ chế Hủy Lệnh (Cancellation Policy)**
*   Hiện tại, khi sinh ra tín hiệu mới, hệ thống có kiểm tra và hủy các lệnh PENDING cũ của cùng cặp tiền không?
*   Hệ thống có cơ chế **TTL (Time-To-Live)** không? (Ví dụ: Lệnh Limit chỉ tồn tại trong 3 cây nến, sau đó tự hủy).
*   *Yêu cầu:* Cần một cơ chế: **"New Signal cancels Old Pending Orders"**. Mỗi thời điểm chỉ nên tồn tại tối đa 1 lệnh Pending cho mỗi chiều.

**2. Cơ chế Gộp Vị Thế (Position Merging)**
*   Tại sao cùng là cặp `BTCUSDT` chiều `SHORT` mà lại tách thành 2 dòng Positions riêng biệt?
*   Chúng ta đang dùng chế độ **Hedge Mode** hay **One-way Mode**? (Khuyến nghị: One-way Mode - Các lệnh Short khớp thêm sẽ gộp vào vị thế cũ và tính lại giá Entry trung bình).

**3. Kiểm soát Margin (Margin Check)**
*   Tại sao với vốn $10,500 lại mở được 2 lệnh tổng $20,000 (Leverage thực tế đang là 2x dù hiển thị 1x)?
*   Code kiểm tra `Available Balance` đang nằm ở đâu? Trước hay sau khi trừ `Pending Order Margin`?

***

### 3. LỜI KHUYÊN NHANH CHO BẠN

Trong lúc chờ báo cáo, đây là giải pháp kỹ thuật ("thuốc giải") mà tôi dự kiến sẽ chỉ đạo team làm:

1.  **Quy tắc "1-1-1":** Tại một thời điểm, với 1 cặp coin, chỉ được phép có:
    *   **1 Position** (Vị thế đang chạy).
    *   **1 Pending Order** (Lệnh đang chờ).
    *   Nếu có tín hiệu mới -> **Hủy lệnh chờ cũ** -> Đặt lệnh chờ mới.
2.  **Cơ chế Timeout:** Mỗi lệnh Limit gán một `expiry_time` (ví dụ: 45 phút ~ 3 nến). Quá giờ không khớp -> Tự hủy.
3.  **Sửa lỗi Margin:** Khi đặt lệnh Pending $10,000, ngay lập tức `Available Balance` phải về 0. Lệnh thứ 2 sẽ bị từ chối ngay từ vòng gửi xe.

Bạn hãy gửi yêu cầu báo cáo trên cho team nhé. Đây là bước tinh chỉnh cuối cùng để hệ thống "khôn" hơn và an toàn hơn.