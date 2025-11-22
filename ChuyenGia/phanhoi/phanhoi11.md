Chào bạn, bạn có "đôi mắt của một con đại bàng" (Eagle Eye). Phát hiện của bạn hoàn toàn chính xác và cực kỳ quan trọng.

**VẤN ĐỀ: "Over-leveraging" (Vượt quá vốn thực tế).**
Với vốn $10,000, việc hệ thống cho phép mở 3 lệnh tổng trị giá ~$15,300 (Gấp 1.5 lần vốn) trong khi chúng ta đang định hướng là **Spot Trading (Không đòn bẩy)** là một lỗi logic nghiêm trọng trong module quản lý vốn (`PaperTradingService`).

Điều này xảy ra do **Lỗi tính toán "Locked Balance" (Vốn bị phong tỏa)**. Khi một lệnh `PENDING` được đặt ra, số tiền tương ứng phải bị "khóa" lại, không được dùng cho lệnh khác. Có vẻ hệ thống đang không trừ số tiền này đi khi xét duyệt lệnh tiếp theo.

Để giải quyết triệt để và rà soát lại toàn bộ hệ thống trước khi chạy tiếp, tôi đã soạn thảo mẫu **Báo Cáo Kiểm Toán Kỹ Thuật (Technical Audit Report)** dưới đây. Bạn hãy gửi yêu cầu này cho Team Lead.

---

### 📋 YÊU CẦU BÁO CÁO: KIỂM TOÁN PAPER TRADING ENGINE

**To:** Development Team
**From:** Project Manager
**Subject:** YÊU CẦU BÁO CÁO RÀ SOÁT LỖI QUẢN LÝ VỐN & TRẠNG THÁI HỆ THỐNG

**Mô tả vấn đề:**
Trên Dashboard hiện tại đang hiển thị 3 lệnh Active với tổng giá trị (Size) ~ $15,300. Trong khi Balance chỉ có $10,150.
=> Hệ thống đang cho phép sử dụng vốn khống (Leverage > 1.0) hoặc không khóa vốn khi đặt lệnh Pending. Điều này vi phạm nguyên tắc quản lý rủi ro.

**Yêu cầu Team thực hiện rà soát và nộp báo cáo chi tiết theo cấu trúc sau:**

#### 1. Báo cáo Logic Quản Lý Vốn (Capital Logic Audit)
*   **Hiện tại:** Code đang kiểm tra số dư như thế nào trước khi đặt lệnh? (Copy đoạn code `check_balance` trong `PaperTradingService`).
*   **Lỗi:** Tại sao lệnh thứ 2 và thứ 3 vẫn được chấp nhận khi lệnh 1 (Pending) đã chiếm $5,000 vốn?
*   **Locked Balance:** Hệ thống có khái niệm `locked_balance` (tiền ký quỹ cho lệnh chờ) chưa? Nếu có, tại sao nó không hoạt động?

#### 2. Báo cáo Cấu hình Rủi Ro (Risk Config)
*   **Position Sizing:** Công thức tính Volume hiện tại là gì? (Fixed Amount, % Balance, hay Risk based?).
*   **Max Positions:** Cấu hình tối đa bao nhiêu lệnh?
*   **Leverage:** Hệ thống có đang vô tình cho phép margin không?

#### 3. Báo cáo Dữ Liệu Tồn đọng (Data Integrity)
*   **Mock Data:** Tại sao trong *Trade History* (Dòng 4) vẫn còn lệnh test cũ "BUY BTC giá $50,000"? Tại sao lệnh SQL xóa dữ liệu rác được yêu cầu trước đó chưa được thực thi hoặc chưa hiệu quả?

#### 4. Đề xuất Giải pháp Khắc phục (Fix Plan)
*   Nêu rõ giải pháp kỹ thuật để ngăn chặn việc đặt lệnh vượt quá số dư khả dụng (`Available Balance = Total - Locked`).
*   Thời gian dự kiến sửa lỗi.

---

### GÓC NHÌN CHUYÊN GIA (Dành riêng cho bạn)

Trong khi chờ báo cáo, tôi dự đoán **Nguyên nhân gốc rễ (Root Cause)** nằm ở đoạn code logic này:

```python
# Logic SAI thường gặp:
if current_balance > order_cost:
    place_order()
# Sai vì: current_balance vẫn là $10k dù đã treo 2 lệnh chờ $5k.

# Logic ĐÚNG phải là:
available_balance = current_balance - sum(pending_orders_value)
if available_balance > order_cost:
    place_order()
```

Bạn hãy gửi yêu cầu báo cáo trên cho team. Sau khi nhận được báo cáo giải trình của họ, tôi sẽ đánh giá xem giải pháp sửa lỗi của họ có triệt để hay không và chúng ta sẽ lên kế hoạch tiếp theo.