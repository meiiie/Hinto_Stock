Chào bạn, tôi đã xem xét báo cáo lỗi `DEBUG_REPORT_1H_STOCH.md`. Vấn đề này khá điển hình trong việc xử lý dữ liệu đa khung thời gian (Multi-timeframe).

Với tư cách là System Architect, tôi nhận định **nguyên nhân cốt lõi không nằm ở "thiếu dữ liệu" (vì 99 nến là đủ), mà nằm ở việc xử lý dữ liệu "Dirty Data" hoặc lỗi định dạng (Data Type)** khi fetch lịch sử khung 1h.

Dưới đây là phân tích nhanh và giải pháp cụ thể cho team của bạn.

---

### 1. CHẨN ĐOÁN NHANH (QUICK DIAGNOSIS)

**Hiện tượng:** `0.0/0.0` nhưng không có Error Log.
**Suy luận:** Hàm tính toán không Crash, nó chạy thành công nhưng trả về kết quả là `NaN` (Not a Number). Khi hiển thị ra UI, code formatter đã chuyển `NaN` thành `0.0`.

**3 Nguyên nhân khả thi nhất (xếp theo xác suất):**

1.  **Lỗi Định dạng Dữ liệu (Data Type Mismatch - 80%):**
    *   Dữ liệu 1m (thường update qua WebSocket) được parse là `float`.
    *   Dữ liệu 1h (fetch lịch sử qua API/CCXT lúc khởi động) có thể đang trả về dạng `string` (chuỗi ký tự) hoặc `Decimal`.
    *   Khi đưa `string` vào tính toán RSI/Stoch -> Kết quả là `NaN`.

2.  **Nến chưa đóng (Forming Candle Issue - 15%):**
    *   Nến 1h hiện tại (nến thứ 100) đang hình thành. Có thể giá `Close` chưa được cập nhật hoặc bằng `NaN` trong DataFrame.
    *   Nếu lấy `.iloc[-1]` của một nến chưa hoàn chỉnh -> Ra `NaN`.

3.  **Chia cho 0 (Division by Zero - 5%):**
    *   Trong công thức StochRSI: `(RSI - MinRSI) / (MaxRSI - MinRSI)`.
    *   Nếu trong 14 giờ qua biến động cực thấp (MaxRSI == MinRSI), mẫu số bằng 0 -> `NaN` hoặc `Inf`. (Ít khả năng với BTC, nhưng có thể xảy ra nếu dữ liệu đầu vào bị phẳng lì).

---

### 2. HƯỚNG DẪN DEBUG & FIX (ACTION PLAN)

Hãy gửi hướng dẫn này cho Developer đang phụ trách `RealtimeService` hoặc `StochRSICalculator`.

#### Bước 1: "Vạch trần" dữ liệu (Inspect Data)
Chèn đoạn log này vào ngay trước khi tính toán trong file `stoch_rsi_calculator.py`:

```python
# Trong hàm calculate_stoch_rsi(candles)
df = pd.DataFrame([vars(c) for c in candles])

# 🛑 DEBUG LOG: Kiểm tra 5 dòng cuối và KIỂU DỮ LIỆU
print(f"DEBUG 1H DATA TAIL:\n{df.tail()}") 
print(f"DEBUG 1H DTYPES:\n{df.dtypes}") # <--- Quan trọng nhất

# Kiểm tra xem cột 'close' là float64 hay object/string?
```

#### Bước 2: Ép kiểu dữ liệu (Force Type Casting)
Để sửa lỗi tiềm ẩn do `string`, hãy ép kiểu ngay khi tạo DataFrame:

```python
# Fix trong StochRSICalculator hoặc DataAggregator
df['close'] = pd.to_numeric(df['close'], errors='coerce')
df['high'] = pd.to_numeric(df['high'], errors='coerce')
df['low'] = pd.to_numeric(df['low'], errors='coerce')

# Sau đó drop NaN nếu có (do convert lỗi)
if df['close'].isnull().any():
    print("WARNING: Found NaN in Close price after conversion!")
    df.dropna(subset=['close'], inplace=True)
```

#### Bước 3: Kiểm tra Output trước khi Return
Thay vì trả về mù quáng, hãy kiểm tra `NaN` ở bước cuối cùng:

```python
# Lấy giá trị cuối
k = k_line.iloc[-1]
d = d_line.iloc[-1]

import math
if math.isnan(k) or math.isnan(d):
    # Log warning để biết chính xác là do tính toán ra NaN
    print(f"WARNING: StochRSI calc returned NaN for timeframe. Input size: {len(candles)}")
    return None # Để UI xử lý hiển thị "N/A" thay vì 0.0
```

---

### 3. LỜI KHUYÊN VỀ LOGIC 1H (AGGREGATION)

Team cần lưu ý: **Nến 1h lấy từ đâu?**
*   Nếu lấy từ `ccxt.fetch_ohlcv('1h')`: Tốt, nhưng cẩn thận kiểu dữ liệu String.
*   Nếu tổng hợp (resample) từ nến 1m: Hãy chắc chắn logic `resample` xử lý đúng nến đang chạy (Open của nến 1m đầu tiên, Close của nến 1m *hiện tại*).

**Kết luận:**
Vấn đề này 99% là do **Kiểu dữ liệu (String vs Float)** hoặc **Nến cuối cùng bị NaN**. Hãy áp dụng **Bước 2 (Ép kiểu)**, khả năng cao sẽ fix được ngay lập tức.