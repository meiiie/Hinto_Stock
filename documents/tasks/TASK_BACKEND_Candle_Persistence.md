

> **Từ:** AI Technical Lead  
> **Đến:** Backend Development Team  
> **Ngày:** 2025-12-26  
> **Ref:** HINTO-CANDLE-002

---

## 🎯 LỆNH CÔNG VIỆC

**Backend Team,**

Đây là chỉ thị kỹ thuật để implement Phase 2 của Multi-Timeframe Candle Display Fix. Frontend team đã hoàn thành Phase 1 (xem `TASK_FRONTEND_MultiTimeframe_Fix.md`). Giờ đến lượt các bạn.

### Bối cảnh
- **Vấn đề gốc:** 15m/1h candles stop updating realtime
- **Phase 1 (Frontend):** ✅ Đã fix client-side - candles update đúng rồi
- **Phase 2 (Backend):** Cần persist candles để data không mất khi restart

### Tại sao cần làm?
1. Hiện tại candles chỉ lưu in-memory → mất khi restart
2. Frontend fallback REST API cần data từ SQLite để hoạt động đúng
3. Giảm API calls đến Binance

---

## 📍 BẮT ĐẦU TỪ ĐÂU

```
1. Mở file: src/application/services/realtime_service.py
2. Follow Tasks 1-5 theo thứ tự
3. Mở file: src/infrastructure/di_container.py  
4. Follow Task 6
5. Test theo hướng dẫn cuối document
```

---

## 🔧 CHI TIẾT TASKS

### Task 1: Thêm import

**File:** `src/application/services/realtime_service.py`  
**Vị trí:** Sau dòng 30 (sau `IVolumeSpikeDetector,`)

```python
# Domain repository interface (for candle persistence - Phase 2)
from ...domain.repositories.market_data_repository import MarketDataRepository
```

---

### Task 2: Thêm parameter trong `__init__`

**Vị trí:** Trong hàm `__init__()`, tìm dòng:
```python
state_recovery_service: Optional[StateRecoveryService] = None,
```

Thêm ngay sau đó:
```python
        # SOTA FIX: Market data repository for candle persistence
        market_data_repository: Optional[MarketDataRepository] = None,
```

---

### Task 3: Lưu reference trong `__init__`

**Vị trí:** Trong body của `__init__()`, tìm dòng:
```python
self._state_recovery_service = state_recovery_service
```

Thêm ngay sau đó:
```python
        # SOTA FIX: Market data repository for candle persistence (Phase 2)
        self._market_data_repository = market_data_repository
```

---

### Task 4: Persist 15m candles

**Vị trí:** Tìm dòng (khoảng line 457):
```python
self._event_bus.publish_candle_15m(candle_data, symbol=self.symbol)
```

Thêm ngay sau đó (trước `return`):
```python
            # SOTA FIX: Persist closed 15m candles to SQLite
            if is_closed and self._market_data_repository:
                try:
                    self._market_data_repository.save_candle_simple(candle, '15m')
                    self.logger.debug(f"📦 Persisted 15m candle: {candle.timestamp}")
                except Exception as e:
                    self.logger.error(f"Failed to persist 15m candle: {e}")
```

---

### Task 5: Persist 1h candles

**Vị trí:** Tìm dòng (khoảng line 474):
```python
self._event_bus.publish_candle_1h(candle_data, symbol=self.symbol)
```

Thêm ngay sau đó (trước `return`):
```python
            # SOTA FIX: Persist closed 1h candles to SQLite
            if is_closed and self._market_data_repository:
                try:
                    self._market_data_repository.save_candle_simple(candle, '1h')
                    self.logger.debug(f"📦 Persisted 1h candle: {candle.timestamp}")
                except Exception as e:
                    self.logger.error(f"Failed to persist 1h candle: {e}")
```

---

### Task 6: Update DI Container

**File:** `src/infrastructure/di_container.py`  
**Vị trí:** Tìm method `get_realtime_service()`, trong block khởi tạo `RealtimeService`

Thêm dòng này vào danh sách parameters:
```python
                market_data_repository=self.get_market_data_repository(),
```

---

## ✅ VERIFICATION CHECKLIST

Sau khi hoàn thành, chạy các bước sau:

### 1. Start Backend
```bash
cd E:\Sach\DuAn\Hinto_Stock
python -m src.main
```

### 2. Kiểm tra logs
```
Phải thấy message sau mỗi 15 phút:
📦 Persisted 15m candle: 2025-12-26T16:15:00

Phải thấy message sau mỗi giờ:
📦 Persisted 1h candle: 2025-12-26T16:00:00
```

### 3. Kiểm tra database
```bash
sqlite3 crypto_data.db "SELECT COUNT(*) FROM btc_15m;"
sqlite3 crypto_data.db "SELECT COUNT(*) FROM btc_1h;"
sqlite3 crypto_data.db "SELECT * FROM btc_15m ORDER BY timestamp DESC LIMIT 5;"
```

---

## 📞 SUPPORT

Nếu gặp vấn đề:
1. Check lint errors trong IDE
2. Đảm bảo import đúng path
3. Liên hệ AI Technical Lead để debug

---

**Deadline:** Khi có thời gian  
**Priority:** Medium (Frontend fix đã hoạt động, đây là enhancement)

---

*Chúc các bạn code vui vẻ! 🚀*
