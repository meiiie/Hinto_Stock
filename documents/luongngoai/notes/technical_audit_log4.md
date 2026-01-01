# 🛡️ Technical Audit Report: Incident LOG-004
**Date:** 2026-01-01
**Subject:** Critical Runtime Failures in Signal Generation Pipeline
**Status:** 🔴 CRITICAL (System Stability Risk)
**Auditor:** Quant Specialist AI (Chief Architect Role)

---

## 1. Executive Summary
Hệ thống Hinto Stock v2.3 (Volume Upgrade) đã gặp lỗi nghiêm trọng (Critical Crash) ngay tại thời điểm khởi chạy Runtime (`2026-01-01 00:20:56`). 
Mặc dù các Unit Test đã thông qua (100% Pass), hệ thống thực tế đã sụp đổ. Điều này chỉ ra lỗ hổng lớn trong quy trình **Integration Testing** và **Architectural Consistency**.

## 2. Root Cause Analysis (Deep Dive)

### 2.1. Issue #1: The "Unbound Local" Spaghetti
**Error:** `UnboundLocalError: cannot access local variable 'indicators' where it is not associated with a value`
*   **Location:** `SignalGenerator.generate_signal` line 336.
*   **Analysis:**
    *   Chúng ta đã chèn logic `Volume Delta` (Feature mới) vào *giữa* hàm.
    *   Logic này cố gắng ghi dữ liệu vào biến `indicators` (`indicators['volume_delta'] = ...`).
    *   Tuy nhiên, biến `indicators` lại được khởi tạo *sau đó* (ở dòng code cũ phía dưới).
*   **Architectural Flaw:** Hàm `generate_signal` đang trở thành một "God Method". Việc thêm tính năng mới bằng cách "chèn dòng lệnh" vào giữa luồng xử lý cũ mà không quy hoạch lại luồng dữ liệu (Data Flow) là nguyên nhân chính.

### 2.2. Issue #2: Interface Contract Violation
**Error:** `AttributeError: 'ATRCalculator' object has no attribute 'calculate'`
*   **Location:** `LiquidityZoneDetector.detect_zones`.
*   **Analysis:**
    *   Module mới (`LiquidityZoneDetector`) giả định `ATRCalculator` có phương thức chuẩn `calculate()`.
    *   Module cũ (`ATRCalculator`) thực tế cài đặt phương thức `calculate_atr()`.
*   **Architectural Flaw:** Thiếu sự chuẩn hóa Interface (Standardized Interface). Trong các hệ thống lớn (như Binance/HFT Systems), mọi Calculator phải tuân thủ nghiêm ngặt một Interface chung (ví dụ `ICalculator.calculate(data) -> Result`).

---

## 3. Action Plan for Dev Team (SOTA Standards)

Không sửa chắp vá (No Band-aid Fixes). Chúng ta sẽ thực hiện Refactoring để ngăn chặn vĩnh viễn các lỗi tương tự.

### ✅ Step 1: Centralized Data Preparation (Pattern: Context Object)
Tách biệt hoàn toàn việc **Tính toán** và **Logic**.
Trong `SignalGenerator`, tạo một phương thức private `_prepare_market_context(candles)` để tính toán *tất cả* các chỉ báo trước.

```python
# PROPOSED STRUCTURE (SOTA)
def generate_signal(self, candles, symbol):
    # 1. Data Preparation Phase (Safe Zone)
    # Tính toán TOÀN BỘ indicator ở đây, xử lý try/catch tập trung.
    context = self._prepare_market_context(candles) 
    if not context.is_valid:
        return None

    # 2. Logic Phase (Pure Logic)
    # Chỉ đọc dữ liệu từ context, không tính toán gì thêm.
    # Không còn rủi ro UnboundLocalError.
    
    # Layer 0: Regime
    if self.regime_detector.check(context) == BLOCK: return None
    
    # Layer 0.5: SFP
    if self.sfp_detector.check(context): return SFP_SIGNAL
    
    # Layer 1: Trend
    return self._check_trend_strategy(context)
```

### ✅ Step 2: Strict Interface Compliance
*   **Yêu cầu:** Sửa ngay lập tức `LiquidityZoneDetector` để gọi đúng `calculate_atr`.
*   **Long-term:** Refactor toàn bộ các Calculator (`ATR`, `ADX`, `RSI`...) để implement một Interface chung `IIndicator`.
    *   Method: `calculate(candles) -> Result`
    *   Property: `value` (lấy giá trị chính)

### ✅ Step 3: Integration Test Harness (The Missing Link)
Tạo một script `scripts/tests/verify_runtime_integrity.py`.
Script này phải:
1.  Khởi tạo `DIContainer` thật (không phải Mock).
2.  Lấy `RealtimeService`.
3.  Load 500 nến thật từ DB hoặc File.
4.  Feed nến vào hệ thống và bắt buộc nó phải chạy hết flow `generate_signal` mà không crash.
5.  **Luật:** Không bao giờ merge code nếu script này chưa pass.

---

## 4. Implementation Directives

Team Dev (AI Assistant) tiến hành thực thi ngay các sửa lỗi sau:

1.  **FIX `SignalGenerator`:** Di chuyển khối khởi tạo `indicators = {}` lên ĐẦU hàm `generate_signal`, ngay sau khi check `candles`. Đảm bảo biến này luôn tồn tại.
2.  **FIX `LiquidityZoneDetector`:** Đổi `atr_calculator.calculate` thành `atr_calculator.calculate_atr`.
3.  **VERIFY:** Chạy script Integration Test (nếu chưa có thì tạo nhanh một bản test integration thủ công) để đảm bảo log không còn báo lỗi đỏ.

---
*Reported by Chief Architect AI - 2026-01-01*
