"""
Dependency Injection Container - Infrastructure Layer

Container for managing dependencies and providing instances.

Production Readiness Update:
- Added BookTickerClient for real spread data
- Added TradingStateMachine for state management
- Added WarmupManager for cold start
- Added HardFilters with BookTickerClient injection
- Added StateRecoveryService for startup recovery
- Added RealtimeService with all dependencies
"""

from typing import Optional, Dict, Any
import logging

from .persistence.sqlite_market_data_repository import SQLiteMarketDataRepository
from .persistence.sqlite_state_repository import SQLiteStateRepository
from .persistence.sqlite_order_repository import SQLiteOrderRepository
from .api.binance_client import BinanceClient
from .api.binance_rest_client import BinanceRestClient
from .exchange.paper_exchange_service import PaperExchangeService
from .exchange.binance_exchange_service import BinanceExchangeService
from ..domain.interfaces.i_exchange_service import IExchangeService
from .indicators.talib_calculator import TALibCalculator
from .indicators.vwap_calculator import VWAPCalculator
from .indicators.bollinger_calculator import BollingerCalculator
from .indicators.stoch_rsi_calculator import StochRSICalculator
from .indicators.adx_calculator import ADXCalculator
from .indicators.atr_calculator import ATRCalculator
from .indicators.volume_spike_detector import VolumeSpikeDetector
from .indicators.regime_detector import RegimeDetector  # SOTA: For Layer 0 filtering
from .websocket.binance_websocket_client import BinanceWebSocketClient
from .websocket.binance_book_ticker_client import BinanceBookTickerClient
from .aggregation.data_aggregator import DataAggregator
from ..application.use_cases.fetch_market_data import FetchMarketDataUseCase
from ..application.use_cases.calculate_indicators import CalculateIndicatorsUseCase
from ..application.use_cases.validate_data import ValidateDataUseCase
from ..application.use_cases.export_data import ExportDataUseCase
from ..application.services.pipeline_service import PipelineService
from ..application.services.dashboard_service import DashboardService
from ..application.services.trading_state_machine import TradingStateMachine
from ..application.services.warmup_manager import WarmupManager
from ..application.services.hard_filters import HardFilters
from ..application.services.state_recovery_service import StateRecoveryService
from ..application.services.smart_entry_calculator import SmartEntryCalculator
from ..application.signals.signal_generator import SignalGenerator
from ..application.analysis.trend_filter import TrendFilter # SOTA: For HTF Confluence


