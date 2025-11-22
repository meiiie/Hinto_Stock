"""
RealtimeService - Application Layer

Orchestrates real-time data flow and coordinates all components.
"""

import asyncio
import logging
import pandas as pd
from typing import Optional, Dict, List, Callable
from datetime import datetime
from collections import deque

from ...domain.entities.candle import Candle
from ...infrastructure.websocket import BinanceWebSocketClient
from ...infrastructure.aggregation import DataAggregator
from ...infrastructure.api.binance_rest_client import BinanceRestClient
from ..analysis import VolumeAnalyzer, RSIMonitor
from ..signals import SignalGenerator, TradingSignal
from ...infrastructure.indicators.talib_calculator import TALibCalculator
from ...infrastructure.indicators.vwap_calculator import VWAPCalculator
from ...infrastructure.indicators.bollinger_calculator import BollingerCalculator
from ...infrastructure.indicators.stoch_rsi_calculator import StochRSICalculator
from .entry_price_calculator import EntryPriceCalculator
from .tp_calculator import TPCalculator
from .stop_loss_calculator import StopLossCalculator
from .confidence_calculator import ConfidenceCalculator
from .smart_entry_calculator import SmartEntryCalculator
from ...infrastructure.indicators.volume_spike_detector import VolumeSpikeDetector
from ...infrastructure.indicators.adx_calculator import ADXCalculator
from ...infrastructure.indicators.adx_calculator import ADXCalculator
from ...infrastructure.indicators.atr_calculator import ATRCalculator
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
        buffer_size: int = 2000,  # Increased to 2000 for full-day VWAP calculation
        paper_service: Optional[PaperTradingService] = None
    ):
        """
        Initialize real-time service.
        
        Args:
            symbol: Trading pair symbol (default: 'btcusdt')
            interval: WebSocket interval (default: '1m')
            buffer_size: Size of candle buffers (default: 2000)
        """
        self.symbol = symbol
        self.interval = interval
        self.buffer_size = buffer_size
        self.paper_service = paper_service
        
        # Components
        self.websocket_client = BinanceWebSocketClient()
        self.rest_client = BinanceRestClient()
        self.aggregator = DataAggregator(buffer_size=buffer_size)
        self.volume_analyzer = VolumeAnalyzer(ma_period=20)
        self.rsi_monitor = RSIMonitor(period=6)
        
        # Initialize calculators (Dependency Injection Root)
        self.talib_calculator = TALibCalculator()
        self.vwap_calculator = VWAPCalculator()
        self.bollinger_calculator = BollingerCalculator()
        self.stoch_rsi_calculator = StochRSICalculator()
        self.entry_calculator = EntryPriceCalculator()
        self.tp_calculator = TPCalculator()
        self.stop_loss_calculator = StopLossCalculator()
        self.confidence_calculator = ConfidenceCalculator()
        self.smart_entry_calculator = SmartEntryCalculator()
        self.volume_spike_detector = VolumeSpikeDetector()
        self.adx_calculator = ADXCalculator()
        self.atr_calculator = ATRCalculator()
        
        self.signal_generator = SignalGenerator(
            # volume_analyzer and rsi_monitor are no longer used by SignalGenerator
            volume_spike_detector=self.volume_spike_detector,
            adx_calculator=self.adx_calculator,
            atr_calculator=self.atr_calculator,
            talib_calculator=self.talib_calculator,
            # entry_calculator is replaced by smart_entry_calculator
            tp_calculator=self.tp_calculator,
            stop_loss_calculator=self.stop_loss_calculator,
            confidence_calculator=self.confidence_calculator,
            vwap_calculator=self.vwap_calculator,
            bollinger_calculator=self.bollinger_calculator,
            stoch_rsi_calculator=self.stoch_rsi_calculator,
            smart_entry_calculator=self.smart_entry_calculator,
            account_size=10000.0  # Default account size for dashboard
        )
        
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
        
        # Logging
        self.logger = logging.getLogger(__name__)
    
    async def start(self) -> None:
        """
        Start the real-time service.
        
        This will:
        1. Load historical data
        2. Connect to WebSocket
        3. Start receiving real-time data
        4. Begin analysis and signal generation
        """
        if self._is_running:
            self.logger.warning("Service already running")
            return
        
        self.logger.info(f"Starting real-time service for {self.symbol}")
        
        try:
            # Load historical data first
            self.logger.info("Loading historical data...")
            await self._load_historical_data()
            
            # Register callbacks
            self.websocket_client.subscribe_candle(self._on_candle_received)
            self.aggregator.on_15m_complete(self._on_15m_complete)
            self.aggregator.on_1h_complete(self._on_1h_complete)
            
            # Connect to WebSocket
            await self.websocket_client.connect(
                symbol=self.symbol,
                interval=self.interval
            )
            
            self._is_running = True
            self.logger.info("✅ Real-time service started successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to start service: {e}")
            raise
    
    async def _load_historical_data(self) -> None:
        """
        Load historical candles from Binance REST API.
        
        This populates the buffer with recent candles so the dashboard
        shows data immediately instead of waiting for the first candle to close.
        """
        try:
            self.logger.info("Fetching historical candles...")
            
            # 1. Fetch last 100 1m candles
            candles_1m = self.rest_client.get_klines(
                symbol=self.symbol,
                interval=self.interval,
                limit=100
            )
            
            if candles_1m:
                self.logger.info(f"Loaded {len(candles_1m)} historical 1m candles")
                # Add to buffer and aggregator
                for candle in candles_1m:
                    self._candles_1m.append(candle)
                    # Feed to aggregator to initialize its state
                    self.aggregator.add_candle_1m(candle, is_closed=True)
                
                # Update latest 1m
                self._latest_1m = candles_1m[-1]
            else:
                self.logger.warning("No historical 1m data fetched")

            # 2. Fetch last 100 15m candles
            candles_15m = self.rest_client.get_klines(
                symbol=self.symbol,
                interval='15m',
                limit=100
            )
            
            if candles_15m and len(candles_15m) > 1:
                # Exclude the last candle as it is likely incomplete (still open)
                completed_15m = candles_15m[:-1]
                self.logger.info(f"Loaded {len(completed_15m)} historical 15m candles")
                
                for candle in completed_15m:
                    self._candles_15m.append(candle)
                
                # Update latest 15m (last completed)
                self._latest_15m = completed_15m[-1]
            
            # 3. Fetch last 100 1h candles
            candles_1h = self.rest_client.get_klines(
                symbol=self.symbol,
                interval='1h',
                limit=100
            )
            
            if candles_1h and len(candles_1h) > 1:
                # Exclude the last candle as it is likely incomplete
                completed_1h = candles_1h[:-1]
                self.logger.info(f"Loaded {len(completed_1h)} historical 1h candles")
                
                for candle in completed_1h:
                    self._candles_1h.append(candle)
                
                # Update latest 1h (last completed)
                self._latest_1h = completed_1h[-1]
            
            self.logger.info(f"✅ Historical data loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Error loading historical data: {e}")
            # Don't fail - continue with WebSocket streaming

    
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
    
    def _on_candle_received(self, candle: Candle, metadata: Dict) -> None:
        """
        Callback when new 1m candle is received from WebSocket.
        
        Args:
            candle: Candle entity
            metadata: Metadata (is_closed, symbol, etc.)
        """
        is_closed = metadata.get('is_closed', False)
        
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
        
        # Always update latest 1m candle (for real-time display)
        self._latest_1m = candle
        
        # Paper Engine Matching (Run on every tick/candle update)
        if self.paper_service:
            self.paper_service.process_market_data(
                current_price=candle.close,
                high=candle.high,
                low=candle.low
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
        self._notify_update_callbacks()
    
    def _on_15m_complete(self, candle: Candle) -> None:
        """
        Callback when 15m candle is completed.
        
        Args:
            candle: Completed 15m candle
        """
        self.logger.info(f"15m candle completed: {candle.timestamp}")
        
        self._latest_15m = candle
        self._candles_15m.append(candle)
        
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
        
        # Generate signals on 1h timeframe
        if len(self._candles_1h) >= 20:
            self._generate_signals_1h()
    
    def _generate_signals(self) -> None:
        """Generate trading signals based on current data."""
        if len(self._candles_1m) < 20:
            return
        
        try:
            signal = self.signal_generator.generate_signal(
                list(self._candles_1m)
            )
            
            if signal and signal.signal_type.value != 'neutral':
                self._latest_signal = signal
                self.logger.info(f"Signal generated: {signal}")
                
                # Send to Paper Engine
                if self.paper_service:
                    self.paper_service.on_signal_received(signal, self.symbol)
                
                # Notify signal callbacks
                self._notify_signal_callbacks(signal)
                
        except Exception as e:
            self.logger.error(f"Error generating signals: {e}")
    
    def _generate_signals_15m(self) -> None:
        """Generate signals on 15m timeframe."""
        try:
            signal = self.signal_generator.generate_signal(
                list(self._candles_15m)
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
                list(self._candles_1h)
            )
            
            if signal and signal.signal_type.value != 'neutral':
                self.logger.info(f"1h Signal: {signal}")
                self._notify_signal_callbacks(signal)
                
        except Exception as e:
            self.logger.error(f"Error generating 1h signals: {e}")

    
    def _notify_signal_callbacks(self, signal: TradingSignal) -> None:
        """Notify all signal callbacks."""
        for callback in self._signal_callbacks:
            try:
                callback(signal)
            except Exception as e:
                self.logger.error(f"Error in signal callback: {e}")
    
    def _notify_update_callbacks(self) -> None:
        """Notify all update callbacks."""
        for callback in self._update_callbacks:
            try:
                callback()
            except Exception as e:
                self.logger.error(f"Error in update callback: {e}")
    
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
                    
                return {k: (v if pd.notna(v) else 0.0) for k, v in latest.items()}
            return {}
        except Exception as e:
            self.logger.error(f"Error calculating indicators: {e}")
            return {}
    
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
        self.logger.debug(f"Added update callback (total: {len(self._update_callbacks)})")
    
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
