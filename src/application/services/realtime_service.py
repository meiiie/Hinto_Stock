"""
RealtimeService - Application Layer

Orchestrates real-time data flow and coordinates all components.

NOTE: This service uses Dependency Injection - all infrastructure
dependencies are injected via constructor, not created internally.
"""

import asyncio
import logging
import pandas as pd
from typing import Optional, Dict, List, Callable, TYPE_CHECKING
from datetime import datetime
from collections import deque

# Domain imports (allowed)
from ...domain.entities.candle import Candle
from ...domain.interfaces import (
    IWebSocketClient,
    IRestClient,
    IDataAggregator,
    IIndicatorCalculator,
    IVWAPCalculator,
    IBollingerCalculator,
    IStochRSICalculator,
    IADXCalculator,
    IATRCalculator,
    IVolumeSpikeDetector,
)

# Domain repository interface (for candle persistence - Phase 2)
from ...domain.repositories.market_data_repository import MarketDataRepository

# Application imports (allowed)
from ..analysis import VolumeAnalyzer, RSIMonitor
from ..signals import SignalGenerator, TradingSignal
from .entry_price_calculator import EntryPriceCalculator
from .tp_calculator import TPCalculator
from .stop_loss_calculator import StopLossCalculator
from ..analysis.trend_filter import TrendFilter, TrendDirection # SOTA: For HTF Confluence
from .confidence_calculator import ConfidenceCalculator
from .smart_entry_calculator import SmartEntryCalculator
from .paper_trading_service import PaperTradingService


