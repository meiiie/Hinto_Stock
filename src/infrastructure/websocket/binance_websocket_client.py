"""
BinanceWebSocketClient - Infrastructure Layer

WebSocket client for real-time Binance market data streaming.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Optional, Callable, Dict, Any
from dataclasses import dataclass
from enum import Enum

try:
    import websockets
    from websockets.client import WebSocketClientProtocol
except ImportError:
    raise ImportError(
        "websockets library is required for real-time streaming. "
        "Install it with: pip install websockets>=12.0"
    )

from .message_parser import BinanceMessageParser
from ...domain.entities.candle import Candle


class ConnectionState(Enum):
    """WebSocket connection states"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"
    ERROR = "error"


@dataclass
class ConnectionStatus:
    """Connection status information"""
    is_connected: bool
    state: ConnectionState
    last_update: datetime
    latency_ms: int
    reconnect_count: int
    error_message: Optional[str] = None


class BinanceWebSocketClient:
    """
    WebSocket client for Binance real-time data streaming.
    
    Features:
    - Persistent WebSocket connection
    - Automatic reconnection with exponential backoff
    - Message parsing and validation
    - Connection health monitoring
    """

    
    def __init__(
        self,
        base_url: str = "wss://stream.binance.com:9443/ws",
        initial_reconnect_delay: float = 1.0,
        max_reconnect_delay: float = 60.0
    ):
        """
        Initialize WebSocket client.
        
        Args:
            base_url: Binance WebSocket stream base URL
            initial_reconnect_delay: Initial delay for reconnection (seconds)
            max_reconnect_delay: Maximum delay for reconnection (seconds)
        """
        self.base_url = base_url
        self.initial_reconnect_delay = initial_reconnect_delay
        self.max_reconnect_delay = max_reconnect_delay
        
        # Connection state
        self._websocket: Optional[WebSocketClientProtocol] = None
        self._state = ConnectionState.DISCONNECTED
        self._reconnect_count = 0
        self._current_reconnect_delay = initial_reconnect_delay
        self._last_update = datetime.now()
        self._latency_ms = 0
        self._error_message: Optional[str] = None
        
        # Callbacks
        self._message_callbacks: list[Callable] = []
        self._candle_callbacks: list[Callable] = []
        self._connection_callbacks: list[Callable] = []
        
        # Control flags
        self._should_run = False
        self._receive_task: Optional[asyncio.Task] = None
        
        # Message parser
        self._parser = BinanceMessageParser()
        
        # Connection parameters (for reconnection)
        self._symbol: Optional[str] = None
        self._interval: Optional[str] = None
        
        # Logging
        self.logger = logging.getLogger(__name__)
    
    async def connect(self, symbol: str = "btcusdt", interval: str = "1m", start_loop: bool = True) -> None:
        """
        Connect to Binance WebSocket stream.
        
        Args:
            symbol: Trading pair symbol (e.g., 'btcusdt')
            interval: Kline interval (e.g., '1m', '15m', '1h')
            start_loop: Whether to start the receive loop task (default: True)
        
        Raises:
            Exception: If connection fails
        """
        if self._state == ConnectionState.CONNECTED:
            self.logger.warning("Already connected to WebSocket")
            return
        
        self._should_run = True
        # Only update state if not reconnecting (to preserve RECONNECTING status if applicable)
        if self._state != ConnectionState.RECONNECTING:
            self._state = ConnectionState.CONNECTING
        
        # Store connection parameters for reconnection
        self._symbol = symbol
        self._interval = interval
        
        # Build WebSocket URL
        stream_name = f"{symbol.lower()}@kline_{interval}"
        url = f"{self.base_url}/{stream_name}"
        
        self.logger.info(f"Connecting to Binance WebSocket: {url}")
        
        try:
            self._websocket = await websockets.connect(
                url,
                ping_interval=20,
                ping_timeout=10
            )
            
            self._state = ConnectionState.CONNECTED
            self._last_update = datetime.now()
            self._error_message = None
            
            self.logger.info("✅ WebSocket connected successfully")
            
            # Notify connection callbacks
            await self._notify_connection_status()
            
            # Start receiving messages ONLY if requested and not already running
            if start_loop:
                if self._receive_task is None or self._receive_task.done():
                    self._receive_task = asyncio.create_task(self._receive_messages())
                else:
                    self.logger.warning("Receive task already running")
            
        except Exception as e:
            self._state = ConnectionState.ERROR
            self._error_message = str(e)
            self.logger.error(f"❌ WebSocket connection failed: {e}")
            raise

    
    async def disconnect(self) -> None:
        """
        Disconnect from WebSocket stream.
        """
        self.logger.info("Disconnecting from WebSocket...")
        
        self._should_run = False
        
        # Cancel receive task
        if self._receive_task and not self._receive_task.done():
            self._receive_task.cancel()
            try:
                await self._receive_task
            except asyncio.CancelledError:
                pass
        
        # Close WebSocket connection
        if self._websocket:
            await self._websocket.close()
            self._websocket = None
        
        self._state = ConnectionState.DISCONNECTED
        self.logger.info("✅ WebSocket disconnected")
    
    async def _receive_messages(self) -> None:
        """
        Receive and process messages from WebSocket.
        
        Handles reconnection on connection loss.
        """
        while self._should_run:
            try:
                if not self._websocket:
                    self.logger.warning("WebSocket not connected, attempting reconnection...")
                    await self._reconnect()
                    continue
                
                # Receive message
                message = await self._websocket.recv()
                # print(f"DEBUG: Received message: {message[:50]}...") # Uncomment for extreme debug
                
                # Update last update time
                self._last_update = datetime.now()
                
                # Parse and process message
                await self._process_message(message)
                
            except websockets.exceptions.ConnectionClosed as e:
                self.logger.warning(f"WebSocket connection closed: {e}")
                self._state = ConnectionState.DISCONNECTED
                
                if self._should_run:
                    await self._reconnect()
                else:
                    break
                    
            except asyncio.CancelledError:
                self.logger.info("Receive task cancelled")
                break
                
            except Exception as e:
                self.logger.error(f"Error receiving message: {e}")
                await asyncio.sleep(1)
    
    async def _reconnect(self) -> None:
        """
        Reconnect to WebSocket with exponential backoff.
        """
        self._state = ConnectionState.RECONNECTING
        self._reconnect_count += 1
        
        self.logger.info(
            f"Reconnecting... (attempt {self._reconnect_count}, "
            f"delay: {self._current_reconnect_delay:.1f}s)"
        )
        
        # Wait before reconnecting
        await asyncio.sleep(self._current_reconnect_delay)
        
        # Increase delay for next attempt (exponential backoff)
        self._current_reconnect_delay = min(
            self._current_reconnect_delay * 2,
            self.max_reconnect_delay
        )
        
        try:
            # Attempt to reconnect using stored parameters
            if self._symbol and self._interval:
                # CRITICAL FIX: Do not start new loop, as we are already inside one
                await self.connect(self._symbol, self._interval, start_loop=False)
                
                # Reset delay on successful connection
                self._current_reconnect_delay = self.initial_reconnect_delay
            else:
                self.logger.error("Cannot reconnect: missing symbol/interval")
                self._state = ConnectionState.ERROR
            
        except Exception as e:
            self.logger.error(f"Reconnection failed: {e}")
            self._state = ConnectionState.ERROR
            self._error_message = str(e)

    
    async def _process_message(self, message: str) -> None:
        """
        Parse and process incoming WebSocket message.
        
        Args:
            message: Raw JSON message from WebSocket
        """
        try:
            data = json.loads(message)
            
            # Calculate latency
            if 'E' in data:  # Event time
                event_time = datetime.fromtimestamp(data['E'] / 1000)
                latency = (datetime.now() - event_time).total_seconds() * 1000
                self._latency_ms = int(latency)
                # print(f"DEBUG: Latency updated: {self._latency_ms}ms")
            
            # Parse message to Candle entity
            candle = self._parser.parse_kline_message(data)
            metadata = self._parser.extract_metadata(data)
            
            # Notify raw message callbacks
            for callback in self._message_callbacks:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(data)
                    else:
                        callback(data)
                except Exception as e:
                    self.logger.error(f"Error in message callback: {e}")
            
            # Notify candle callbacks if parsing successful
            if candle:
                for callback in self._candle_callbacks:
                    try:
                        if asyncio.iscoroutinefunction(callback):
                            await callback(candle, metadata)
                        else:
                            callback(candle, metadata)
                    except Exception as e:
                        self.logger.error(f"Error in candle callback: {e}")
        
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse message: {e}")
        except Exception as e:
            self.logger.error(f"Error processing message: {e}")
    
    async def _notify_connection_status(self) -> None:
        """Notify all connection status callbacks"""
        status = self.get_connection_status()
        
        for callback in self._connection_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(status)
                else:
                    callback(status)
            except Exception as e:
                self.logger.error(f"Error in connection callback: {e}")
    
    def subscribe_kline(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """
        Subscribe to raw kline messages.
        
        Args:
            callback: Function to call when new kline message arrives
                     Signature: callback(data: Dict[str, Any]) -> None
        """
        self._message_callbacks.append(callback)
        self.logger.debug(f"Added kline callback (total: {len(self._message_callbacks)})")
    
    def subscribe_candle(self, callback: Callable[[Candle, Dict[str, Any]], None]) -> None:
        """
        Subscribe to parsed Candle entities.
        
        Args:
            callback: Function to call when new candle is parsed
                     Signature: callback(candle: Candle, metadata: Dict) -> None
        """
        self._candle_callbacks.append(callback)
        self.logger.debug(f"Added candle callback (total: {len(self._candle_callbacks)})")
    
    def subscribe_connection_status(self, callback: Callable[[ConnectionStatus], None]) -> None:
        """
        Subscribe to connection status changes.
        
        Args:
            callback: Function to call when connection status changes
                     Signature: callback(status: ConnectionStatus) -> None
        """
        self._connection_callbacks.append(callback)
        self.logger.debug(f"Added connection callback (total: {len(self._connection_callbacks)})")
    
    def is_connected(self) -> bool:
        """
        Check if WebSocket is currently connected.
        
        Returns:
            True if connected, False otherwise
        """
        return self._state == ConnectionState.CONNECTED and self._websocket is not None
    
    def get_connection_status(self) -> ConnectionStatus:
        """
        Get current connection status.
        
        Returns:
            ConnectionStatus object with current state
        """
        return ConnectionStatus(
            is_connected=self.is_connected(),
            state=self._state,
            last_update=self._last_update,
            latency_ms=self._latency_ms,
            reconnect_count=self._reconnect_count,
            error_message=self._error_message
        )
    
    def __repr__(self) -> str:
        """String representation"""
        return (
            f"BinanceWebSocketClient("
            f"state={self._state.value}, "
            f"reconnects={self._reconnect_count}, "
            f"latency={self._latency_ms}ms"
            f")"
        )
