"""
Event Bus - Event-Driven Bridge Pattern

Giải quyết vấn đề Async/Sync mismatch giữa RealtimeService (Sync) và WebSocketManager (Async).

Pattern: Producer-Consumer với asyncio.Queue
- Producer: RealtimeService đẩy events vào queue (sync, non-blocking)
- Consumer: Broadcast Worker lấy events và broadcast qua WebSocket (async)

Lợi ích:
1. Decoupling hoàn toàn giữa Core Logic và I/O
2. Thread-safe communication (via call_soon_threadsafe)
3. Không phụ thuộc vào timing của client connection
4. Graceful handling khi không có clients

CRITICAL: Thread-Safety
- Binance WebSocket client chạy trong OS Thread riêng
- asyncio.Queue.put_nowait() KHÔNG thread-safe khi gọi từ thread khác
- Phải dùng loop.call_soon_threadsafe() để bridge giữa Thread và Async Loop
"""

import asyncio
import logging
import threading
from typing import Dict, Any, Optional, TYPE_CHECKING
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

if TYPE_CHECKING:
    from .websocket_manager import WebSocketManager

logger = logging.getLogger(__name__)


class EventType(Enum):
    """Types of events that can be broadcast."""
    CANDLE_UPDATE = "candle"      # 1m candle update (default)
    CANDLE_15M = "candle_15m"     # 15-minute candle update
    CANDLE_1H = "candle_1h"       # 1-hour candle update
    SIGNAL = "signal"
    STATUS = "status"
    ERROR = "error"
    STATE_CHANGE = "state_change"  # Task 11: Trading state machine state changes


