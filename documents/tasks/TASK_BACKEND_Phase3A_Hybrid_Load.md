# 📋 TECHNICAL DIRECTIVE: Phase 3A Hybrid Load

> **Từ:** AI Technical Lead  
> **Đến:** Backend Development Team  
> **Ngày:** 2025-12-26  
> **Ref:** HINTO-CANDLE-003A  
> **Priority:** HIGH

---

## 🎯 MỤC TIÊU

Implement SOTA Hybrid Data Layer: SQLite first, Binance fallback.

**Vấn đề hiện tại:**
- SQLite SAVES candles nhưng `_load_historical_data()` KHÔNG READ từ SQLite
- Mỗi lần restart luôn gọi Binance API (chậm, dependency external)

---

## 📍 BẮT ĐẦU TỪ ĐÂU

```
1. Mở file: src/application/services/realtime_service.py
2. Thêm helper _load_candles_hybrid() method
3. Update _load_historical_data() để dùng hybrid method
4. Test
```

---

## 🔧 TASKS

### Task 1: Thêm `_load_candles_hybrid` helper method

**File:** `src/application/services/realtime_service.py`  
**Vị trí:** Thêm TRƯỚC method `_load_historical_data()` (khoảng line 195)

```python
    def _load_candles_hybrid(self, timeframe: str, limit: int = 100) -> List[Candle]:
        """
        SOTA Hybrid Data Layer: Load candles from SQLite first, Binance fallback.
        
        Pattern: Read-through cache
        - L1: In-memory (populated by this method)
        - L2: SQLite (check first)
        - L3: Binance API (fallback + write-through)
        
        Args:
            timeframe: '1m', '15m', or '1h'
            limit: Number of candles to load
            
        Returns:
            List of Candle objects, sorted by timestamp ascending
        """
        local_candles = []
        
        # Step 1: Try SQLite first (L2 cache)
        if self._market_data_repository:
            try:
                market_data_list = self._market_data_repository.get_latest_candles(
                    timeframe, limit
                )
                local_candles = [md.candle for md in market_data_list]
                # Sort ascending (oldest first) - SQLite returns DESC
                local_candles = sorted(local_candles, key=lambda c: c.timestamp)
                
                if local_candles:
                    self.logger.info(f"📦 SQLite HIT: {len(local_candles)}/{limit} {timeframe} candles")
            except Exception as e:
                self.logger.warning(f"⚠️ SQLite read failed for {timeframe}: {e}")
        
        # Step 2: Check if we have enough data (80% threshold)
        threshold = int(limit * 0.8)
        if len(local_candles) >= threshold:
            return local_candles
        
        # Step 3: SQLite miss - fetch from Binance (L3)
        self.logger.info(f"📡 SQLite MISS for {timeframe} ({len(local_candles)}/{limit}), fetching from Binance...")
        
        try:
            external_candles = self.rest_client.get_klines(
                symbol=self.symbol,
                interval=timeframe,
                limit=limit
            )
            
            if not external_candles:
                self.logger.warning(f"No external data for {timeframe}")
                return local_candles  # Return whatever we have
            
            # Step 4: Merge local + external, deduplicate by timestamp
            merged = self._merge_candles(local_candles, external_candles)
            
            # Step 5: Write-through - save new candles to SQLite
            if self._market_data_repository:
                local_timestamps = {c.timestamp for c in local_candles}
                new_candles = [c for c in merged if c.timestamp not in local_timestamps]
                
                if new_candles:
                    self.logger.info(f"💾 Write-through: Saving {len(new_candles)} new {timeframe} candles to SQLite")
                    for candle in new_candles:
                        try:
                            self._market_data_repository.save_candle_simple(candle, timeframe)
                        except Exception as e:
                            self.logger.error(f"Failed to save candle: {e}")
            
            return merged
            
        except Exception as e:
            self.logger.error(f"Binance fetch failed for {timeframe}: {e}")
            return local_candles  # Return whatever we have from SQLite
    
    def _merge_candles(self, local: List[Candle], external: List[Candle]) -> List[Candle]:
        """
        Merge local and external candles, deduplicate by timestamp.
        
        Priority: External (source of truth) for conflicts
        """
        # Create map by timestamp, external overwrites local
        candle_map = {}
        
        for candle in local:
            candle_map[candle.timestamp] = candle
        
        for candle in external:
            candle_map[candle.timestamp] = candle  # Overwrites if exists
        
        # Sort by timestamp ascending
        merged = sorted(candle_map.values(), key=lambda c: c.timestamp)
        return merged
```

