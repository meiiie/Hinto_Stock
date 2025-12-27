"""
SharedBinanceClient - SOTA Multi-Symbol Combined Streams Manager

Single WebSocket connection for all symbols, routes data to registered handlers.
Follows Binance official best practices (Dec 2025).

Usage:
    client = SharedBinanceClient()
    client.register_handler('btcusdt', my_callback)
    client.register_handler('ethusdt', other_callback)
    await client.connect()  # 1 connection for ALL symbols
"""

import asyncio
import logging
from typing import Callable, Dict, List, Optional, Any
from datetime import datetime

from .binance_websocket_client import BinanceWebSocketClient, ConnectionStatus
from ...domain.entities.candle import Candle


class SharedBinanceClient:
    """
    SOTA: Shared WebSocket client for multi-symbol combined streams.
    
    Uses single Binance WebSocket connection for all symbols.
    Routes data to registered symbol-specific handlers.
    
    Benefits:
    - 1 connection instead of N (no timeout issues)
    - Lower latency (single connection to maintain)
    - Binance rate limit compliant
    - Scales to 100+ symbols easily
    """
    
    _instance: Optional['SharedBinanceClient'] = None
    
    def __new__(cls):
        """Singleton pattern"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self._client = BinanceWebSocketClient()
        self._handlers: Dict[str, List[Callable]] = {}  # symbol -> [callbacks]
        self._connection_handlers: List[Callable] = []
        self._symbols: List[str] = []
        self._intervals: List[str] = ['1m', '15m', '1h']  # Default timeframes
        self._is_running = False
        self.logger = logging.getLogger(__name__)
        
        # Subscribe to client callbacks and route to handlers
        self._client.subscribe_candle(self._route_candle)
        self._client.subscribe_connection_status(self._route_connection_status)
    
    def register_handler(
        self, 
        symbol: str, 
        callback: Callable[[Candle, Dict[str, Any]], None]
    ) -> None:
        """
        Register a callback for a specific symbol.
        
        Args:
            symbol: Symbol to receive data for (e.g., 'btcusdt')
            callback: Function to call with candle data
        """
        symbol_lower = symbol.lower()
        if symbol_lower not in self._handlers:
            self._handlers[symbol_lower] = []
            if symbol_lower not in self._symbols:
                self._symbols.append(symbol_lower)
        
        self._handlers[symbol_lower].append(callback)
        self.logger.info(f"📝 Registered handler for {symbol_lower} (total: {len(self._handlers[symbol_lower])})")
    
    def register_connection_handler(self, callback: Callable[[ConnectionStatus], None]) -> None:
        """Register callback for connection status changes"""
        self._connection_handlers.append(callback)
    
    async def connect(self) -> None:
        """
        Connect to Binance with combined streams for all registered symbols.
        """
        if self._is_running:
            self.logger.warning("SharedBinanceClient already running")
            return
        
        if not self._symbols:
            self.logger.error("No symbols registered! Call register_handler first.")
            return
        
        self._is_running = True
        self.logger.info(f"🚀 SOTA Combined Streams: {len(self._symbols)} symbols × {len(self._intervals)} timeframes")
        
        await self._client.connect(
            symbols=self._symbols,
            intervals=self._intervals
        )
    
    async def disconnect(self) -> None:
        """Disconnect from Binance"""
        self._is_running = False
        await self._client.disconnect()
    
    def _route_candle(self, candle: Candle, metadata: Dict[str, Any]) -> None:
        """Route candle data to the correct symbol handler"""
        symbol = metadata.get('symbol', '').lower()
        interval = metadata.get('interval', '1m')
        
        if symbol in self._handlers:
            for callback in self._handlers[symbol]:
                try:
                    callback(candle, metadata)
                except Exception as e:
                    self.logger.error(f"Error in handler for {symbol}: {e}")
        else:
            self.logger.debug(f"No handler for symbol: {symbol}")
    
    async def _route_connection_status(self, status: ConnectionStatus) -> None:
        """Route connection status to all handlers"""
        for callback in self._connection_handlers:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(status)
                else:
                    callback(status)
            except Exception as e:
                self.logger.error(f"Error in connection handler: {e}")
    
    @property
    def is_connected(self) -> bool:
        return self._client.is_connected()
    
    def get_status(self) -> ConnectionStatus:
        return self._client.get_connection_status()


# Singleton getter
_shared_client: Optional[SharedBinanceClient] = None

def get_shared_binance_client() -> SharedBinanceClient:
    """Get the singleton SharedBinanceClient instance"""
    global _shared_client
    if _shared_client is None:
        _shared_client = SharedBinanceClient()
    return _shared_client
