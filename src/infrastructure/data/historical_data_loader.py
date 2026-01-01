"""
HistoricalDataLoader - Infrastructure Layer

Service for loading historical market data for backtesting.
Supports fetching large datasets from Binance by paginating requests.
"""

import logging
import asyncio
from datetime import datetime, timezone
from typing import List, Optional, Dict

from ...domain.entities.candle import Candle
from ..api.binance_rest_client import BinanceRestClient


class HistoricalDataLoader:
    """
    Service to fetch large amounts of historical klines.
    
    Handles pagination logic to overcome Binance's 1000-candle limit per request.
    """
    
    def __init__(self, rest_client: Optional[BinanceRestClient] = None):
        """
        Initialize loader.
        
        Args:
            rest_client: Injected Binance REST client
        """
        self.rest_client = rest_client or BinanceRestClient()
        self.logger = logging.getLogger(__name__)

    async def load_candles(
        self,
        symbol: str,
        interval: str,
        start_time: datetime,
        end_time: Optional[datetime] = None
    ) -> List[Candle]:
        """
        Load historical candles for a specific time range.
        
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
            
        # Ensure start/end are timezone aware
        if start_time.tzinfo is None:
            start_time = start_time.replace(tzinfo=timezone.utc)
        if end_time.tzinfo is None:
            end_time = end_time.replace(tzinfo=timezone.utc)

        all_candles: List[Candle] = []
        
        # Convert to milliseconds for Binance API
        current_start_ms = int(start_time.timestamp() * 1000)
        end_ms = int(end_time.timestamp() * 1000)
        
        self.logger.info(f"⏳ Loading historical data for {symbol} {interval} from {start_time} to {end_time}...")

        while current_start_ms < end_ms:
            # Note: Binance 'klines' API doesn't have startTime in our current rest_client.get_klines
            # but it has endTime. We can fetch backwards from end_time.
            # However, for large ranges, it's easier to fetch chunks.
            
            # Since our BinanceRestClient.get_klines only supports end_time,
            # we fetch in chunks from the END of the range backwards.
            # But backtesting usually wants forward progress.
            
            # Better implementation: Fetch chunks of 1000 backwards until we hit start_time
            # or exceed the limit.
            
            # Actually, let's stick to the current rest_client's capability but use it effectively.
            # We'll fetch the LATEST 1000 until we go back far enough.
            
            # Wait, Binance API DOES support startTime. Let's check if we should modify the client.
            # Our client doesn't have it. Let's add it or use raw requests here.
            
            # For MVP, we will fetch 1000 candles at a time.
            # Note: get_klines in our rest_client uses 'endTime'.
            
            limit = 1000
            chunk = self.rest_client.get_klines(
                symbol=symbol,
                interval=interval,
                limit=limit,
                end_time=end_ms
            )
            
            if not chunk:
                break
                
            # Filter candles that are before our start_time
            chunk_filtered = [c for c in chunk if int(c.timestamp.timestamp() * 1000) >= current_start_ms]
            
            if not chunk_filtered:
                break
                
            # Add to list (Binance returns them ASC, but we are moving backwards)
            all_candles = chunk_filtered + all_candles
            
            # Move end_ms back to the timestamp of the earliest candle in this chunk minus 1ms
            first_candle_ms = int(chunk[0].timestamp.timestamp() * 1000)
            end_ms = first_candle_ms - 1
            
            # Stop if we've reached or passed the start_time
            if first_candle_ms <= current_start_ms:
                break
                
            # Rate limiting safety (Optimized for performance)
            await asyncio.sleep(0.01)

        # Final deduplication and sorting
        seen_timestamps = set()
        unique_candles = []
        for c in sorted(all_candles, key=lambda x: x.timestamp):
            if c.timestamp not in seen_timestamps:
                unique_candles.append(c)
                seen_timestamps.add(c.timestamp)
                
        self.logger.info(f"✅ Successfully loaded {len(unique_candles)} candles")
        return unique_candles

    async def load_portfolio_data(
        self,
        symbols: List[str],
        interval: str,
        start_time: datetime,
        end_time: Optional[datetime] = None
    ) -> Dict[datetime, Dict[str, Candle]]:
        """
        Load synchronized data for multiple symbols.
        
        Returns:
            Dict where key is timestamp and value is dict of {symbol: Candle}
            Example: {
                dt(2024,1,1, 12,0): {'BTCUSDT': Candle(...), 'ETHUSDT': Candle(...)},
                ...
            }
        """
        self.logger.info(f"📊 Loading portfolio data for {len(symbols)} symbols...")
        
        # 1. Load all data in parallel
        tasks = [self.load_candles(sym, interval, start_time, end_time) for sym in symbols]
        results = await asyncio.gather(*tasks)
        
        # 2. Merge into timeline
        timeline = {}
        for sym, candles in zip(symbols, results):
            for c in candles:
                if c.timestamp not in timeline:
                    timeline[c.timestamp] = {}
                timeline[c.timestamp][sym] = c
                
        # 3. Sort by time
        # Note: In Python 3.7+, dicts maintain insertion order, so sorting keys is enough
        sorted_keys = sorted(timeline.keys())
        sorted_timeline = {k: timeline[k] for k in sorted_keys}
        
        self.logger.info(f"✅ Portfolio timeline ready: {len(sorted_timeline)} timestamps")
        return sorted_timeline