---

### Task 2: Update `_load_historical_data()` method

**File:** `src/application/services/realtime_service.py`  
**Vị trí:** Replace toàn bộ method `_load_historical_data()` (lines 199-269)

```python
    async def _load_historical_data(self) -> None:
        """
        SOTA Hybrid Load: SQLite first, Binance fallback.
        
        This populates the buffer with recent candles so the dashboard
        shows data immediately instead of waiting for the first candle to close.
        
        Architecture:
        - L1: In-memory deques (fastest, volatile)
        - L2: SQLite (fast, persistent)
        - L3: Binance REST API (slow, source of truth)
        """
        try:
            self.logger.info("🚀 Loading historical candles (SOTA Hybrid)...")
            
            # 1. Load 1m candles
            candles_1m = self._load_candles_hybrid('1m', 100)
            if candles_1m:
                for candle in candles_1m:
                    self._candles_1m.append(candle)
                    self.aggregator.add_candle_1m(candle, is_closed=True)
                self._latest_1m = candles_1m[-1]
                self.logger.info(f"✅ Loaded {len(candles_1m)} 1m candles")
            else:
                self.logger.warning("No 1m data available")
            
            # 2. Load 15m candles (exclude last = incomplete)
            candles_15m = self._load_candles_hybrid('15m', 100)
            if candles_15m and len(candles_15m) > 1:
                completed_15m = candles_15m[:-1]  # Exclude incomplete
                for candle in completed_15m:
                    self._candles_15m.append(candle)
                self._latest_15m = completed_15m[-1]
                self.logger.info(f"✅ Loaded {len(completed_15m)} 15m candles")
            
            # 3. Load 1h candles (exclude last = incomplete)
            candles_1h = self._load_candles_hybrid('1h', 100)
            if candles_1h and len(candles_1h) > 1:
                completed_1h = candles_1h[:-1]
                for candle in completed_1h:
                    self._candles_1h.append(candle)
                self._latest_1h = completed_1h[-1]
                self.logger.info(f"✅ Loaded {len(completed_1h)} 1h candles")
            
            self.logger.info("✅ Historical data loaded successfully (SOTA Hybrid)")
            
        except Exception as e:
            self.logger.error(f"Error loading historical data: {e}")
            # Don't fail - continue with WebSocket streaming
```

---

## ✅ VERIFICATION

```bash
# 1. Delete old SQLite database (fresh start)
del crypto_data.db

# 2. Start backend
python -m src.main

# 3. Check logs - should see SQLite MISS (fresh DB)
📡 SQLite MISS for 1m (0/100), fetching from Binance...
💾 Write-through: Saving 100 new 1m candles to SQLite

# 4. Wait 15-30 minutes for candles to accumulate, then Restart backend

# 5. Check logs - should see SQLite HIT
📦 SQLite HIT: 95/100 1m candles
📦 SQLite HIT: 8/100 15m candles
```

---

## 📊 EXPECTED BEHAVIOR

| Scenario | Before | After |
|----------|--------|-------|
| First startup | Binance only | Binance + save to SQLite |
| Restart with data | Binance only | SQLite first (fast) |
| Binance API down | No data | Use SQLite cache |

---

*Priority: HIGH - Core persistence fix*
