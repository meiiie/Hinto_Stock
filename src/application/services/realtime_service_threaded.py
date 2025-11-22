"""
Threaded RealtimeService - Application Layer

Wrapper around RealtimeService that runs async operations in a background thread.
This allows Streamlit (synchronous) to work with async WebSocket connections.
"""

import asyncio
import threading
import logging
from typing import Optional, Dict, List, Callable
from datetime import datetime

from .realtime_service import RealtimeService
from .paper_trading_service import PaperTradingService
from ...domain.entities.candle import Candle
from ..signals import TradingSignal


class ThreadedRealtimeService:
    """
    Thread-safe wrapper for RealtimeService.
    
    Runs async operations in a dedicated background thread with its own event loop.
    Provides synchronous API for Streamlit to interact with.
    """
    
    def __init__(self, symbol: str = 'btcusdt', interval: str = '1m', buffer_size: int = 100, paper_service: Optional[PaperTradingService] = None):
        """
        Initialize threaded service.
        
        Args:
            symbol: Trading pair symbol
            interval: Candle interval
            buffer_size: Size of candle buffers
        """
        self.symbol = symbol
        self.interval = interval
        self.buffer_size = buffer_size
        self.paper_service = paper_service
        
        # Background thread and event loop
        self._thread: Optional[threading.Thread] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._stop_event = threading.Event()
        
        # Service instance (will be created in background thread)
        self._service: Optional[RealtimeService] = None
        
        # Logging
        self.logger = logging.getLogger(__name__)
    
    def start(self) -> None:
        """
        Start the service in a background thread.
        
        This creates a new thread with its own event loop and starts the WebSocket connection.
        """
        if self._thread and self._thread.is_alive():
            self.logger.warning("Service already running")
            return
        
        self.logger.info("Starting threaded real-time service...")
        
        # Reset stop event
        self._stop_event.clear()
        
        # Create and start background thread
        self._thread = threading.Thread(target=self._run_event_loop, daemon=True)
        self._thread.start()
        
        # Wait a bit for initialization
        import time
        time.sleep(2)
        
        self.logger.info("✅ Threaded service started")
    
    def _run_event_loop(self) -> None:
        """
        Run event loop in background thread.
        
        This method runs in a separate thread and manages the async event loop.
        """
        try:
            # Create new event loop for this thread
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
            
            # Create service instance
            self._service = RealtimeService(
                symbol=self.symbol,
                interval=self.interval,

                buffer_size=self.buffer_size,
                paper_service=self.paper_service
            )
            
            # Start service (async)
            self._loop.run_until_complete(self._service.start())
            
            # Keep loop running until stop is requested
            while not self._stop_event.is_set():
                self._loop.run_until_complete(asyncio.sleep(0.1))
            
            # Cleanup
            self._loop.run_until_complete(self._service.stop())
            
        except Exception as e:
            self.logger.error(f"Error in event loop thread: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
        finally:
            if self._loop:
                self._loop.close()
    
    def stop(self) -> None:
        """
        Stop the service and background thread.
        """
        if not self._thread or not self._thread.is_alive():
            self.logger.warning("Service not running")
            return
        
        self.logger.info("Stopping threaded service...")
        
        # Signal thread to stop
        self._stop_event.set()
        
        # Wait for thread to finish
        self._thread.join(timeout=5.0)
        
        self.logger.info("✅ Threaded service stopped")
    
    def is_running(self) -> bool:
        """Check if service is running."""
        return (
            self._thread is not None 
            and self._thread.is_alive() 
            and self._service is not None 
            and self._service.is_running()
        )
    
    def get_latest_data(self, timeframe: str = '1m') -> Optional[Candle]:
        """Get latest candle for specified timeframe."""
        if not self._service:
            return None
        return self._service.get_latest_data(timeframe)
    
    def get_candles(self, timeframe: str = '1m', limit: int = 100) -> List[Candle]:
        """Get recent candles for specified timeframe."""
        if not self._service:
            return []
        return self._service.get_candles(timeframe, limit)
    
    def get_latest_indicators(self, timeframe: str = '1m') -> Dict:
        """Get latest calculated indicators."""
        if not self._service:
            return {}
        return self._service.get_latest_indicators(timeframe)
    
    def get_current_signals(self) -> Optional[TradingSignal]:
        """Get current trading signal."""
        if not self._service:
            return None
        return self._service.get_current_signals()
    
    def get_status(self) -> Dict:
        """Get service status."""
        if not self._service:
            return {
                'is_running': False,
                'connection': {'is_connected': False},
                'data': {},
                'signals': {}
            }
        return self._service.get_status()
    
    def subscribe_signals(self, callback: Callable[[TradingSignal], None]) -> None:
        """Subscribe to trading signals."""
        if self._service:
            self._service.subscribe_signals(callback)
    
    def subscribe_updates(self, callback: Callable[[], None]) -> None:
        """Subscribe to data updates."""
        if self._service:
            self._service.subscribe_updates(callback)
    
    # Expose analyzers for direct access
    @property
    def rsi_monitor(self):
        """Get RSI monitor."""
        return self._service.rsi_monitor if self._service else None
    
    @property
    def volume_analyzer(self):
        """Get volume analyzer."""
        return self._service.volume_analyzer if self._service else None
    
    @property
    def signal_generator(self):
        """Get signal generator."""
        return self._service.signal_generator if self._service else None
    
    def __repr__(self) -> str:
        """String representation"""
        return (
            f"ThreadedRealtimeService("
            f"symbol={self.symbol}, "
            f"interval={self.interval}, "
            f"running={self.is_running()}"
            f")"
        )
