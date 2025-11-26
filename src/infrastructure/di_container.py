"""
Dependency Injection Container - Infrastructure Layer

Container for managing dependencies and providing instances.
"""

from typing import Optional, Dict, Any
import logging

from .persistence.sqlite_market_data_repository import SQLiteMarketDataRepository
from .api.binance_client import BinanceClient
from .indicators.talib_calculator import TALibCalculator
from ..application.use_cases.fetch_market_data import FetchMarketDataUseCase
from ..application.use_cases.calculate_indicators import CalculateIndicatorsUseCase
from ..application.use_cases.validate_data import ValidateDataUseCase
from ..application.use_cases.export_data import ExportDataUseCase
from ..application.services.pipeline_service import PipelineService
from ..application.services.dashboard_service import DashboardService


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
            db_path = self.get_config('DATABASE_PATH', 'crypto_data.db')
            
            self._instances['market_data_repository'] = SQLiteMarketDataRepository(
                db_path=db_path
            )
            self.logger.debug(f"Created SQLiteMarketDataRepository with db: {db_path}")
        
        return self._instances['market_data_repository']
    
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
