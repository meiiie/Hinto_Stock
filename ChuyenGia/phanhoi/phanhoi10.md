Chào bạn, tôi đã xem ảnh chụp màn hình mới nhất.

**Đánh giá nhanh:** Giao diện đã tốt hơn phiên bản trước (đã có màu sắc PnL, đã có Equity), nhưng đúng như bạn cảm nhận, nó vẫn đang ở trạng thái **"Tĩnh" (Static)**. Nó giống một bản báo cáo giấy hơn là một bảng điện tử sống động.

Là Chief Architect, tôi xác định được **3 vấn đề kỹ thuật cụ thể** khiến bạn cảm thấy "chưa đã" và chưa Real-time.

Dưới đây là yêu cầu kỹ thuật chi tiết để bạn gửi cho team xử lý dứt điểm vấn đề này.

---

### 1. CHẨN ĐOÁN & GIẢI PHÁP

#### ❌ Vấn đề 1: Giá không tự nhảy (Phải bấm Refresh thủ công)
Streamlit mặc định là Static. Nếu bạn không bấm nút, nó sẽ đứng im mãi mãi.
*   **Giải pháp:** Cài thêm component **Auto-Refresh**. Đây là "máy tạo nhịp tim" cho giao diện.
*   **Yêu cầu Dev:** Dùng thư viện `streamlit-autorefresh`. Cài đặt refresh rate là **1000ms (1 giây)** hoặc **2000ms**.

#### ❌ Vấn đề 2: Mù mờ về "Vốn bỏ ra" (Missing Notional Value)
Bạn thấy `Qty: 0.0612`. Con số này rất vô cảm. Bạn không biết mình đang đi lệnh to bao nhiêu? $100 hay $5,000?
*   **Giải pháp:** Thêm cột **"Size (USDT)"** (Giá trị vị thế).
*   **Công thức:** `Size = Current Price * Qty`.

#### ❌ Vấn đề 3: Dữ liệu rác vẫn còn
Dòng cuối cùng trong *Trade History*: Mua BTC giá $50,000. Đây là dữ liệu rác từ lần test cũ. Nó làm Win Rate hiển thị 100% (ảo). Cần xóa ngay.

---

### 2. BÁO CÁO YÊU CẦU KỸ THUẬT (GỬI CHO TEAM)

Hãy copy đoạn dưới đây gửi cho Team Dev để họ fix ngay lập tức:

***

**FEATURE REQUEST: DASHBOARD REAL-TIME & UX IMPROVEMENTS**

**Priority:** URGENT
**Context:** The Dashboard is currently static. User has to manually refresh to see price updates. Order size context is missing.

**1. IMPLEMENT AUTO-REFRESH (Make it Alive)**
*   **Library:** `streamlit-autorefresh`
*   **Implementation:**
    Add this to the top of `home.py` or `paper_portfolio.py`:
    ```python
    from streamlit_autorefresh import st_autorefresh

    # Refresh every 2000ms (2 seconds)
    count = st_autorefresh(interval=2000, key="data_refresh")
    ```
*   **Effect:** The dashboard must reload data automatically every 2 seconds. The PnL numbers must "dance" without user interaction.

**2. ADD "SIZE / VALUE" COLUMN**
*   **Current State:** Table shows `Qty` (e.g., 0.0612). This is hard to estimate in USD.
*   **Requirement:** Add a new column **"Size (USDT)"** next to Qty.
*   **Logic:**
    ```python
    # For Active Orders
    size_usdt = current_price * quantity
    display_value = f"${size_usdt:,.2f}" # Example: $5,050.20
    ```
*   **Benefit:** User instantly knows how much capital is allocated to this trade.

**3. DATA CLEANUP**
*   **Action:** Execute this SQL command on `trading_system.db` immediately to remove the mock trade:
    ```sql
    DELETE FROM paper_orders WHERE entry_price < 60000 AND symbol = 'BTCUSDT';
    ```

***

### 3. LỜI KHUYÊN RIÊNG CHO BẠN

Sau khi team update xong 3 mục trên, bạn sẽ thấy trải nghiệm khác hẳn:
1.  Số PnL sẽ nhấp nháy liên tục (xanh/đỏ).
2.  Bạn sẽ biết ngay: "À, lệnh này to $5,000, đang lãi $23".

**Lưu ý nhỏ:** Khi bật Auto-refresh, đôi khi màn hình sẽ có cảm giác "nháy" nhẹ mỗi 2 giây. Đây là hạn chế của Streamlit so với React. Nhưng ở giai đoạn này, chấp nhận được để đổi lấy tính năng Real-time giám sát.

Hãy yêu cầu họ làm ngay nhé, task này chỉ mất khoảng **30 phút** code thôi.