class DIContainer:
    """
    Dependency Injection Container.
    
    This container manages the creation and lifecycle of all dependencies
    in the application. It implements the Singleton pattern for shared
    instances and provides factory methods for creating services.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the DI container.
        
        Args:
            config: Configuration dictionary with settings
        """
        self.config = config or {}
        self._instances: Dict[str, Any] = {}
        self.logger = logging.getLogger(__name__)
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key not found
        
        Returns:
            Configuration value
        """
        return self.config.get(key, default)
    
    def get_binance_client(self) -> BinanceClient:
        """
        Get BinanceClient instance (singleton).
        
        Returns:
            BinanceClient instance
        """
        if 'binance_client' not in self._instances:
            api_key = self.get_config('BINANCE_API_KEY')
            api_secret = self.get_config('BINANCE_API_SECRET')
            
            self._instances['binance_client'] = BinanceClient(
                api_key=api_key,
                api_secret=api_secret
            )
            self.logger.debug("Created BinanceClient instance")
        
        return self._instances['binance_client']
    
    def get_indicator_calculator(self) -> TALibCalculator:
        """
        Get TALibCalculator instance (singleton).
        
        Returns:
            TALibCalculator instance
        """
        if 'indicator_calculator' not in self._instances:
            self._instances['indicator_calculator'] = TALibCalculator()
            self.logger.debug("Created TALibCalculator instance")
        
        return self._instances['indicator_calculator']
    
    def get_market_data_repository(self) -> SQLiteMarketDataRepository:
        """
        Get SQLiteMarketDataRepository instance (singleton).
        
        Returns:
            SQLiteMarketDataRepository instance
        """
        if 'market_data_repository' not in self._instances:
            # SOTA: Store databases in data/ folder for clean project structure
            db_path = self.get_config('DATABASE_PATH', 'data/market_data.db')
            
            self._instances['market_data_repository'] = SQLiteMarketDataRepository(
                db_path=db_path
            )
            self.logger.debug(f"Created SQLiteMarketDataRepository with db: {db_path}")
        
        return self._instances['market_data_repository']
    
    def get_data_retention_service(self):
        """
        Get DataRetentionService instance (singleton).
        
        SOTA: Automatic database cleanup with rolling window policy.
        
        Returns:
            DataRetentionService instance
        """
        if 'data_retention_service' not in self._instances:
            # Lazy import to avoid circular dependency
            from ..application.services.data_retention_service import DataRetentionService
            
            self._instances['data_retention_service'] = DataRetentionService(
                repository=self.get_market_data_repository()
            )
            self.logger.debug("Created DataRetentionService")
        
        return self._instances['data_retention_service']
    
    def get_fetch_market_data_use_case(self) -> FetchMarketDataUseCase:
        """
        Get FetchMarketDataUseCase instance.
        
        Returns:
            FetchMarketDataUseCase instance
        """
        binance_client = self.get_binance_client()
        return FetchMarketDataUseCase(binance_client)
    
    def get_calculate_indicators_use_case(self) -> CalculateIndicatorsUseCase:
        """
        Get CalculateIndicatorsUseCase instance.
        
        Returns:
            CalculateIndicatorsUseCase instance
        """
        calculator = self.get_indicator_calculator()
        return CalculateIndicatorsUseCase(calculator)
    
    def get_validate_data_use_case(self) -> ValidateDataUseCase:
        """
        Get ValidateDataUseCase instance.
        
        Returns:
            ValidateDataUseCase instance
        """
        repository = self.get_market_data_repository()
        return ValidateDataUseCase(repository)
    
    def get_export_data_use_case(self) -> ExportDataUseCase:
        """
        Get ExportDataUseCase instance.
        
        Returns:
            ExportDataUseCase instance
        """
        repository = self.get_market_data_repository()
        return ExportDataUseCase(repository)
    
    def get_pipeline_service(self) -> PipelineService:
        """
        Get PipelineService instance.
        
        Returns:
            PipelineService instance with all dependencies injected
        """
        fetch_use_case = self.get_fetch_market_data_use_case()
        calculate_use_case = self.get_calculate_indicators_use_case()
        repository = self.get_market_data_repository()
        
        return PipelineService(
            fetch_use_case=fetch_use_case,
            calculate_use_case=calculate_use_case,
            repository=repository
        )
    
    def get_dashboard_service(self) -> DashboardService:
        """
        Get DashboardService instance.
        
        Returns:
            DashboardService instance with all dependencies injected
        """
        market_data_repo = self.get_market_data_repository()
        export_use_case = self.get_export_data_use_case()
        validate_use_case = self.get_validate_data_use_case()
        
        return DashboardService(
            market_data_repo=market_data_repo,
            export_use_case=export_use_case,
            validate_use_case=validate_use_case
        )
    
    # ==================== Production Readiness Methods ====================
    
    def get_book_ticker_client(self) -> BinanceBookTickerClient:
        """
        Get BinanceBookTickerClient instance (singleton).
        
        Returns:
            BinanceBookTickerClient for real bid/ask data
        """
        if 'book_ticker_client' not in self._instances:
            self._instances['book_ticker_client'] = BinanceBookTickerClient()
            self.logger.debug("Created BinanceBookTickerClient instance")
        
        return self._instances['book_ticker_client']
    
    def get_trading_state_machine(self, symbol: str = "btcusdt") -> TradingStateMachine:
        """
        Get TradingStateMachine instance (singleton per symbol).
        
        Args:
            symbol: Trading symbol
            
        Returns:
            TradingStateMachine instance
        """
        key = f'trading_state_machine_{symbol}'
        if key not in self._instances:
            self._instances[key] = TradingStateMachine(symbol=symbol)
            self.logger.debug(f"Created TradingStateMachine for {symbol}")
        
        return self._instances[key]
    
    def get_warmup_manager(self) -> WarmupManager:
        """
        Get WarmupManager instance (singleton).
        
        Returns:
            WarmupManager instance
        """
        if 'warmup_manager' not in self._instances:
            rest_client = self.get_rest_client()
            vwap_calculator = self.get_vwap_calculator()
            stoch_rsi_calculator = self.get_stoch_rsi_calculator()
            adx_calculator = self.get_adx_calculator()
            
            self._instances['warmup_manager'] = WarmupManager(
                rest_client=rest_client,
                vwap_calculator=vwap_calculator,
                stoch_rsi_calculator=stoch_rsi_calculator,
                adx_calculator=adx_calculator
            )
            self.logger.debug("Created WarmupManager instance")
        
        return self._instances['warmup_manager']
    
    def get_hard_filters(self) -> HardFilters:
        """
        Get HardFilters instance with BookTickerClient and Config injection (singleton).
        
        Expert Feedback 3: Now injects Config for configurable thresholds
        
        Returns:
            HardFilters instance with real spread data capability
        """
        if 'hard_filters' not in self._instances:
            book_ticker_client = self.get_book_ticker_client()
            config = self.get_config_instance()
            
            self._instances['hard_filters'] = HardFilters(
                book_ticker_client=book_ticker_client,
                config=config
            )
            self.logger.debug("Created HardFilters with BookTickerClient and Config")
        
        return self._instances['hard_filters']
    
    def get_config_instance(self):
        """
        Get Config instance (singleton).
        
        Expert Feedback 3: Centralized config management
        
        Returns:
            Config instance with all settings
        """
        if 'config_instance' not in self._instances:
            from ..config import Config
            self._instances['config_instance'] = Config()
            self.logger.debug("Created Config instance")
        
        return self._instances['config_instance']
    
    def get_order_repository(self) -> SQLiteOrderRepository:
        """
        Get SQLiteOrderRepository instance (singleton).
        
        Returns:
            SQLiteOrderRepository for order/position persistence
        """
        if 'order_repository' not in self._instances:
            db_path = self.get_config('DATABASE_PATH', 'data/trading_system.db')
            self._instances['order_repository'] = SQLiteOrderRepository(db_path=db_path)
            self.logger.debug(f"Created SQLiteOrderRepository with db: {db_path}")
        
        return self._instances['order_repository']
    
    def get_exchange_service(self) -> IExchangeService:
        """
        Get IExchangeService instance based on TRADING_MODE config (singleton).
        
        Factory method that returns:
        - PaperExchangeService when TRADING_MODE="PAPER" (default)
        - BinanceExchangeService when TRADING_MODE="REAL"
        
        Returns:
            IExchangeService implementation
        """
        if 'exchange_service' not in self._instances:
            trading_mode = self.get_config('TRADING_MODE', 'PAPER').upper()
            
            if trading_mode == 'PAPER':
                order_repository = self.get_order_repository()
                self._instances['exchange_service'] = PaperExchangeService(
                    order_repository=order_repository
                )
                self.logger.info("Created PaperExchangeService (PAPER mode)")
            elif trading_mode == 'REAL':
                rest_client = self.get_rest_client()
                api_key = self.get_config('BINANCE_API_KEY')
                api_secret = self.get_config('BINANCE_API_SECRET')
                
                self._instances['exchange_service'] = BinanceExchangeService(
                    rest_client=rest_client,
                    api_key=api_key,
                    api_secret=api_secret
                )
                self.logger.info("Created BinanceExchangeService (REAL mode)")
            else:
                # Default to paper trading for safety
                self.logger.warning(
                    f"Unknown TRADING_MODE '{trading_mode}', defaulting to PAPER"
                )
                order_repository = self.get_order_repository()
                self._instances['exchange_service'] = PaperExchangeService(
                    order_repository=order_repository
                )
        
        return self._instances['exchange_service']
    
    def get_state_repository(self) -> SQLiteStateRepository:
        """
        Get SQLiteStateRepository instance (singleton).
        
        Returns:
            SQLiteStateRepository for state persistence
        """
        if 'state_repository' not in self._instances:
            db_path = self.get_config('DATABASE_PATH', 'data/trading_system.db')
            self._instances['state_repository'] = SQLiteStateRepository(db_path=db_path)
            self.logger.debug(f"Created SQLiteStateRepository with db: {db_path}")
        
        return self._instances['state_repository']
    
    def get_state_recovery_service(self) -> StateRecoveryService:
        """
        Get StateRecoveryService instance (singleton).
        
        Expert Feedback 3: Now uses IExchangeService instead of IRestClient
        
        Returns:
            StateRecoveryService for startup recovery
        """
        if 'state_recovery_service' not in self._instances:
            state_repository = self.get_state_repository()
            exchange_service = self.get_exchange_service()
            
            self._instances['state_recovery_service'] = StateRecoveryService(
                state_repository=state_repository,
                exchange_service=exchange_service
            )
            self.logger.debug(
                f"Created StateRecoveryService with {exchange_service.get_exchange_type()} exchange"
            )
        
        return self._instances['state_recovery_service']
    
    def get_rest_client(self) -> BinanceRestClient:
        """
        Get BinanceRestClient instance (singleton).
        
        Returns:
            BinanceRestClient instance
        """
        if 'rest_client' not in self._instances:
            self._instances['rest_client'] = BinanceRestClient()
            self.logger.debug("Created BinanceRestClient instance")
        
        return self._instances['rest_client']
    
    def get_websocket_client(self) -> BinanceWebSocketClient:
        """
        Get BinanceWebSocketClient instance (singleton).
        
        Returns:
            BinanceWebSocketClient instance
        """
        if 'websocket_client' not in self._instances:
            self._instances['websocket_client'] = BinanceWebSocketClient()
            self.logger.debug("Created BinanceWebSocketClient instance")
        
        return self._instances['websocket_client']
    
    def get_data_aggregator(self) -> DataAggregator:
        """
        Get DataAggregator instance (Transient).
        
        CRITICAL FIX (Phase 6): Must be transient (new instance per call) because 
        it stores stateful buffers (_candles_1m, _buffer_15m). Sharing it across 
        RealtimeServices causes data mixing between symbols (e.g., BTC data 
        polluting ETH 15m candles).
        
        Returns:
            New DataAggregator instance
        """
        # SOTA: Return new instance every time (Transient Scope)
        instance = DataAggregator()
        self.logger.debug(f"Created new isolated DataAggregator instance: {id(instance)}")
        return instance
    
    def get_vwap_calculator(self) -> VWAPCalculator:
        """Get VWAPCalculator instance (singleton)."""
        if 'vwap_calculator' not in self._instances:
            self._instances['vwap_calculator'] = VWAPCalculator()
        return self._instances['vwap_calculator']
    
    def get_bollinger_calculator(self) -> BollingerCalculator:
        """Get BollingerCalculator instance (singleton)."""
        if 'bollinger_calculator' not in self._instances:
            self._instances['bollinger_calculator'] = BollingerCalculator()
        return self._instances['bollinger_calculator']
    
    def get_stoch_rsi_calculator(self) -> StochRSICalculator:
        """Get StochRSICalculator instance (singleton)."""
        if 'stoch_rsi_calculator' not in self._instances:
            self._instances['stoch_rsi_calculator'] = StochRSICalculator()
        return self._instances['stoch_rsi_calculator']
    
    def get_adx_calculator(self) -> ADXCalculator:
        """Get ADXCalculator instance (singleton)."""
        if 'adx_calculator' not in self._instances:
            self._instances['adx_calculator'] = ADXCalculator()
        return self._instances['adx_calculator']
    
    def get_atr_calculator(self) -> ATRCalculator:
        """Get ATRCalculator instance (singleton)."""
        if 'atr_calculator' not in self._instances:
            self._instances['atr_calculator'] = ATRCalculator()
        return self._instances['atr_calculator']
    
    def get_volume_spike_detector(self) -> VolumeSpikeDetector:
        """Get VolumeSpikeDetector instance (singleton)."""
        if 'volume_spike_detector' not in self._instances:
            self._instances['volume_spike_detector'] = VolumeSpikeDetector()
        return self._instances['volume_spike_detector']
    
    def get_regime_detector(self) -> RegimeDetector:
        """
        Get RegimeDetector instance (singleton).
        
        SOTA: Injects ADX threshold from StrategyConfig.
        
        Returns:
            RegimeDetector for Layer 0 market regime classification
        """
        if 'regime_detector' not in self._instances:
            config = self.get_config_instance()
            strategy_config = config.strategy
            
            self._instances['regime_detector'] = RegimeDetector(
                adx_trending_threshold=strategy_config.adx_trending_threshold
            )
            self.logger.debug(
                f"Created RegimeDetector with ADX threshold: {strategy_config.adx_trending_threshold}"
            )
        return self._instances['regime_detector']
    
    def get_signal_generator(self) -> SignalGenerator:
        """
        Get SignalGenerator instance with all dependencies (singleton).
        
        SOTA: Now injects StrategyConfig for centralized parameter management.
        
        Returns:
            SignalGenerator with injected calculators and config
        """
        if 'signal_generator' not in self._instances:
            # SOTA: Get strategy config from centralized Config
            config = self.get_config_instance()
            strategy_config = config.strategy
            
            self._instances['signal_generator'] = SignalGenerator(
                vwap_calculator=self.get_vwap_calculator(),
                bollinger_calculator=self.get_bollinger_calculator(),
                stoch_rsi_calculator=self.get_stoch_rsi_calculator(),
                smart_entry_calculator=SmartEntryCalculator(),
                volume_spike_detector=self.get_volume_spike_detector(),
                adx_calculator=self.get_adx_calculator(),
                atr_calculator=self.get_atr_calculator(),
                talib_calculator=self.get_indicator_calculator(),
                # SOTA: Inject RegimeDetector for Layer 0 filtering
                regime_detector=self.get_regime_detector(),
                # SOTA: Inject config-based parameters instead of hardcoded
                use_filters=True,
                strict_mode=strategy_config.strict_mode,
                use_regime_filter=strategy_config.use_regime_filter,
                strategy_config=strategy_config,  # Full config object
            )
            self.logger.info(
                f"Created SignalGenerator with SOTA config: "
                f"strict_mode={strategy_config.strict_mode}, "
                f"regime_mode={strategy_config.regime_filter_mode}"
            )
        
        return self._instances['signal_generator']
    
    def get_paper_trading_service(self):
        """
        Get PaperTradingService instance (singleton).
        
        SOTA FIX: This was MISSING - signals were generated but never
        reached trade execution because paper_service was not injected.
        
        Returns:
            PaperTradingService for paper trading execution
        """
        if 'paper_trading_service' not in self._instances:
            # Lazy import to avoid circular dependency
            from ..application.services.paper_trading_service import PaperTradingService
            
            order_repository = self.get_order_repository()
            # SOTA FIX: Inject MarketDataRepository for multi-symbol pricing
            market_data_repository = self.get_market_data_repository()
            
            self._instances['paper_trading_service'] = PaperTradingService(
                repository=order_repository,
                market_data_repository=market_data_repository
            )
            self.logger.info("Created PaperTradingService with order repository")
        
        return self._instances['paper_trading_service']
    
    def get_signal_lifecycle_service(self):
        """
        Get SignalLifecycleService instance (singleton).
        
        SOTA FIX: This was MISSING - signals were not persisted to DB.
        
        Returns:
            SignalLifecycleService for signal persistence
        """
        if 'signal_lifecycle_service' not in self._instances:
            # Lazy import to avoid circular dependency
            from ..application.services.signal_lifecycle_service import SignalLifecycleService
            from ..infrastructure.repositories.sqlite_signal_repository import SQLiteSignalRepository
            
            signal_repository = SQLiteSignalRepository()
            self._instances['signal_lifecycle_service'] = SignalLifecycleService(
                signal_repository=signal_repository
            )
            self.logger.info("Created SignalLifecycleService with signal repository")
        
        return self._instances['signal_lifecycle_service']
    
    def get_trend_filter(self) -> TrendFilter:
        """Get TrendFilter instance (singleton)."""
        if 'trend_filter' not in self._instances:
            self._instances['trend_filter'] = TrendFilter(ema_period=50) # Standard 1H/4H period
        return self._instances['trend_filter']

    def get_realtime_service(self, symbol: str = "btcusdt"):
        """
        Get RealtimeService instance with all dependencies (singleton per symbol).
        
        NOTE: Import RealtimeService here to avoid circular import.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            RealtimeService with all dependencies injected
        """
        # Lazy import to avoid circular dependency
        from ..application.services.realtime_service import RealtimeService
        
        key = f'realtime_service_{symbol}'
        if key not in self._instances:
            self._instances[key] = RealtimeService(
                symbol=symbol,
                websocket_client=self.get_websocket_client(),
                rest_client=self.get_rest_client(),
                aggregator=self.get_data_aggregator(),
                talib_calculator=self.get_indicator_calculator(),
                vwap_calculator=self.get_vwap_calculator(),
                bollinger_calculator=self.get_bollinger_calculator(),
                stoch_rsi_calculator=self.get_stoch_rsi_calculator(),
                adx_calculator=self.get_adx_calculator(),
                atr_calculator=self.get_atr_calculator(),
                volume_spike_detector=self.get_volume_spike_detector(),
                signal_generator=self.get_signal_generator(),
                # SOTA FIX: Inject market data repository for candle persistence
                market_data_repository=self.get_market_data_repository(),
                # CRITICAL FIX: Inject paper_service for trade execution!
                paper_service=self.get_paper_trading_service(),
                # SOTA FIX: Inject lifecycle_service for signal persistence!
                lifecycle_service=self.get_signal_lifecycle_service(),
                # SOTA FIX: Inject trend_filter for HTF Confluence (Phase 12)
                trend_filter=self.get_trend_filter(),
            )
            self.logger.info(f"✅ Created RealtimeService for {symbol} with all services injected!")
        
        return self._instances[key]
    
    def cleanup(self):
        """
        Cleanup resources.
        
        Should be called when shutting down the application.
        """
        # Close BinanceClient session if exists
        if 'binance_client' in self._instances:
            try:
                self._instances['binance_client'].close()
                self.logger.debug("Closed BinanceClient")
            except Exception as e:
                self.logger.warning(f"Error closing BinanceClient: {e}")
        
        # Clear all instances
        self._instances.clear()
        self.logger.info("DI Container cleaned up")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.cleanup()
