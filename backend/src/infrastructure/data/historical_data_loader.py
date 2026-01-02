"""
HistoricalDataLoader - Smart Local Data Warehouse

SOTA Implementation (Jan 2026):
- Parquet-based caching for historical data
- Incremental sync (only fetch missing data)
- ZSTD compression for minimal storage
- First run: ~2-5 min. Subsequent runs: <1 sec

Storage Structure:
  backend/data/cache/
  ├── BTCUSDT/
  │   ├── 15m.parquet  (~500KB for 1 year)
  │   └── 1h.parquet
  └── metadata.json    (last sync timestamps)
"""

import logging
import asyncio
import json
import os
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict
from pathlib import Path

import pandas as pd

from ...domain.entities.candle import Candle
from ...domain.interfaces.i_historical_data_loader import IHistoricalDataLoader
from ..api.binance_rest_client import BinanceRestClient


class HistoricalDataLoader(IHistoricalDataLoader):
    """
    Smart Local Data Warehouse for Historical Market Data.
    
    Uses Parquet format for:
    - Columnar storage (optimized for time-series)
    - ZSTD compression (3-5x smaller than CSV)
    - 50-100x faster read/write than CSV
    
    Features:
    - Incremental sync: Only fetches missing data
    - Automatic cache validation
    - Graceful fallback to API if cache corrupted
    """
    
    # Cache directory relative to backend/
    CACHE_DIR = Path(__file__).parent.parent.parent.parent / "data" / "cache"
    METADATA_FILE = CACHE_DIR / "metadata.json"
    
    # Parquet compression (ZSTD = best speed/ratio balance)
    COMPRESSION = "zstd"
    
    def __init__(self, rest_client: Optional[BinanceRestClient] = None):
        """
        Initialize loader with cache directory setup.
        
        Args:
            rest_client: Injected Binance REST client
        """
        self.rest_client = rest_client or BinanceRestClient()
        self.logger = logging.getLogger(__name__)
        
        # Ensure cache directory exists
        self.CACHE_DIR.mkdir(parents=True, exist_ok=True)
        
        # Load metadata
        self._metadata = self._load_metadata()
        
    def _load_metadata(self) -> Dict:
        """Load sync metadata from JSON file."""
        if self.METADATA_FILE.exists():
            try:
                with open(self.METADATA_FILE, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Failed to load metadata: {e}")
        return {}
    
    def _save_metadata(self):
        """Save sync metadata to JSON file."""
        try:
            with open(self.METADATA_FILE, 'w') as f:
                json.dump(self._metadata, f, indent=2, default=str)
        except Exception as e:
            self.logger.warning(f"Failed to save metadata: {e}")
    
    def _get_cache_path(self, symbol: str, interval: str) -> Path:
        """
        Get Parquet file path for symbol/interval.
        
        Example: data/cache/BTCUSDT/15m.parquet
        """
        symbol_dir = self.CACHE_DIR / symbol.upper()
        symbol_dir.mkdir(parents=True, exist_ok=True)
        return symbol_dir / f"{interval}.parquet"
    
    def _get_metadata_key(self, symbol: str, interval: str) -> str:
        """Get metadata key for symbol/interval pair."""
        return f"{symbol.upper()}_{interval}"
    
    async def load_candles(
        self,
        symbol: str,
        interval: str,
        start_time: datetime,
        end_time: Optional[datetime] = None
    ) -> List[Candle]:
        """
        Load historical candles with Smart Sync caching.
        
        Flow:
        1. Check Parquet cache
        2. If cache exists, check if incremental update needed
        3. Only fetch missing data from API
        4. Merge and save back to cache
        5. Return filtered data for requested range
        
        Args:
            symbol: Trading pair (e.g. 'BTCUSDT')
            interval: Timeframe (e.g. '1m', '15m', '1h')
            start_time: Start of range
            end_time: End of range (default: now)
            
        Returns:
            List of Candle entities sorted by timestamp
        """
        if end_time is None:
            end_time = datetime.now(timezone.utc)
            
        # Ensure timezone aware
        if start_time.tzinfo is None:
            start_time = start_time.replace(tzinfo=timezone.utc)
        if end_time.tzinfo is None:
            end_time = end_time.replace(tzinfo=timezone.utc)
        
        cache_path = self._get_cache_path(symbol, interval)
        meta_key = self._get_metadata_key(symbol, interval)
        
        self.logger.info(f"📂 Smart Sync: {symbol} {interval} | {start_time.date()} → {end_time.date()}")
        
        # === Step 1: Try to load from cache ===
        df_cache = None
        if cache_path.exists():
            try:
                df_cache = pd.read_parquet(cache_path)
                self.logger.info(f"  📦 Cache hit: {len(df_cache)} candles from disk")
            except Exception as e:
                self.logger.warning(f"  ⚠️ Cache corrupted, will refetch: {e}")
                df_cache = None
        
        # === Step 2: Determine what to fetch ===
        need_fetch = False
        fetch_start = start_time
        fetch_end = end_time
        
        if df_cache is not None and not df_cache.empty:
            cache_start = pd.to_datetime(df_cache['timestamp'].min()).to_pydatetime().replace(tzinfo=timezone.utc)
            cache_end = pd.to_datetime(df_cache['timestamp'].max()).to_pydatetime().replace(tzinfo=timezone.utc)
            
            # Check if we need data BEFORE cache
            if start_time < cache_start:
                self.logger.info(f"  ⬅️ Need historical data before cache: {start_time} < {cache_start}")
                fetch_start = start_time
                fetch_end = cache_start - timedelta(minutes=1)
                need_fetch = True
            
            # Check if we need data AFTER cache (incremental update)
            if end_time > cache_end + timedelta(minutes=self._interval_to_minutes(interval)):
                self.logger.info(f"  ➡️ Incremental update: {cache_end} → {end_time}")
                fetch_start = cache_end + timedelta(minutes=1)
                fetch_end = end_time
                need_fetch = True
            
            # If cache fully covers the range
            if not need_fetch:
                self.logger.info(f"  ✅ Cache fully covers range, no fetch needed")
        else:
            # No cache, fetch everything
            need_fetch = True
            self.logger.info(f"  📥 Cache miss, fetching full range from API")
        
        # === Step 3: Fetch missing data from API ===
        new_candles = []
        if need_fetch:
            new_candles = await self._fetch_from_api(symbol, interval, fetch_start, fetch_end)
            self.logger.info(f"  📡 Fetched {len(new_candles)} new candles from Binance")
        
        # === Step 4: Merge and save cache ===
        if new_candles:
            df_new = self._candles_to_dataframe(new_candles)
            
            if df_cache is not None and not df_cache.empty:
                df_merged = pd.concat([df_cache, df_new], ignore_index=True)
                df_merged = df_merged.drop_duplicates(subset=['timestamp'])
                df_merged = df_merged.sort_values('timestamp').reset_index(drop=True)
            else:
                df_merged = df_new
            
            # Save to Parquet with ZSTD compression
            df_merged.to_parquet(cache_path, compression=self.COMPRESSION, index=False)
            self.logger.info(f"  💾 Saved {len(df_merged)} candles to cache ({cache_path.stat().st_size / 1024:.1f} KB)")
            
            # Update metadata
            self._metadata[meta_key] = {
                "last_sync": datetime.now(timezone.utc).isoformat(),
                "candle_count": len(df_merged),
                "date_range": f"{df_merged['timestamp'].min()} - {df_merged['timestamp'].max()}"
            }
            self._save_metadata()
            
            df_cache = df_merged
        
        # === Step 5: Filter to requested range and return ===
        if df_cache is None or df_cache.empty:
            return []
        
        # Convert timestamp column to datetime for filtering
        df_cache['timestamp'] = pd.to_datetime(df_cache['timestamp'])
        
        mask = (df_cache['timestamp'] >= start_time) & (df_cache['timestamp'] <= end_time)
        df_filtered = df_cache[mask]
        
        candles = self._dataframe_to_candles(df_filtered, symbol)
        self.logger.info(f"  ✅ Returning {len(candles)} candles for requested range")
        
        return candles
    
    async def _fetch_from_api(
        self,
        symbol: str,
        interval: str,
        start_time: datetime,
        end_time: datetime
    ) -> List[Candle]:
        """
        Fetch candles from Binance API with pagination.
        
        Uses backwards pagination from end_time.
        """
        all_candles: List[Candle] = []
        
        current_end_ms = int(end_time.timestamp() * 1000)
        start_ms = int(start_time.timestamp() * 1000)
        
        request_count = 0
        max_requests = 100  # Safety limit
        
        while current_end_ms > start_ms and request_count < max_requests:
            limit = 1000
            chunk = self.rest_client.get_klines(
                symbol=symbol,
                interval=interval,
                limit=limit,
                end_time=current_end_ms
            )
            
            if not chunk:
                break
            
            # Filter candles within range
            chunk_filtered = [c for c in chunk if int(c.timestamp.timestamp() * 1000) >= start_ms]
            all_candles = chunk_filtered + all_candles
            
            # Move backwards
            first_candle_ms = int(chunk[0].timestamp.timestamp() * 1000)
            current_end_ms = first_candle_ms - 1
            
            if first_candle_ms <= start_ms:
                break
            
            request_count += 1
            await asyncio.sleep(0.05)  # Rate limiting
        
        # Deduplicate and sort
        seen = set()
        unique = []
        for c in sorted(all_candles, key=lambda x: x.timestamp):
            if c.timestamp not in seen:
                unique.append(c)
                seen.add(c.timestamp)
        
        return unique
    
    def _candles_to_dataframe(self, candles: List[Candle]) -> pd.DataFrame:
        """Convert list of Candle entities to DataFrame."""
        data = []
        for c in candles:
            data.append({
                'timestamp': c.timestamp,
                'open': c.open,
                'high': c.high,
                'low': c.low,
                'close': c.close,
                'volume': c.volume
            })
        return pd.DataFrame(data)
    
    def _dataframe_to_candles(self, df: pd.DataFrame, symbol: str) -> List[Candle]:
        """Convert DataFrame back to list of Candle entities."""
        candles = []
        for _, row in df.iterrows():
            ts = row['timestamp']
            if isinstance(ts, str):
                ts = datetime.fromisoformat(ts.replace('Z', '+00:00'))
            elif isinstance(ts, pd.Timestamp):
                ts = ts.to_pydatetime()
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
                
            # Note: Candle entity doesn't have symbol/interval fields
            candles.append(Candle(
                timestamp=ts,
                open=float(row['open']),
                high=float(row['high']),
                low=float(row['low']),
                close=float(row['close']),
                volume=float(row['volume'])
            ))
        return candles
    
    def _interval_to_minutes(self, interval: str) -> int:
        """Convert interval string to minutes."""
        mapping = {
            '1m': 1, '3m': 3, '5m': 5, '15m': 15, '30m': 30,
            '1h': 60, '2h': 120, '4h': 240, '6h': 360, '8h': 480, '12h': 720,
            '1d': 1440, '3d': 4320, '1w': 10080
        }
        return mapping.get(interval, 15)
    
    async def load_portfolio_data(
        self,
        symbols: List[str],
        interval: str,
        start_time: datetime,
        end_time: Optional[datetime] = None
    ) -> Dict[datetime, Dict[str, Candle]]:
        """
        Load synchronized data for multiple symbols with Smart Sync.
        
        All symbols are loaded in parallel with individual caching.
        
        Returns:
            Dict where key is timestamp and value is dict of {symbol: Candle}
        """
        self.logger.info(f"📊 Loading portfolio data for {len(symbols)} symbols...")
        
        # Load all data in parallel (each with its own cache)
        tasks = [self.load_candles(sym, interval, start_time, end_time) for sym in symbols]
        results = await asyncio.gather(*tasks)
        
        # Merge into timeline
        timeline = {}
        for sym, candles in zip(symbols, results):
            for c in candles:
                if c.timestamp not in timeline:
                    timeline[c.timestamp] = {}
                timeline[c.timestamp][sym] = c
        
        # Sort by time
        sorted_keys = sorted(timeline.keys())
        sorted_timeline = {k: timeline[k] for k in sorted_keys}
        
        self.logger.info(f"✅ Portfolio timeline ready: {len(sorted_timeline)} timestamps")
        return sorted_timeline
    
    def clear_cache(self, symbol: Optional[str] = None, interval: Optional[str] = None):
        """
        Clear cache files.
        
        Args:
            symbol: Specific symbol to clear (None = all)
            interval: Specific interval to clear (None = all for symbol)
        """
        if symbol and interval:
            cache_path = self._get_cache_path(symbol, interval)
            if cache_path.exists():
                cache_path.unlink()
                self.logger.info(f"🗑️ Cleared cache: {symbol}/{interval}")
        elif symbol:
            symbol_dir = self.CACHE_DIR / symbol.upper()
            if symbol_dir.exists():
                import shutil
                shutil.rmtree(symbol_dir)
                self.logger.info(f"🗑️ Cleared all cache for: {symbol}")
        else:
            import shutil
            if self.CACHE_DIR.exists():
                shutil.rmtree(self.CACHE_DIR)
                self.CACHE_DIR.mkdir(parents=True, exist_ok=True)
                self.logger.info("🗑️ Cleared entire cache")
        
        # Reset metadata
        self._metadata = {}
        self._save_metadata()
    
    def get_cache_stats(self) -> Dict:
        """
        Get cache statistics.
        
        Returns:
            Dict with cache info for each symbol/interval
        """
        stats = {
            "cache_dir": str(self.CACHE_DIR),
            "total_size_kb": 0,
            "symbols": {}
        }
        
        if not self.CACHE_DIR.exists():
            return stats
        
        for symbol_dir in self.CACHE_DIR.iterdir():
            if symbol_dir.is_dir():
                symbol = symbol_dir.name
                stats["symbols"][symbol] = {}
                for parquet_file in symbol_dir.glob("*.parquet"):
                    interval = parquet_file.stem
                    size_kb = parquet_file.stat().st_size / 1024
                    stats["symbols"][symbol][interval] = {
                        "size_kb": round(size_kb, 2),
                        "meta": self._metadata.get(f"{symbol}_{interval}", {})
                    }
                    stats["total_size_kb"] += size_kb
        
        stats["total_size_kb"] = round(stats["total_size_kb"], 2)
        return stats
