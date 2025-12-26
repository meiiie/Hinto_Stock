# 📋 TECHNICAL DIRECTIVE: Phase 3 API Optimization

> **Từ:** AI Technical Lead  
> **Đến:** Backend Development Team  
> **Ngày:** 2025-12-26  
> **Ref:** HINTO-CANDLE-003  
> **Priority:** LOW (Enhancement)

---

## 🎯 MỤC TIÊU

Implement hybrid data source: Query SQLite first, fallback Binance REST nếu không đủ data.

**Lợi ích:**
- Giảm API calls đến Binance
- Faster response (local SQLite vs network)
- Data không mất khi Binance down tạm thời

---

## 📍 BẮT ĐẦU TỪ ĐÂU

```
1. Mở file: src/api/dependencies.py
2. Thêm get_market_data_repository() function
3. Mở file: src/api/routers/market.py
4. Update get_market_history() endpoint
5. Test
```

---

## 🔧 TASKS

### Task 1: Thêm dependency function

**File:** `src/api/dependencies.py`  
**Vị trí:** Sau `get_signal_lifecycle_service()` function

```python
@lru_cache()
def get_market_data_repository():
    """
    SOTA Phase 3: Get MarketDataRepository for hybrid data source.
    SQLite first, Binance fallback.
    """
    container = get_container()
    return container.get_market_data_repository()
```

---

### Task 2: Update market history endpoint

**File:** `src/api/routers/market.py`  
**Thêm import ở đầu file:**

```python
from src.api.dependencies import get_market_data_repository
from src.infrastructure.persistence.sqlite_market_data_repository import SQLiteMarketDataRepository
```

**Update function `get_market_history` (khoảng line 172):**

```python
@router.get("/history/{symbol}")
async def get_market_history(
    symbol: str,
    timeframe: str = Query(default='15m', pattern='^(1m|15m|1h)$'),
    limit: int = Query(default=100, ge=1, le=1000),
    service: RealtimeService = Depends(get_realtime_service),
    repo: SQLiteMarketDataRepository = Depends(get_market_data_repository)
):
    """
    Get historical market data with hybrid data source.
    
    SOTA Phase 3: SQLite first, Binance fallback.
    """
    # Step 1: Try SQLite first
    try:
        sqlite_candles = repo.get_latest_candles(timeframe, limit)
        if len(sqlite_candles) >= limit * 0.8:  # 80% threshold
            logger.debug(f"SQLite hit: {len(sqlite_candles)} candles for {timeframe}")
            return [
                {
                    'time': int(c.candle.timestamp.timestamp()),
                    'open': c.candle.open,
                    'high': c.candle.high,
                    'low': c.candle.low,
                    'close': c.candle.close,
                    'volume': c.candle.volume,
                }
                for c in sqlite_candles
            ]
    except Exception as e:
        logger.warning(f"SQLite query failed: {e}")
    
    # Step 2: Fallback to service (Binance REST)
    logger.debug(f"SQLite miss, falling back to Binance for {timeframe}")
    return service.get_historical_data_with_indicators(timeframe, limit)
```

---

### Task 3: Update market_router endpoint (optional)

**File:** `src/api/routers/market.py`  
**Function:** `get_market_history_rest` (line 226)

Apply same hybrid logic.

---

## ✅ VERIFICATION

```bash
# Start backend
python -m src.main

# Wait for some candles to be persisted (15+ minutes)

# Test history endpoint
curl "http://127.0.0.1:8000/ws/history/btcusdt?timeframe=15m&limit=10"

# Check logs for "SQLite hit" vs "SQLite miss"
```

---

## 📎 NOTES

- Phase 3 là **LOW priority** - Phase 1 và 2 đã fix được vấn đề chính
- Có thể skip nếu không cần optimize performance
- SQLite threshold 80% để tránh edge case

---

*Optional enhancement - implement khi có thời gian.*
