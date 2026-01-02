"""
FetchMarketDataUseCase - Application Layer

Use case for fetching market data from external API.
"""

from typing import List, Protocol
import pandas as pd
from datetime import datetime

from ...domain.entities.candle import Candle


class BinanceClientProtocol(Protocol):
    """Protocol defining the interface for Binance API client"""
    def get_klines(self, symbol: str, interval: str, limit: int) -> pd.DataFrame:
        """Fetch klines data from Binance API"""
        ...


class FetchMarketDataUseCase:
    """
    Use case for fetching market data from Binance API.
    
    This use case:
    1. Fetches raw data from Binance API
    2. Converts to domain entities (Candle)
    3. Returns list of Candle entities
    
    Dependencies are injected via constructor (Dependency Injection).
    """
    
    def __init__(self, binance_client: BinanceClientProtocol):
        """
        Initialize use case with dependencies.
        
        Args:
            binance_client: Client for fetching data from Binance API
        """
        self.client = binance_client
    
    def execute(
        self, 
        symbol: str = 'BTCUSDT',
        timeframe: str = '15m',
        limit: int = 100
    ) -> List[Candle]:
        """
        Execute the use case: fetch market data and convert to entities.
        
        Args:
            symbol: Trading pair (default: 'BTCUSDT')
            timeframe: Timeframe (default: '15m')
            limit: Number of candles to fetch (default: 100)
        
        Returns:
            List of Candle entities
        
        Raises:
            ValueError: If parameters are invalid
            RuntimeError: If API call fails
        """
        # Validate inputs
        if limit <= 0:
            raise ValueError(f"Limit must be positive, got {limit}")
        
        if limit > 1000:
            raise ValueError(f"Limit cannot exceed 1000, got {limit}")
        
        # Fetch data from API
        try:
            df = self.client.get_klines(symbol, timeframe, limit)
        except Exception as e:
            raise RuntimeError(f"Failed to fetch data from Binance: {e}") from e
        
        if df is None or df.empty:
            return []
        
        # Convert DataFrame to Candle entities
        candles = []
        for _, row in df.iterrows():
            try:
                candle = Candle(
                    timestamp=pd.to_datetime(row['open_time'], unit='ms'),
                    open=float(row['open']),
                    high=float(row['high']),
                    low=float(row['low']),
                    close=float(row['close']),
                    volume=float(row['volume'])
                )
                candles.append(candle)
            except (KeyError, ValueError) as e:
                # Skip invalid rows
                continue
        
        return candles