@dataclass
class BroadcastEvent:
    """Event structure for the queue."""
    event_type: EventType
    data: Dict[str, Any]
    symbol: str = "btcusdt"
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for JSON serialization."""
        return {
            'type': self.event_type.value,
            'symbol': self.symbol,
            'timestamp': self.timestamp.isoformat(),
            **self.data
        }


class EventBus:
    """
    Central event bus for async communication.
    
    Singleton pattern - one queue for the entire application.
    """
    
    _instance: Optional['EventBus'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        # Main event queue - unlimited size for now
        # In production, consider maxsize to prevent memory issues
        self._queue: asyncio.Queue = asyncio.Queue()
        
        # Reference to the main event loop (set when worker starts)
        # CRITICAL: Needed for thread-safe publishing from Binance WS thread
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        
        # Statistics
        self._events_published = 0
        self._events_consumed = 0
        self._events_dropped = 0
        
        # Worker state
        self._worker_task: Optional[asyncio.Task] = None
        self._is_running = False
        
        self._initialized = True
        logger.info("EventBus initialized")
    
    def publish(self, event: BroadcastEvent) -> bool:
        """
        Publish event to queue - THREAD-SAFE (Bulletproof).
        
        This method can be called safely from:
        1. Async context (same event loop)
        2. External threads (e.g., Binance WebSocket thread)
        
        Uses call_soon_threadsafe() to bridge between Thread world and Async world.
        
        Args:
            event: BroadcastEvent to publish
            
        Returns:
            True if published successfully, False otherwise
        """
        try:
            # Case 1: Called from within the same async event loop
            try:
                running_loop = asyncio.get_running_loop()
                if self._loop and running_loop == self._loop:
                    # Same loop - safe to use put_nowait directly
                    self._queue.put_nowait(event)
                    self._events_published += 1
                    logger.debug(f"Event published (async): {event.event_type.value}")
                    return True
            except RuntimeError:
                # No running loop in current context - we're in a different thread
                pass
            
            # Case 2: Called from external thread (e.g., Binance WS thread)
            # CRITICAL: Must use call_soon_threadsafe to safely interact with async loop
            if self._loop and not self._loop.is_closed():
                self._loop.call_soon_threadsafe(self._safe_put, event)
                self._events_published += 1
                logger.debug(f"Event published (thread-safe): {event.event_type.value}")
                return True
            else:
                # Loop not ready yet - drop event
                self._events_dropped += 1
                logger.warning(f"Event dropped (loop not ready): {event.event_type.value}")
                return False
                
        except asyncio.QueueFull:
            self._events_dropped += 1
            logger.warning(f"Queue full, event dropped: {event.event_type.value}")
            return False
        except Exception as e:
            self._events_dropped += 1
            logger.error(f"Failed to publish event: {e}")
            return False
    
    def _safe_put(self, event: BroadcastEvent) -> None:
        """
        Internal method to safely put event into queue.
        Called via call_soon_threadsafe from external threads.
        """
        try:
            self._queue.put_nowait(event)
        except asyncio.QueueFull:
            self._events_dropped += 1
            logger.warning(f"Queue full in _safe_put: {event.event_type.value}")
    
    def publish_candle_update(self, candle_data: Dict[str, Any], symbol: str = "btcusdt") -> bool:
        """Convenience method to publish 1m candle update."""
        event = BroadcastEvent(
            event_type=EventType.CANDLE_UPDATE,
            data=candle_data,
            symbol=symbol
        )
        return self.publish(event)
    
    def publish_candle_15m(self, candle_data: Dict[str, Any], symbol: str = "btcusdt") -> bool:
        """
        Publish 15-minute candle update for multi-timeframe chart support.
        
        Called when 15m candle is updated or closed.
        
        Args:
            candle_data: Dict with OHLCV and indicators
            symbol: Trading symbol
        """
        event = BroadcastEvent(
            event_type=EventType.CANDLE_15M,
            data=candle_data,
            symbol=symbol
        )
        return self.publish(event)
    
    def publish_candle_1h(self, candle_data: Dict[str, Any], symbol: str = "btcusdt") -> bool:
        """
        Publish 1-hour candle update for multi-timeframe chart support.
        
        Called when 1h candle is updated or closed.
        
        Args:
            candle_data: Dict with OHLCV and indicators
            symbol: Trading symbol
        """
        event = BroadcastEvent(
            event_type=EventType.CANDLE_1H,
            data=candle_data,
            symbol=symbol
        )
        return self.publish(event)
    
    def publish_signal(self, signal_data: Dict[str, Any], symbol: str = "btcusdt") -> bool:
        """Convenience method to publish trading signal."""
        event = BroadcastEvent(
            event_type=EventType.SIGNAL,
            data={'signal': signal_data},
            symbol=symbol
        )
        return self.publish(event)
    
    def publish_state_change(self, state_data: Dict[str, Any], symbol: str = "btcusdt") -> bool:
        """
        Convenience method to publish state machine state change.
        
        Task 11: State change events for frontend state tracking.
        
        Args:
            state_data: Dict with state change info (from_state, to_state, reason, etc.)
            symbol: Trading symbol
            
        Returns:
            True if published successfully
        """
        event = BroadcastEvent(
            event_type=EventType.STATE_CHANGE,
            data={'state_change': state_data},
            symbol=symbol
        )
        return self.publish(event)
    
    async def start_worker(self, manager: 'WebSocketManager') -> None:
        """
        Start the broadcast worker.
        
        This should be called during FastAPI lifespan startup.
        CRITICAL: Captures the event loop reference for thread-safe publishing.
        
        Args:
            manager: WebSocketManager instance to broadcast to
        """
        if self._is_running:
            logger.warning("Worker already running")
            return
        
        # CRITICAL: Capture the event loop reference
        # This is needed for thread-safe publishing from Binance WS thread
        self._loop = asyncio.get_running_loop()
        logger.info(f"EventBus captured event loop: {self._loop}")
        
        self._is_running = True
        self._worker_task = asyncio.create_task(
            self._broadcast_worker(manager)
        )
        logger.info("🚀 Broadcast Worker Started (Thread-Safe Mode)")
    
    async def stop_worker(self) -> None:
        """Stop the broadcast worker gracefully."""
        self._is_running = False
        
        if self._worker_task:
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass
        
        # Clear loop reference
        self._loop = None
        logger.info("Broadcast Worker Stopped")
    
    async def _broadcast_worker(self, manager: 'WebSocketManager') -> None:
        """
        Background worker that consumes events and broadcasts to WebSocket clients.
        
        Runs continuously until stopped.
        """
        while self._is_running:
            try:
                # Wait for event from queue (async blocking)
                # Timeout to allow periodic health checks
                try:
                    event: BroadcastEvent = await asyncio.wait_for(
                        self._queue.get(),
                        timeout=5.0  # Check every 5 seconds
                    )
                except asyncio.TimeoutError:
                    # No events, continue loop
                    continue
                
                # Broadcast to all connected clients
                message = event.to_dict()
                sent_count = await manager.broadcast(message, symbol=event.symbol)
                
                self._events_consumed += 1
                self._queue.task_done()
                
                if sent_count > 0:
                    logger.debug(f"Broadcast {event.event_type.value} to {sent_count} clients")
                
            except asyncio.CancelledError:
                logger.info("Worker cancelled")
                break
            except Exception as e:
                logger.error(f"Worker error: {e}", exc_info=True)
                await asyncio.sleep(1)  # Prevent tight loop on errors
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get queue statistics."""
        return {
            'queue_size': self._queue.qsize(),
            'events_published': self._events_published,
            'events_consumed': self._events_consumed,
            'events_dropped': self._events_dropped,
            'worker_running': self._is_running,
            'loop_captured': self._loop is not None,
            'current_thread': threading.current_thread().name
        }


# Global singleton instance
_event_bus: Optional[EventBus] = None


def get_event_bus() -> EventBus:
    """Get or create the global EventBus instance."""
    global _event_bus
    if _event_bus is None:
        _event_bus = EventBus()
    return _event_bus
