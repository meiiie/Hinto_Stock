# 🏗️ Implementation Plan: Smart Data Warehouse (Local Caching)

> **Status:** Draft (Ready for Dev)
> **Goal:** Eliminate API Timeouts & Enable 1-Year Backtests
> **Tech Stack:** Python, Pandas, PyArrow (Parquet)

---

## 1. Problem Statement
*   **Current:** On-Demand Fetching (Direct Binance API).
*   **Pain Point:** Loading 90 days for 10 symbols takes >5 mins (Timeout).
*   **Solution:** **"Sync & Store" Architecture**. Download once, store locally in Parquet format (fast, compressed), update incrementally.

---

## 2. Architecture Design

### 2.1 Storage Structure
```
backend/data/
├── cache/
│   ├── BTCUSDT/
│   │   ├── 15m.parquet   # Main timeframe
│   │   └── 4h.parquet    # HTF timeframe
│   ├── ETHUSDT/
│   │   └── ...
```

### 2.2 Logic Flow: "Smart Sync" Strategy

When `load_data(symbol, interval, start_date)` is called:

1.  **Check Cache:** Does `data/cache/{symbol}/{interval}.parquet` exist?
2.  **Case A: No Cache (First Run)**
    *   Fetch FULL history from Binance (e.g., from 2023-01-01).
    *   Save to Parquet.
    *   Return requested slice.
3.  **Case B: Cache Exists (Subsequent Runs)**
    *   Load Parquet metadata (fast).
    *   Identify `last_timestamp` in file.
    *   **Incremental Update:** Fetch only from `last_timestamp` to `NOW`.
    *   Append new data -> Save back to Parquet.
    *   Return requested slice.

---

## 3. Implementation Steps

### Step 1: Create `ParquetDataManager` Class
Create `backend/src/infrastructure/data/parquet_manager.py`.

```python
import pandas as pd
import os
from pathlib import Path

class ParquetDataManager:
    def __init__(self, data_dir="data/cache"):
        self.base_path = Path(data_dir)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def load(self, symbol: str, interval: str) -> pd.DataFrame:
        path = self._get_path(symbol, interval)
        if path.exists():
            return pd.read_parquet(path)
        return None

    def save(self, df: pd.DataFrame, symbol: str, interval: str):
        path = self._get_path(symbol, interval)
        path.parent.mkdir(parents=True, exist_ok=True)
        # Ensure timestamp index
        if 'timestamp' in df.columns:
            df.set_index('timestamp', inplace=True)
        # Save compressed
        df.to_parquet(path, compression='snappy')

    def _get_path(self, symbol, interval):
        return self.base_path / symbol / f"{interval}.parquet"
```

### Step 2: Integrate into `HistoricalDataLoader`
Modify `backend/src/infrastructure/data/historical_data_loader.py`.

```python
class HistoricalDataLoader:
    def __init__(self):
        self.client = BinanceRestClient()
        self.cache = ParquetDataManager() # Inject dependency

    async def load_data(self, symbol, interval, start_time, end_time):
        # 1. Try Load Cache
        df = self.cache.load(symbol, interval)
        
        # 2. Sync Logic
        if df is None:
            # Full Download
            df = await self._fetch_full_history(symbol, interval)
            self.cache.save(df, symbol, interval)
        else:
            # Incremental Update
            last_ts = df.index[-1]
            if last_ts < datetime.now() - timedelta(minutes=15):
                new_df = await self.client.get_klines(symbol, interval, start=last_ts)
                if not new_df.empty:
                    df = pd.concat([df, new_df])
                    df = df[~df.index.duplicated(keep='last')] # Dedup
                    self.cache.save(df, symbol, interval)
        
        # 3. Slice & Return
        mask = (df.index >= start_time) & (df.index <= end_time)
        return df.loc[mask]
```

---

## 4. Benchmark Expectations

| Metric | API (Old) | Parquet Cache (New) | Improvement |
| :--- | :--- | :--- | :--- |
| **Speed (90 days)** | 300s (or Timeout) | **0.5s** | **600x Faster** |
| **Data Size** | N/A (RAM only) | ~500KB / year | Efficient |
| **Stability** | Fragile (Rate Limits) | Robust (Offline capable) | ✅ |

---

*Hinto Engineering Team - 2026*
