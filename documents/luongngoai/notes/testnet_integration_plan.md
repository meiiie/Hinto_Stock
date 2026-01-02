# 🌉 Binance Testnet Integration Plan (SOTA Blueprint)

> **Status:** Draft for Review
> **Objective:** Upgrade system from Internal Simulation to Real Exchange Connectivity (Testnet)
> **Target Date:** Jan 3, 2026

---

## 1. Architectural Strategy (Chiến lược Kiến trúc)

Chúng ta sẽ không "đập đi xây lại" mà áp dụng mẫu thiết kế **Adapter Pattern** để mở rộng khả năng kết nối.

### 1.1 Current State (AS-IS)
*   `PaperExchangeService` -> Gọi `SQLite DB` (Local).
*   `BinanceExchangeService` -> Gọi `Binance API` (Nhưng chưa có logic ký tên).

### 1.2 Target State (TO-BE)
*   **Universal API Client:** Nâng cấp `BinanceRestClient` để xử lý cả Public Request (Data) và Private Request (Order).
*   **Testnet Switch:** Thêm cấu hình `BINANCE_USE_TESTNET=True` để tự động điều hướng URL.

---

## 2. Technical Implementation Details

### 2.1 Upgrade `BinanceRestClient`
Class này cần thêm khả năng ký thực (Signing Capability) để gửi lệnh.

**Yêu cầu thay đổi:**
1.  **Dependency:** Thêm `hmac`, `hashlib` (Standard Lib).
2.  **Logic:**
    *   Hàm `_get_signature(params)`: Tạo chữ ký HMAC-SHA256.
    *   Hàm `_send_signed_request(method, endpoint, params)`: Tự động thêm `timestamp`, `signature` vào header.
3.  **Config:** Nhận `api_key` và `api_secret` từ Constructor.

### 2.2 Upgrade `BinanceExchangeService`
Đây là nơi "tay chân" hoạt động. Nó sẽ biến các lệnh trừu tượng thành request cụ thể.

**Các hàm cần implement:**
*   `create_order(symbol, side, quantity, price, type)`: Gửi lệnh Limit/Market.
*   `cancel_order(symbol, order_id)`: Hủy lệnh.
*   `get_account_balance()`: Lấy số dư USDT thực trên ví Futures.

### 2.3 Environment Configuration (`.env`)
Thêm các biến mới:
```bash
BINANCE_API_KEY=your_testnet_key
BINANCE_API_SECRET=your_testnet_secret
BINANCE_USE_TESTNET=True # Toggle switch
```

---

## 3. Risk Management & Safety (An toàn là trên hết)

Để tránh rủi ro "thao tác nhầm" trên tài khoản thật, hệ thống sẽ có các chốt chặn an toàn:

1.  **Testnet Flag Check:** Trước khi gửi bất kỳ lệnh nào, hệ thống sẽ in ra LOG cảnh báo rõ ràng: `⚠️ RUNNING IN TESTNET MODE`.
2.  **Asset Protection:** Chỉ trade các cặp `USDT` (Futures), không đụng vào Spot Wallet.
3.  **Hard Coded URL:** Nếu `BINANCE_USE_TESTNET=True`, URL sẽ bị fix cứng vào `https://testnet.binancefuture.com` trong code, không thể bị override bởi biến môi trường sai.

---

## 4. Execution Roadmap (Lộ trình thực thi)

| Bước | Mô tả | Thời gian ước tính |
| :--- | :--- | :--- |
| **1** | Nâng cấp `BinanceRestClient` (Auth logic) | 1 giờ |
| **2** | Implement `BinanceExchangeService` (Order logic) | 2 giờ |
| **3** | Unit Test (Mocking API) | 1 giờ |
| **4** | Integration Test (Gửi 1 lệnh lên Testnet) | 30 phút |

---

## 5. Decision Required (Cần duyệt)

Team cần xác nhận:
1.  Đồng ý nâng cấp `BinanceRestClient` hiện tại (thay vì tạo client mới) để tận dụng lại code cũ.
2.  Đã có tài khoản Binance Futures Testnet chưa? (Nếu chưa, cần đăng ký tại https://testnet.binancefuture.com).

*Prepared by AI Assistant - Hinto Stock Engineering*
