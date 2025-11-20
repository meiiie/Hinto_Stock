"""
PipelineService - Application Layer

Service orchestrating the data pipeline workflow.
"""

import logging
from typing import Optional

from ...domain.repositories.market_data_repository import MarketDataRepository
from ...domain.entities.market_data import MarketData
from ..use_cases.fetch_market_data import FetchMarketDataUseCase
from ..use_cases.calculate_indicators import CalculateIndicatorsUseCase


class PipelineService:
    """
    Application service orchestrating the data pipeline.
    
    This service coordinates the workflow:
    1. Fetch market data from API
    2. Calculate technical indicators
    3. Save to repository
    
    This is the main business workflow for the application.
    """
    
    def __init__(
        self,
        fetch_use_case: FetchMarketDataUseCase,
        calculate_use_case: CalculateIndicatorsUseCase,
        repository: MarketDataRepository,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize service with dependencies.
        
        Args:
            fetch_use_case: Use case for fetching market data
            calculate_use_case: Use case for calculating indicators
            repository: Repository for persisting data
            logger: Optional logger instance
        """
        self.fetch_use_case = fetch_use_case
        self.calculate_use_case = calculate_use_case
        self.repository = repository
        self.logger = logger or logging.getLogger(__name__)
    
    def update_market_data(
        self,
        symbol: str = 'BTCUSDT',
        timeframe: str = '15m',
        limit: int = 5
    ) -> dict:
        """
        Update market data: fetch, calculate indicators, save.
        
        This is the main workflow method.
        
        Args:
            symbol: Trading pair (default: 'BTCUSDT')
            timeframe: Timeframe (default: '15m')
            limit: Number of candles to fetch (default: 5)
        
        Returns:
            Dictionary with update results:
            - success: bool
            - records_saved: int
            - message: str
        
        Raises:
            Exception: If critical error occurs (logged but not raised)
        """
        try:
            # Step 1: Fetch candles
            self.logger.info(f"Fetching {limit} candles for {symbol} ({timeframe})")
            candles = self.fetch_use_case.execute(symbol, timeframe, limit)
            
            if not candles:
                self.logger.warning("No candles fetched from API")
                return {
                    'success': False,
                    'records_saved': 0,
                    'message': 'No data fetched from API'
                }
            
            self.logger.info(f"Fetched {len(candles)} candles")
            
            # Step 2: Calculate indicators
            self.logger.info("Calculating technical indicators")
            candles_with_indicators = self.calculate_use_case.execute(candles)
            
            # Step 3: Save to repository
            self.logger.info(f"Saving {len(candles_with_indicators)} records")
            saved_count = 0
            
            for candle, indicator in candles_with_indicators:
                try:
                    # Create MarketData aggregate
                    market_data = MarketData(
                        candle=candle,
                        indicator=indicator,
                        timeframe=timeframe
                    )
                    
                    # Save to repository
                    self.repository.save_market_data(market_data)
                    saved_count += 1
                    
                except Exception as e:
                    self.logger.error(f"Failed to save record: {e}")
                    continue
            
            self.logger.info(f"Successfully saved {saved_count} records")
            
            return {
                'success': True,
                'records_saved': saved_count,
                'message': f'Updated {saved_count} records for {symbol} {timeframe}'
            }
            
        except Exception as e:
            self.logger.error(f"Error updating market data: {e}", exc_info=True)
            return {
                'success': False,
                'records_saved': 0,
                'message': f'Error: {str(e)}'
            }
    
    def get_pipeline_status(self) -> dict:
        """
        Get current pipeline status.
        
        Returns:
            Dictionary with status information
        """
        try:
            # Get database info
            info_15m = self.repository.get_table_info('15m')
            info_1h = self.repository.get_table_info('1h')
            
            return {
                'status': 'OPERATIONAL',
                'database': {
                    '15m': info_15m,
                    '1h': info_1h
                },
                'database_size_mb': self.repository.get_database_size()
            }
        except Exception as e:
            self.logger.error(f"Error getting pipeline status: {e}")
            return {
                'status': 'ERROR',
                'message': str(e)
            }