class RealtimeService:
    """
    Real-time trading service that orchestrates all components.
    
    Responsibilities:
    - Manage WebSocket client lifecycle
    - Coordinate data aggregation
    - Trigger analysis and signal generation
    - Provide data access for dashboard
    - Handle errors and reconnection
    
    Data Flow:
    WebSocket → Aggregator → Analyzers → Signal Generator → Dashboard
    """
    
    def __init__(
        self,
        symbol: str = 'btcusdt',
        interval: str = '1m',
        buffer_size: int = 2000,
        paper_service: Optional[PaperTradingService] = None,
        # Injected dependencies (interfaces)
        websocket_client: Optional[IWebSocketClient] = None,
        rest_client: Optional[IRestClient] = None,
        aggregator: Optional[IDataAggregator] = None,
        talib_calculator: Optional[IIndicatorCalculator] = None,
        vwap_calculator: Optional[IVWAPCalculator] = None,
        bollinger_calculator: Optional[IBollingerCalculator] = None,
        stoch_rsi_calculator: Optional[IStochRSICalculator] = None,
        adx_calculator: Optional[IADXCalculator] = None,
        atr_calculator: Optional[IATRCalculator] = None,
        volume_spike_detector: Optional[IVolumeSpikeDetector] = None,
        signal_generator: Optional[SignalGenerator] = None,
        # SOTA FIX: Market data repository for candle persistence (Phase 2)
        market_data_repository: Optional[MarketDataRepository] = None,
        # SOTA FIX: Signal lifecycle service for persistence
        lifecycle_service: Optional['SignalLifecycleService'] = None,  # SignalLifecycleService (avoid circular import)
        # SOTA FIX: TrendFilter for HTF Confluence
        trend_filter: Optional[TrendFilter] = None,
        # CRITICAL FIX: SignalConfirmationService for whipsaw prevention
        signal_confirmation_service: Optional['SignalConfirmationService'] = None
    ):
        """
        Initialize real-time service with dependency injection.
        
        Args:
            symbol: Trading pair symbol (default: 'btcusdt')
            interval: WebSocket interval (default: '1m')
            buffer_size: Size of candle buffers (default: 2000)
            paper_service: Paper trading service (optional)
            
        Injected Dependencies (use DI container to provide these):
            websocket_client: WebSocket client implementation
            rest_client: REST API client implementation
            aggregator: Data aggregator implementation
            talib_calculator: Technical indicator calculator
            vwap_calculator: VWAP calculator
            bollinger_calculator: Bollinger Bands calculator
            stoch_rsi_calculator: Stochastic RSI calculator
            adx_calculator: ADX calculator
            atr_calculator: ATR calculator
            volume_spike_detector: Volume spike detector
            signal_generator: Signal generator (pre-configured)
        """
        self.symbol = symbol
        self.interval = interval
        self.buffer_size = buffer_size
        self.paper_service = paper_service
        
        # Store injected dependencies
        # If not provided, they will be created by DI container
        self.websocket_client = websocket_client
        self.rest_client = rest_client
        self.aggregator = aggregator
        self.volume_analyzer = VolumeAnalyzer(ma_period=20)
        self.rsi_monitor = RSIMonitor(period=6)
        
        # Store calculator references (injected)
        self.talib_calculator = talib_calculator
        self.vwap_calculator = vwap_calculator
        self.bollinger_calculator = bollinger_calculator
        self.stoch_rsi_calculator = stoch_rsi_calculator
        self.adx_calculator = adx_calculator
        self.atr_calculator = atr_calculator
        self.volume_spike_detector = volume_spike_detector
        
        # Application-layer calculators (created here, they're in Application layer)
        self.entry_calculator = EntryPriceCalculator()
        self.tp_calculator = TPCalculator()
        self.stop_loss_calculator = StopLossCalculator()
        self.confidence_calculator = ConfidenceCalculator()
        self.smart_entry_calculator = SmartEntryCalculator()
        
        # Signal generator (injected or will be set later)
        self.signal_generator = signal_generator
        
        # SOTA FIX: Market data repository for candle persistence (Phase 2)
        self._market_data_repository = market_data_repository
        
        # SOTA FIX: Signal lifecycle service for persistence
        self._lifecycle_service = lifecycle_service

        # SOTA FIX: TrendFilter for HTF Confluence
        self.trend_filter = trend_filter
        
        # CRITICAL FIX: SignalConfirmationService for whipsaw prevention
        self._signal_confirmation_service = signal_confirmation_service
        
        # Data storage (in-memory cache)
        self._latest_1m: Optional[Candle] = None
        self._latest_15m: Optional[Candle] = None
        self._latest_1h: Optional[Candle] = None
        self._latest_signal: Optional[TradingSignal] = None
        
        # Candle buffers for analysis
        self._candles_1m: deque = deque(maxlen=buffer_size)
        self._candles_15m: deque = deque(maxlen=buffer_size)
        self._candles_1h: deque = deque(maxlen=buffer_size)
        
        # Callbacks
        self._signal_callbacks: List[Callable] = []
        self._update_callbacks: List[Callable] = []
        
        # State
        self._is_running = False
        
        # EventBus for broadcasting events (set via set_event_bus)
        self._event_bus = None
        
        # Logging
        self.logger = logging.getLogger(__name__)
    
    def set_event_bus(self, event_bus) -> None:
        """
        Set the EventBus for broadcasting events.
        
        Called by main.py during startup to connect RealtimeService to EventBus.
        
        Args:
            event_bus: EventBus instance for broadcasting
        """
        self._event_bus = event_bus
        self.logger.info("✅ EventBus connected to RealtimeService")
    
    async def start(self, shared_client_mode: bool = False) -> None:
        """
        Start the real-time service.
        
        This will:
        1. Load historical data
        2. Connect to WebSocket (unless shared_client_mode=True)
        3. Start receiving real-time data
        4. Begin analysis and signal generation
        
        Args:
            shared_client_mode: If True, skip WebSocket connection (data comes from SharedBinanceClient)
        """
        if self._is_running:
            self.logger.warning("Service already running")
            return
        
        self.logger.info(f"Starting real-time service for {self.symbol} (shared_mode={shared_client_mode})")
        
        try:
            # Load historical data first
            self.logger.info("Loading historical data...")
            await self._load_historical_data()
            
            # Register aggregator callbacks
            self.aggregator.on_15m_complete(self._on_15m_complete)
            self.aggregator.on_1h_complete(self._on_1h_complete)
            
            # SOTA: Multi-Symbol Subscription (Active + Portfolio Watchlist)
            watchlist_symbols = {self.symbol.lower()}
            
            # Add portfolio positions to watchlist
            if self.paper_service:
                try:
                    positions = self.paper_service.get_positions()
                    for pos in positions:
                        watchlist_symbols.add(pos.symbol.lower())
                    self.logger.info(f"📋 Portfolio Watchlist: {watchlist_symbols}")
                except Exception as e:
                    self.logger.error(f"Failed to fetch portfolio symbols: {e}")

            if shared_client_mode:
                self.logger.info("📡 Using SharedBinanceClient for data streaming")
            else:
                # Legacy: Connect own WebSocket with ALL symbols
                # Subscribe to all unique symbols in watchlist
                # Intervals: 1m (Base), 15m (Signal), 1h (HTF)
                await self.websocket_client.connect(
                    symbols=list(watchlist_symbols),
                    intervals=['1m', '15m', '1h']
                )
            
            self._is_running = True
            self.logger.info("✅ Real-time service started successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to start service: {e}")
    
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
                    self.symbol, timeframe, limit
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
                            self._market_data_repository.save_candle_simple(candle, timeframe, self.symbol)
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

    async def _load_historical_data(self) -> None:
        """
        SOTA Fresh Load: Always fetch 500 latest candles from Binance on startup.
        
        FIX: Previous logic merged SQLite (old) + Binance (new), causing stale data.
        Now: ALWAYS fetch fresh candles from Binance, then persist for future sessions.
        
        Architecture:
        1. Fetch 500 latest from Binance REST API (source of truth)
        2. Populate in-memory buffers (L1 cache)
        3. Persist to SQLite for future fast-startup (L2 cache)
        
        This ensures charts always show the most current 400 candles.
        """
        try:
            self.logger.info("🚀 Loading historical candles (SOTA Fresh Mode)...")
            
            # SOTA: Load 500 candles for professional chart display
            # Frontend requests 400, plus 50 warm-up trim = 450 minimum
            CANDLE_LOAD_LIMIT = 500
            
            # 1. Load 1m candles - ALWAYS from Binance
            self.logger.info(f"📡 Fetching {CANDLE_LOAD_LIMIT} fresh 1m candles from Binance...")
            candles_1m = self.rest_client.get_klines(
                symbol=self.symbol,
                interval='1m',
                limit=CANDLE_LOAD_LIMIT
            )
            if candles_1m:
                # Clear buffer and populate with fresh data
                self._candles_1m.clear()
                for candle in candles_1m:
                    self._candles_1m.append(candle)
                    self.aggregator.add_candle_1m(candle, is_closed=True)
                self._latest_1m = candles_1m[-1]
                self.logger.info(f"✅ Loaded {len(candles_1m)} fresh 1m candles")
                
                # Persist to SQLite for future quick restarts
                if self._market_data_repository:
                    self._persist_candles_batch(candles_1m, '1m')
            else:
                self.logger.warning("⚠️ No 1m data from Binance, trying SQLite fallback...")
                candles_1m = self._load_candles_hybrid('1m', CANDLE_LOAD_LIMIT)
                for candle in candles_1m:
                    self._candles_1m.append(candle)
            
            # 2. Load 15m candles - ALWAYS from Binance
            self.logger.info(f"📡 Fetching {CANDLE_LOAD_LIMIT} fresh 15m candles from Binance...")
            candles_15m = self.rest_client.get_klines(
                symbol=self.symbol,
                interval='15m',
                limit=CANDLE_LOAD_LIMIT
            )
            if candles_15m and len(candles_15m) > 1:
                self._candles_15m.clear()
                completed_15m = candles_15m[:-1]  # Exclude incomplete
                for candle in completed_15m:
                    self._candles_15m.append(candle)
                self._latest_15m = completed_15m[-1]
                self.logger.info(f"✅ Loaded {len(completed_15m)} fresh 15m candles")
                
                # Persist to SQLite
                if self._market_data_repository:
                    self._persist_candles_batch(completed_15m, '15m')
            else:
                self.logger.warning("⚠️ No 15m data from Binance")
            
            # 3. Load 1h candles - ALWAYS from Binance
            self.logger.info(f"📡 Fetching {CANDLE_LOAD_LIMIT} fresh 1h candles from Binance...")
            candles_1h = self.rest_client.get_klines(
                symbol=self.symbol,
                interval='1h',
                limit=CANDLE_LOAD_LIMIT
            )
            if candles_1h and len(candles_1h) > 1:
                self._candles_1h.clear()
                completed_1h = candles_1h[:-1]
                for candle in completed_1h:
                    self._candles_1h.append(candle)
                self._latest_1h = completed_1h[-1]
                self.logger.info(f"✅ Loaded {len(completed_1h)} fresh 1h candles")
                
                # Persist to SQLite
                if self._market_data_repository:
                    self._persist_candles_batch(completed_1h, '1h')
            else:
                self.logger.warning("⚠️ No 1h data from Binance")
            
            self.logger.info("✅ Historical data loaded successfully (SOTA Fresh Mode)")
            
        except Exception as e:
            self.logger.error(f"❌ Error loading historical data: {e}")
            # Fallback to hybrid (SQLite + Binance) if fresh load fails
            self.logger.info("🔄 Falling back to hybrid load...")
            await self._load_historical_data_hybrid_fallback()
    
    async def _load_historical_data_hybrid_fallback(self) -> None:
        """Fallback hybrid load if fresh Binance load fails."""
        try:
            CANDLE_LOAD_LIMIT = 500
            
            candles_1m = self._load_candles_hybrid('1m', CANDLE_LOAD_LIMIT)
            for candle in candles_1m:
                self._candles_1m.append(candle)
            if candles_1m:
                self._latest_1m = candles_1m[-1]
                
            candles_15m = self._load_candles_hybrid('15m', CANDLE_LOAD_LIMIT)
            if candles_15m:
                for candle in candles_15m[:-1]:
                    self._candles_15m.append(candle)
                self._latest_15m = candles_15m[-2] if len(candles_15m) > 1 else None
                
            candles_1h = self._load_candles_hybrid('1h', CANDLE_LOAD_LIMIT)
            if candles_1h:
                for candle in candles_1h[:-1]:
                    self._candles_1h.append(candle)
                self._latest_1h = candles_1h[-2] if len(candles_1h) > 1 else None
                
            self.logger.info("✅ Hybrid fallback load complete")
        except Exception as e:
            self.logger.error(f"Hybrid fallback also failed: {e}")
    
    def _persist_candles_batch(self, candles: List[Candle], timeframe: str) -> None:
        """Persist a batch of candles to SQLite asynchronously."""
        if not self._market_data_repository or not candles:
            return
            
        saved_count = 0
        for candle in candles:
            try:
                self._market_data_repository.save_candle_simple(candle, timeframe, self.symbol)
                saved_count += 1
            except Exception:
                pass  # Ignore duplicates
        
        if saved_count > 0:
            self.logger.debug(f"💾 Persisted {saved_count} {timeframe} candles to SQLite")
    
    async def stop(self) -> None:
        """
        Stop the real-time service.
        
        This will:
        1. Disconnect from WebSocket
        2. Clear buffers
        3. Reset state
        """
        if not self._is_running:
            self.logger.warning("Service not running")
            return
        
        self.logger.info("Stopping real-time service...")
        
        try:
            # Disconnect WebSocket
            await self.websocket_client.disconnect()
            
            self._is_running = False
            self.logger.info("✅ Real-time service stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping service: {e}")
    
    def on_candle_update(self, candle: Candle, metadata: Dict) -> None:
        """
        Public callback for SharedBinanceClient data routing.
        
        SOTA: This is called by SharedBinanceClient when data arrives
        for this service's symbol. Delegates to internal _on_candle_received.
        
        Args:
            candle: Candle entity
            metadata: Metadata (is_closed, symbol, interval, etc.)
        """
        # Verify this candle is for our symbol
        incoming_symbol = metadata.get('symbol', '').lower()
        if incoming_symbol and incoming_symbol != self.symbol.lower():
            self.logger.debug(f"Ignoring candle for {incoming_symbol} (expected {self.symbol})")
            return
        
        self._on_candle_received(candle, metadata)
    
    def _on_candle_received(self, candle: Candle, metadata: Dict) -> None:
        """
        Callback when candle is received from WebSocket.
        
        SOTA: With multi-stream, this receives 1m, 15m, AND 1h candles.
        Route based on metadata.interval.
        
        Args:
            candle: Candle entity
            metadata: Metadata (is_closed, symbol, interval, etc.)
        """
        interval = metadata.get('interval', '1m')
        is_closed = metadata.get('is_closed', False)
        
        # Use metadata for symbol info instead of accessing candle.symbol
        candle_symbol = metadata.get('symbol', self.symbol)
        self.logger.info(f"🕯️ [{interval}] Candle: {candle.close:.2f} closed={is_closed} symbol={candle_symbol}")
        
        # SOTA: Check if this is the ACTIVE symbol
        is_active_symbol = (candle_symbol.lower() == self.symbol.lower())
        
        # SOTA: Always persist ALL incoming data (for Portfolio PnL)
        # This acts as the "Background Price Oracle" feeder
        if self._market_data_repository:
             try:
                 # 1. Update In-Memory Hot Cache (Fastest, for live PnL)
                 self._market_data_repository.update_realtime_price(candle_symbol, candle.close)
                 
                 # 2. Persist to DB if closed (Slower, for history)
                 if is_closed:
                    self._market_data_repository.save_candle_simple(candle, interval, candle_symbol.lower())
             except Exception as e:
                 pass # Ignore persistence errors to keep stream alive

        # SOTA Multi-Stream Routing
        if interval == '15m':
            self._handle_15m_candle(candle, is_closed)
            return
        elif interval == '1h':
            self._handle_1h_candle(candle, is_closed)
            return
            
        # --- 1m Processing (Base Timeframe) ---
        
        # CRITICAL SOTA FILTER: Only process signals/chart updates for the ACTIVE symbol.
        # Passive portfolio symbols are handled above (persistence only) and then ignored here.
        if not is_active_symbol:
             # SOTA FIX: Broadcast "Ticker" update for portfolio symbols
             # This allows the Frontend Portfolio to update PnL in realtime
             if self._event_bus:
                 asyncio.create_task(self.connection_manager.broadcast_json({
                     "type": "candle", # Frontend treats this as candle update -> updates store
                     "symbol": candle_symbol, # e.g. 'SOLUSDT'
                     "data": {
                         "open": candle.open,
                         "high": candle.high,
                         "low": candle.low,
                         "close": candle.close, # Used for PnL
                         "time": int(candle.timestamp.timestamp()) if hasattr(candle.timestamp, 'timestamp') else 0,
                         # No indicators for passive symbols to save bandwidth/CPU
                     }
                 }, self.symbol)) # Broadcast to ACTIVE channel (e.g. BTC)
             return

        # Default: 1m candle processing for ACTIVE symbol
        # Check if this is a NEW candle (different timestamp from current latest)
        
        if self._latest_1m and candle.timestamp != self._latest_1m.timestamp:
            # New candle started - the previous one is now complete
            self.logger.debug(f"New candle detected: {candle.timestamp} - Saving previous candle")
            self._candles_1m.append(self._latest_1m)
            self.logger.debug(f"Buffer size: {len(self._candles_1m)}")
            
            # Add to aggregator
            self.aggregator.add_candle_1m(self._latest_1m, is_closed=True)
            
            # Generate signals
            self._generate_signals()
        
        # Always update latest 1m candle (for real-time display of ACTIVE symbol)
        self._latest_1m = candle
        
        # SOTA FIX: Broadcast candle update via EventBus to frontend WebSocket
        if self._event_bus:
            # Get latest indicators for the candle
            indicators = self.get_latest_indicators('1m')
            candle_data = {
                'open': candle.open,
                'high': candle.high, 
                'low': candle.low,
                'close': candle.close,
                'volume': candle.volume,
                'timestamp': candle.timestamp.isoformat() if hasattr(candle.timestamp, 'isoformat') else str(candle.timestamp),
                'time': int(candle.timestamp.timestamp()) if hasattr(candle.timestamp, 'timestamp') else 0,
                'vwap': indicators.get('vwap'),
                'bollinger': indicators.get('bollinger'),
                'rsi': indicators.get('rsi'),
            }
            self._event_bus.publish_candle_update(candle_data, symbol=self.symbol)
            self.logger.debug(f"📡 EventBus: Published 1m candle {candle.close:.2f}")
        
        # Paper Engine Matching (Run on every tick/candle update)
        if self.paper_service:
            self.paper_service.process_market_data(
                current_price=candle.close,
                high=candle.high,
                low=candle.low,
                symbol=self.symbol
            )
        
        # Also add if explicitly closed by Binance
        if is_closed and (not self._candles_1m or candle.timestamp != self._candles_1m[-1].timestamp):
            self.logger.debug(f"Candle explicitly closed: {candle.timestamp}")
            self._candles_1m.append(candle)
            self.logger.debug(f"Buffer size: {len(self._candles_1m)}")
            
            # Add to aggregator
            self.aggregator.add_candle_1m(candle, is_closed=True)
            
            # Generate signals
            self._generate_signals()
        
        # Notify update callbacks
        self.logger.info(f"📢 Calling _notify_update_callbacks with {len(self._update_callbacks)} callbacks")
        self._notify_update_callbacks()
    
    def _handle_15m_candle(self, candle: Candle, is_closed: bool) -> None:
        """
        SOTA Multi-Stream: Handle 15m candle from Binance combined stream.
        
        This receives NATIVE 15m candles directly from Binance WebSocket.
        Broadcasts to frontend for realtime chart updates.
        
        Args:
            candle: 15m Candle entity
            is_closed: Whether candle is closed
        """
        # Update latest 15m candle
        self._latest_15m = candle
        
        # If closed, add to buffer and persist
        if is_closed:
            self._candles_15m.append(candle)
            
            # Persist to SQLite
            if self._market_data_repository:
                try:
                    self._market_data_repository.save_candle_simple(candle, '15m', self.symbol)
                    self.logger.debug(f"📦 Persisted 15m candle from stream: {candle.timestamp}")
                except Exception as e:
                    self.logger.error(f"Failed to persist 15m candle: {e}")
        
        # Broadcast to frontend (both forming and closed candles)
        if self._event_bus:
            candle_data = {
                'open': candle.open,
                'high': candle.high,
                'low': candle.low,
                'close': candle.close,
                'volume': candle.volume,
                'timestamp': candle.timestamp.isoformat() if hasattr(candle.timestamp, 'isoformat') else str(candle.timestamp),
                'time': int(candle.timestamp.timestamp()) if hasattr(candle.timestamp, 'timestamp') else 0,
            }
            self._event_bus.publish_candle_15m(candle_data, symbol=self.symbol)
            self.logger.debug(f"📡 EventBus: Published 15m candle {candle.close:.2f} (closed={is_closed})")
    
    def _handle_1h_candle(self, candle: Candle, is_closed: bool) -> None:
        """
        SOTA Multi-Stream: Handle 1h candle from Binance combined stream.
        
        This receives NATIVE 1h candles directly from Binance WebSocket.
        Broadcasts to frontend for realtime chart updates.
        
        Args:
            candle: 1h Candle entity
            is_closed: Whether candle is closed
        """
        # Update latest 1h candle
        self._latest_1h = candle
        
        # If closed, add to buffer and persist
        if is_closed:
            self._candles_1h.append(candle)
            
            # Persist to SQLite
            if self._market_data_repository:
                try:
                    self._market_data_repository.save_candle_simple(candle, '1h', self.symbol)
                    self.logger.debug(f"📦 Persisted 1h candle from stream: {candle.timestamp}")
                except Exception as e:
                    self.logger.error(f"Failed to persist 1h candle: {e}")
        
        # Broadcast to frontend (both forming and closed candles)
        if self._event_bus:
            candle_data = {
                'open': candle.open,
                'high': candle.high,
                'low': candle.low,
                'close': candle.close,
                'volume': candle.volume,
                'timestamp': candle.timestamp.isoformat() if hasattr(candle.timestamp, 'isoformat') else str(candle.timestamp),
                'time': int(candle.timestamp.timestamp()) if hasattr(candle.timestamp, 'timestamp') else 0,
            }
            self._event_bus.publish_candle_1h(candle_data, symbol=self.symbol)
            self.logger.debug(f"📡 EventBus: Published 1h candle {candle.close:.2f} (closed={is_closed})")
    
    def _on_15m_complete(self, candle: Candle) -> None:
        """
        Callback when 15m candle is completed.
        
        Args:
            candle: Completed 15m candle
        """
        self.logger.info(f"15m candle completed: {candle.timestamp}")
        
        self._latest_15m = candle
        self._candles_15m.append(candle)
        
        # SOTA FIX: Persist closed 15m candles to SQLite (Phase 2)
        if self._market_data_repository:
            try:
                self._market_data_repository.save_candle_simple(candle, '15m', self.symbol)
                self.logger.debug(f"📦 Persisted 15m candle: {candle.timestamp}")
            except Exception as e:
                self.logger.error(f"Failed to persist 15m candle: {e}")
        
        # SOTA FIX: Broadcast 15m candle via EventBus to frontend
        if self._event_bus:
            candle_data = {
                'open': candle.open,
                'high': candle.high,
                'low': candle.low,
                'close': candle.close,
                'volume': candle.volume,
                'timestamp': candle.timestamp.isoformat() if hasattr(candle.timestamp, 'isoformat') else str(candle.timestamp),
                'time': int(candle.timestamp.timestamp()) if hasattr(candle.timestamp, 'timestamp') else 0,
            }
            self._event_bus.publish_candle_15m(candle_data, symbol=self.symbol)
            self.logger.debug(f"📡 EventBus: Published 15m candle {candle.close:.2f}")
        
        # Generate signals on 15m timeframe
        if len(self._candles_15m) >= 20:
            self._generate_signals_15m()
    
    def _on_1h_complete(self, candle: Candle) -> None:
        """
        Callback when 1h candle is completed.
        
        Args:
            candle: Completed 1h candle
        """
        self.logger.info(f"1h candle completed: {candle.timestamp}")
        
        self._latest_1h = candle
        self._candles_1h.append(candle)
        
        # SOTA FIX: Persist closed 1h candles to SQLite (Phase 2)
        if self._market_data_repository:
            try:
                self._market_data_repository.save_candle_simple(candle, '1h', self.symbol)
                self.logger.debug(f"📦 Persisted 1h candle: {candle.timestamp}")
            except Exception as e:
                self.logger.error(f"Failed to persist 1h candle: {e}")
        
        # SOTA FIX: Broadcast 1h candle via EventBus to frontend
        if self._event_bus:
            candle_data = {
                'open': candle.open,
                'high': candle.high,
                'low': candle.low,
                'close': candle.close,
                'volume': candle.volume,
                'timestamp': candle.timestamp.isoformat() if hasattr(candle.timestamp, 'isoformat') else str(candle.timestamp),
                'time': int(candle.timestamp.timestamp()) if hasattr(candle.timestamp, 'timestamp') else 0,
            }
            self._event_bus.publish_candle_1h(candle_data, symbol=self.symbol)
            self.logger.debug(f"📡 EventBus: Published 1h candle {candle.close:.2f}")
        
        # Generate signals on 1h timeframe
        if len(self._candles_1h) >= 20:
            self._generate_signals_1h()
    
    def _generate_signals(self) -> None:
        """Generate trading signals based on current data."""
        if len(self._candles_1m) < 20:
            return
        
        try:
            signal = self.signal_generator.generate_signal(
                list(self._candles_1m),
                symbol=self.symbol
            )
            
            if signal and signal.signal_type.value != 'neutral':
                # CRITICAL FIX: Use SignalConfirmationService to prevent whipsaw
                # Requires 2 consecutive signals in same direction
                if self._signal_confirmation_service:
                    confirmed_signal = self._signal_confirmation_service.process_signal(
                        self.symbol, signal
                    )
                    
                    if not confirmed_signal:
                        # Signal pending confirmation - don't execute yet
                        self.logger.debug(
                            f"📋 Signal {signal.signal_type.value} pending confirmation"
                        )
                        return
                    
                    # Use confirmed signal (may have better entry price)
                    signal = confirmed_signal
                    self.logger.info(f"🎯 CONFIRMED signal executing: {signal.signal_type.value}")
                
                self._latest_signal = signal
                self.logger.info(f"Signal generated: {signal}")
                
                # SOTA FIX: Save signal FIRST to get signal_id
                saved_signal = self._notify_signal_callbacks(signal)
                
                # Send to Paper Engine (creates order)
                if self.paper_service:
                    self.paper_service.on_signal_received(signal, self.symbol)
                    
                    # SOTA FIX: Link signal to order via mark_executed
                    if saved_signal and self._lifecycle_service:
                        try:
                            pending_orders = self.paper_service.repo.get_pending_orders()
                            for order in pending_orders:
                                if order.symbol.lower() == self.symbol.lower():
                                    self._lifecycle_service.mark_executed(saved_signal.id, order.id)
                                    self.logger.info(f"🔗 Signal {saved_signal.id[:8]}... linked to order {order.id[:8]}...")
                                    break
                        except Exception as e:
                            self.logger.error(f"Error linking signal to order: {e}")
                
        except Exception as e:
            self.logger.error(f"Error generating signals: {e}")
    
    def _generate_signals_15m(self) -> None:
        """Generate signals on 15m timeframe."""
        try:
            # SOTA: HTF Confluence (Check 1H Trend)
            htf_trend = None
            if self.trend_filter and len(self._candles_1h) >= 50: # Need 50 for EMA50
                htf_trend = self.trend_filter.get_trend_direction(list(self._candles_1h))
                self.logger.debug(f"HTF Trend (1h): {htf_trend.value}")

            signal = self.signal_generator.generate_signal(
                list(self._candles_15m),
                symbol=self.symbol,
                htf_trend=htf_trend
            )
            
            if signal and signal.signal_type.value != 'neutral':
                self.logger.info(f"15m Signal: {signal}")
                self._notify_signal_callbacks(signal)
                
        except Exception as e:
            self.logger.error(f"Error generating 15m signals: {e}")
    
    def _generate_signals_1h(self) -> None:
        """Generate signals on 1h timeframe."""
        try:
            signal = self.signal_generator.generate_signal(
                list(self._candles_1h),
                symbol=self.symbol
            )
            
            if signal and signal.signal_type.value != 'neutral':
                self.logger.info(f"1h Signal: {signal}")
                self._notify_signal_callbacks(signal)
                
        except Exception as e:
            self.logger.error(f"Error generating 1h signals: {e}")

    
    def _notify_signal_callbacks(self, signal: TradingSignal) -> Optional[TradingSignal]:
        """
        Notify all signal callbacks, persist to DB, and broadcast via EventBus.
        
        SOTA FIX: Returns saved signal for linking with orders.
        
        Returns:
            Optional[TradingSignal]: The saved signal with ID, or None if not saved
        """
        # DEBUG: Log signal and lifecycle service status
        self.logger.info(f"🔔 Signal callback: {signal.signal_type.value} @ ${signal.price:.2f} (lifecycle_service: {'OK' if self._lifecycle_service else 'NONE'})")
        
        saved_signal = None
        
        # 1. SOTA FIX: Save signal to database via lifecycle service
        if self._lifecycle_service:
            try:
                saved_signal = self._lifecycle_service.register_signal(signal)
                self.logger.info(f"💾 Signal persisted: {saved_signal.id if saved_signal else 'none'}")
            except Exception as e:
                self.logger.error(f"Error persisting signal: {e}")
        
        # 2. SOTA FIX: Broadcast signal via EventBus to frontend
        if self._event_bus:
            try:
                signal_data = {
                    'id': getattr(signal, 'id', None) or (saved_signal.id if saved_signal else None),
                    'signal_type': signal.signal_type.value,
                    'price': signal.price,
                    'entry_price': signal.entry_price,
                    'stop_loss': signal.stop_loss,
                    'tp_levels': signal.tp_levels,
                    'confidence': signal.confidence,
                    'timeframe': '1m',  # SOTA FIX: TradingSignal has no timeframe field
                    'timestamp': signal.timestamp.isoformat() if signal.timestamp else None,
                    'meta': getattr(signal, 'meta', {}),
                }
                self._event_bus.publish_signal(signal_data, symbol=self.symbol)
                self.logger.info(f"📡 Signal broadcasted: {signal.signal_type.value}")
            except Exception as e:
                self.logger.error(f"Error broadcasting signal: {e}")
        
        # 3. Legacy: Notify registered callbacks
        for callback in self._signal_callbacks:
            try:
                callback(signal)
            except Exception as e:
                self.logger.error(f"Error in signal callback: {e}")
        
        return saved_signal
    
    def _notify_update_callbacks(self) -> None:
        """Notify all update callbacks."""
        if self._update_callbacks:
            self.logger.debug(f"Notifying {len(self._update_callbacks)} update callbacks")
        for callback in self._update_callbacks:
            try:
                callback()
            except Exception as e:
                self.logger.error(f"Error in update callback: {e}", exc_info=True)
    
    # Public API for dashboard
    
    def get_latest_data(self, timeframe: str = '1m') -> Optional[Candle]:
        """
        Get latest candle for specified timeframe.
        
        Args:
            timeframe: '1m', '15m', or '1h'
        
        Returns:
            Latest Candle or None
        """
        if timeframe == '1m':
            return self._latest_1m
        elif timeframe == '15m':
            return self._latest_15m
        elif timeframe == '1h':
            return self._latest_1h
        else:
            return None
    
    def get_current_signals(self) -> Optional[TradingSignal]:
        """
        Get current trading signal.
        
        Returns:
            Latest TradingSignal or None
        """
        return self._latest_signal
    
    def get_candles(self, timeframe: str = '1m', limit: int = 100) -> List[Candle]:
        """
        Get recent candles for specified timeframe.
        
        Args:
            timeframe: '1m', '15m', or '1h'
            limit: Maximum number of candles to return
        
        Returns:
            List of Candles
        """
        if timeframe == '1m':
            candles = list(self._candles_1m)
        elif timeframe == '15m':
            candles = list(self._candles_15m)
        elif timeframe == '1h':
            candles = list(self._candles_1h)
        else:
            return []
        
        return candles[-limit:] if len(candles) > limit else candles
    
    def get_latest_indicators(self, timeframe: str = '1m') -> Dict[str, float]:
        """
        Get latest indicator values for dashboard display.
        
        Args:
            timeframe: '1m', '15m', or '1h'
            
        Returns:
            Dict with indicator values (rsi, ema_7, ema_25, etc.)
        """
        candles = self.get_candles(timeframe, limit=100)
        
        # CRITICAL FIX: Append current forming candle for real-time price
        if timeframe == '1m' and self._latest_1m:
            # Only append if it's not already in the list (timestamps match)
            if not candles or candles[-1].timestamp != self._latest_1m.timestamp:
                candles.append(self._latest_1m)
                
        if not candles or len(candles) < 20:
            return {}
            
        try:
            # Convert to DataFrame
            df = pd.DataFrame({
                'open': [c.open for c in candles],
                'high': [c.high for c in candles],
                'low': [c.low for c in candles],
                'close': [c.close for c in candles],
                'volume': [c.volume for c in candles]
            })
            
            if timeframe == '1h':
                # Debug logging for 1h timeframe
                pass
            
            # Calculate indicators
            try:
                result_df = self.talib_calculator.calculate_all(df)
            except Exception as e:
                self.logger.error(f"TALib calculation failed for {timeframe}: {e}")
                result_df = df.copy()
            
            # Calculate additional Trend Pullback indicators
            # VWAP
            vwap_series = self.vwap_calculator.calculate_vwap_series(candles)
            if vwap_series is not None:
                result_df['vwap'] = vwap_series.values
            else:
                result_df['vwap'] = 0.0
            
            # Bollinger Bands
            bb_result = self.bollinger_calculator.calculate_bands(candles)
            if bb_result:
                result_df['bb_upper'] = bb_result.upper_band
                result_df['bb_middle'] = bb_result.middle_band
                result_df['bb_lower'] = bb_result.lower_band
            else:
                result_df['bb_upper'] = 0.0
                result_df['bb_middle'] = 0.0
                result_df['bb_lower'] = 0.0
            
            # StochRSI
            stoch_result = self.stoch_rsi_calculator.calculate_stoch_rsi(candles)
            if stoch_result:
                result_df['stoch_k'] = stoch_result.k_value
                result_df['stoch_d'] = stoch_result.d_value
                # Add nested dict for frontend compatibility
                result_df['stoch_rsi'] = [{'k': stoch_result.k_value, 'd': stoch_result.d_value}] * len(result_df)
            else:
                result_df['stoch_k'] = 0.0
                result_df['stoch_d'] = 0.0
                result_df['stoch_rsi'] = [{'k': 0.0, 'd': 0.0}] * len(result_df)
            
            # Return latest values as dict
            if not result_df.empty:
                # Handle NaN values safely for JSON serialization/display
                latest = result_df.iloc[-1].to_dict()
                
                # Map specific keys for frontend/demo compatibility
                if 'rsi_6' in latest:
                    latest['rsi'] = latest['rsi_6']
                
                # Construct nested objects for Dashboard
                
                # 1. Bollinger Bands
                if bb_result:
                    latest['bollinger'] = {
                        'upper_band': bb_result.upper_band,
                        'middle_band': bb_result.middle_band,
                        'lower_band': bb_result.lower_band,
                        'bandwidth': bb_result.bandwidth,
                        'percent_b': bb_result.percent_b
                    }
                
                # 2. StochRSI
                if stoch_result:
                    latest['stoch_rsi'] = {
                        'k': stoch_result.k_value,
                        'd': stoch_result.d_value,
                        'zone': stoch_result.zone.value
                    }
                else:
                    # Debug logging if StochRSI is missing
                    self.logger.warning(f"StochRSI failed for {timeframe}. Candles: {len(candles)}. Min req: {self.stoch_rsi_calculator.rsi_period + self.stoch_rsi_calculator.stoch_period + self.stoch_rsi_calculator.k_period + self.stoch_rsi_calculator.d_period}")
                
                # 3. Liquidity Zones (Volume Upgrade)
                if self.signal_generator.liquidity_zone_detector:
                    try:
                        # Use same logic as SignalGenerator to get latest zones
                        atr_val = latest.get('atr')
                        zones_result = self.signal_generator.liquidity_zone_detector.detect_zones(
                            candles, 
                            current_price=latest['close'], 
                            atr_value=atr_val
                        )
                        if zones_result:
                            latest['liquidity_zones'] = zones_result.to_dict()
                    except Exception as e:
                        self.logger.warning(f"Failed to get liquidity zones: {e}")

                # 4. SFP (SOTA)
                if self.signal_generator.sfp_detector:
                    try:
                        sfp_result = self.signal_generator.sfp_detector.detect(candles)
                        if sfp_result.is_valid:
                            latest['sfp'] = sfp_result.to_dict()
                    except Exception as e:
                        self.logger.warning(f"Failed to get SFP: {e}")

                # 5. Momentum Velocity (SOTA)
                if self.signal_generator.momentum_velocity_calculator:
                    try:
                        velocity_res = self.signal_generator.momentum_velocity_calculator.calculate(candles)
                        if velocity_res:
                            latest['velocity'] = {
                                'value': float(velocity_res.velocity),
                                'is_fomo': bool(velocity_res.is_fomo_spike),
                                'is_crash': bool(velocity_res.is_crash_drop)
                            }
                    except Exception as e:
                        self.logger.warning(f"Failed to get Velocity: {e}")

                return {k: (v if pd.notna(v) else 0.0) for k, v in latest.items()}
            return {}
        except Exception as e:
            self.logger.error(f"Error calculating indicators: {e}")
            return {}

    def get_historical_data_with_indicators(
        self, 
        timeframe: str = '1m', 
        limit: int = 1000,
        candles: Optional[List[Candle]] = None
    ) -> List[Dict]:
        """
        Get historical candles with calculated indicators.
        
        SOTA: Accepts optional pre-loaded candles (e.g., from SQLite) to calculate
        indicators without fetching from buffer or API.
        
        Args:
            timeframe: '1m', '15m', or '1h'
            limit: Number of candles
            candles: Optional pre-loaded candle list (for SQLite data)
            
        Returns:
            List of dicts with candle data and indicators
        """
        # Use provided candles or fetch from buffer
        if candles is None:
            candles = self.get_candles(timeframe, limit=limit)
        
        # Append current forming candle if available (for 1m)
        if timeframe == '1m' and self._latest_1m:
            if not candles or candles[-1].timestamp != self._latest_1m.timestamp:
                candles.append(self._latest_1m)
                
        if not candles:
            return []
            
        try:
            # Convert to DataFrame for calculation
            df = pd.DataFrame({
                'open': [c.open for c in candles],
                'high': [c.high for c in candles],
                'low': [c.low for c in candles],
                'close': [c.close for c in candles],
                'volume': [c.volume for c in candles]
            })
            
            # Calculate indicators
            # VWAP
            vwap_series = self.vwap_calculator.calculate_vwap_series(candles)
            
            # Bollinger Bands - use series method for arrays
            bb_series = self.bollinger_calculator.calculate_bands_series(candles)
            
            # Prepare result list
            result = []
            for i, candle in enumerate(candles):
                # Handle VWAP - can be Series or scalar
                if vwap_series is not None:
                    try:
                        val = vwap_series.iloc[i] if hasattr(vwap_series, 'iloc') else vwap_series
                        # SOTA: Explicit NaN check
                        vwap_val = float(val) if not pd.isna(val) else 0.0
                    except (IndexError, TypeError):
                        vwap_val = 0.0
                else:
                    vwap_val = 0.0
                
                # Handle Bollinger Bands - now using series result
                if bb_series:
                    try:
                        bb_upper = bb_series.upper_band[i] if i < len(bb_series.upper_band) else 0.0
                        bb_lower = bb_series.lower_band[i] if i < len(bb_series.lower_band) else 0.0
                        bb_middle = bb_series.middle_band[i] if i < len(bb_series.middle_band) else 0.0
                    except (IndexError, TypeError):
                        bb_upper = bb_lower = bb_middle = 0.0
                else:
                    bb_upper = bb_lower = bb_middle = 0.0
                
                item = {
                    'time': int(candle.timestamp.timestamp()), # Seconds for Lightweight Charts
                    'open': candle.open,
                    'high': candle.high,
                    'low': candle.low,
                    'close': candle.close,
                    'volume': candle.volume,
                    'vwap': vwap_val,
                    'bb_upper': bb_upper,
                    'bb_lower': bb_lower,
                    'bb_middle': bb_middle
                }
                result.append(item)
                
            return result
            
        except Exception as e:
            self.logger.error(f"Error calculating historical indicators: {e}")
            return []
    
    def subscribe_signals(self, callback: Callable[[TradingSignal], None]) -> None:
        """
        Subscribe to trading signals.
        
        Args:
            callback: Function to call when signal is generated
        """
        self._signal_callbacks.append(callback)
        self.logger.debug(f"Added signal callback (total: {len(self._signal_callbacks)})")
    
    def subscribe_updates(self, callback: Callable[[], None]) -> None:
        """
        Subscribe to data updates.
        
        Args:
            callback: Function to call when data updates
        """
        self._update_callbacks.append(callback)
        self.logger.info(f"✅ Added update callback (total: {len(self._update_callbacks)})")
    
    def get_status(self) -> Dict:
        """
        Get service status.
        
        Returns:
            Dict with status information
        """
        connection_status = self.websocket_client.get_connection_status()
        
        return {
            'is_running': self._is_running,
            'connection': {
                'is_connected': connection_status.is_connected,
                'state': connection_status.state.value,
                'latency_ms': connection_status.latency_ms,
                'reconnect_count': connection_status.reconnect_count
            },
            'data': {
                '1m_candles': len(self._candles_1m),
                '15m_candles': len(self._candles_15m),
                '1h_candles': len(self._candles_1h),
                'latest_1m': self._latest_1m.timestamp if self._latest_1m else None,
                'latest_15m': self._latest_15m.timestamp if self._latest_15m else None,
                'latest_1h': self._latest_1h.timestamp if self._latest_1h else None
            },
            'signals': {
                'latest': str(self._latest_signal) if self._latest_signal else None
            }
        }
    
    def is_running(self) -> bool:
        """Check if service is running."""
        return self._is_running
    
    def __repr__(self) -> str:
        """String representation"""
        return (
            f"RealtimeService("
            f"symbol={self.symbol}, "
            f"interval={self.interval}, "
            f"running={self._is_running}"
            f")"
        )
