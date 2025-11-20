"""
Main pipeline orchestrator for Binance Data Pipeline.

Coordinates all components (API client, indicator calculator, database, validator)
and manages the data collection workflow with logging and scheduling.

NOTE: This is a backward-compatible wrapper around the new Clean Architecture.
The actual business logic is now in PipelineService (Application Layer).
"""

import os
import logging
from datetime import datetime
from typing import Optional
import pandas as pd
from apscheduler.schedulers.blocking import BlockingScheduler

from src.config import Config
from src.binance_client import BinanceClient
from src.indicators import IndicatorCalculator, IndicatorCalculatorFallback, TALIB_AVAILABLE
from src.database import DatabaseManager
from src.validator import DataValidator

# New Clean Architecture imports
from src.infrastructure.di_container import DIContainer
from src.application.services.pipeline_service import PipelineService


class DataPipeline:
    """
    Main orchestrator for the data pipeline.
    
    Coordinates data fetching, processing, storage, and validation.
    Includes logging and error handling to ensure pipeline resilience.
    
    Attributes:
        config (Config): Configuration instance
        client (BinanceClient): Binance API client
        calculator (IndicatorCalculator): Technical indicator calculator
        db_manager (DatabaseManager): Database manager
        validator (DataValidator): Data validator
        logger (logging.Logger): Logger instance
    """
    
    def __init__(self, config: Optional[Config] = None, use_clean_architecture: bool = False):
        """
        Initialize the data pipeline.
        
        Args:
            config (Config, optional): Configuration instance. 
                                      If None, creates new Config from .env
            use_clean_architecture (bool): If True, use new Clean Architecture.
                                          If False, use legacy implementation.
        """
        # Initialize configuration
        self.config = config if config else Config()
        self.config.validate()
        
        # Setup logging first
        self.logger = self._setup_logging()
        
        # Flag to determine which implementation to use
        self.use_clean_architecture = use_clean_architecture
        
        if self.use_clean_architecture:
            # New Clean Architecture approach
            self.logger.info("Using Clean Architecture implementation")
            
            # Initialize DI Container
            di_config = {
                'DATABASE_PATH': self.config.db_path,
                'BINANCE_API_KEY': None,
                'BINANCE_API_SECRET': None
            }
            self.container = DIContainer(di_config)
            
            # Get services from container
            self.pipeline_service = self.container.get_pipeline_service()
            
            # Keep legacy components for backward compatibility
            self.client = self.container.get_binance_client()
            self.calculator = self.container.get_indicator_calculator()
            self.db_manager = DatabaseManager(self.config.db_path)
            self.validator = DataValidator(self.db_manager)
        else:
            # Legacy implementation
            self.logger.info("Using legacy implementation")
            
            # Initialize components (old way)
            self.client = BinanceClient(self.config)
            
            # Use TA-Lib if available, otherwise fallback
            if TALIB_AVAILABLE:
                self.calculator = IndicatorCalculator()
            else:
                self.calculator = IndicatorCalculatorFallback()
                print("⚠️  Using fallback indicator calculator (TA-Lib not installed)")
            
            self.db_manager = DatabaseManager(self.config.db_path)
            self.validator = DataValidator(self.db_manager)
            
            self.pipeline_service = None
            self.container = None
        
        # Setup scheduler (not started yet)
        self.scheduler = BlockingScheduler()
        
        self.logger.info("=" * 60)
        self.logger.info("Data Pipeline Initialized")
        self.logger.info(f"Architecture: {'Clean Architecture' if self.use_clean_architecture else 'Legacy'}")
        self.logger.info(f"Database: {self.config.db_path}")
        self.logger.info(f"API Base URL: {self.config.base_url}")
        self.logger.info(f"Indicator Calculator: {'TA-Lib' if TALIB_AVAILABLE else 'Fallback'}")
        self.logger.info("=" * 60)
    
    def _setup_logging(self) -> logging.Logger:
        """
        Setup logging with both file and console handlers.
        
        Returns:
            logging.Logger: Configured logger instance
        """
        # Create logs directory
        log_dir = "documents/logs"
        os.makedirs(log_dir, exist_ok=True)
        
        # Create log file with date
        log_file = os.path.join(
            log_dir,
            f"pipeline_{datetime.now().strftime('%Y%m%d')}.log"
        )
        
        # Create logger
        logger = logging.getLogger('DataPipeline')
        logger.setLevel(logging.INFO)
        
        # Remove existing handlers to avoid duplicates
        logger.handlers.clear()
        
        # File handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        
        # Add handlers
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def update_data(self, symbol: str = "BTCUSDT") -> bool:
        """
        Main update logic to fetch and process data.
        
        Fetches latest data from Binance, calculates indicators,
        and saves to database. Handles both 15m and 1h timeframes.
        
        Args:
            symbol (str): Trading pair symbol (default: "BTCUSDT")
        
        Returns:
            bool: True if update successful, False otherwise
        """
        try:
            self.logger.info(f"Starting data update for {symbol}")
            
            # Fetch 15-minute data
            success_15m = self._update_timeframe(symbol, "15m", "btc_15m", limit=5)
            
            # Fetch 1-hour data if current minute is 0
            current_minute = datetime.now().minute
            if current_minute == 0:
                self.logger.info("Hourly update triggered (minute == 0)")
                success_1h = self._update_timeframe(symbol, "1h", "btc_1h", limit=2)
            else:
                success_1h = True  # Skip 1h update, not an error
            
            # Overall success if at least 15m succeeded
            success = success_15m
            
            if success:
                self.logger.info("✅ Data update completed successfully")
            else:
                self.logger.warning("⚠️  Data update completed with errors")
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Error in update_data: {e}", exc_info=True)
            return False
    
    def _update_timeframe(
        self,
        symbol: str,
        interval: str,
        table_name: str,
        limit: int = 5
    ) -> bool:
        """
        Update data for a specific timeframe.
        
        Args:
            symbol (str): Trading pair symbol
            interval (str): Timeframe interval (15m, 1h)
            table_name (str): Database table name
            limit (int): Number of klines to fetch
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if self.use_clean_architecture and self.pipeline_service:
                # Use new Clean Architecture
                self.logger.info(f"Using PipelineService for {symbol} ({interval})")
                
                result = self.pipeline_service.update_market_data(
                    symbol=symbol,
                    timeframe=interval,
                    limit=limit
                )
                
                if result['success']:
                    self.logger.info(f"✅ {result['message']}")
                    return True
                else:
                    self.logger.error(f"❌ {result['message']}")
                    return False
            else:
                # Use legacy implementation
                self.logger.info(f"Fetching {limit} klines for {symbol} ({interval})")
                
                # Step 1: Fetch data from Binance
                df = self.client.get_klines(symbol, interval, limit)
                
                if df is None or df.empty:
                    self.logger.error(f"Failed to fetch data for {interval}")
                    return False
                
                self.logger.info(f"Fetched {len(df)} records")
                
                # Step 2: Calculate indicators
                self.logger.info("Calculating technical indicators")
                df = self.calculator.calculate_all(df)
                
                # Step 3: Save to database
                self.logger.info(f"Saving data to {table_name}")
                rows_saved = self.db_manager.save_data(df, table_name)
                self.logger.info(f"Saved {rows_saved} rows to {table_name}")
                
                return True
            
        except Exception as e:
            self.logger.error(
                f"❌ Error updating {interval} data: {e}",
                exc_info=True
            )
            return False
    
    def validate_data(self, table_name: str = 'btc_15m', limit: int = 100) -> dict:
        """
        Run data validation checks.
        
        Args:
            table_name (str): Table to validate
            limit (int): Number of recent records to check
        
        Returns:
            dict: Validation results
        """
        try:
            self.logger.info(f"Running validation on {table_name}")
            
            results = self.validator.validate_all(table_name, limit)
            
            if results['valid']:
                self.logger.info(f"✅ Validation passed for {table_name}")
            else:
                self.logger.warning(f"⚠️  Validation issues found in {table_name}")
                for issue in results['issues']:
                    self.logger.warning(f"  - {issue}")
            
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Error during validation: {e}", exc_info=True)
            return {
                'valid': False,
                'issues': [f"Validation error: {str(e)}"],
                'warnings': [],
                'checks': {}
            }
    
    def get_status(self) -> dict:
        """
        Get current pipeline status and statistics.
        
        Returns:
            dict: Status information including record counts and table info
        """
        try:
            status = {
                'timestamp': datetime.now().isoformat(),
                'database': self.config.db_path,
                'tables': {}
            }
            
            # Get info for both tables
            for table_name in ['btc_15m', 'btc_1h']:
                try:
                    info = self.db_manager.get_table_info(table_name)
                    status['tables'][table_name] = info
                except Exception as e:
                    status['tables'][table_name] = {'error': str(e)}
            
            return status
            
        except Exception as e:
            self.logger.error(f"Error getting status: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
    
    def run_once(self, symbol: str = "BTCUSDT", validate: bool = True) -> bool:
        """
        Run pipeline once (fetch, process, save, optionally validate).
        
        Useful for testing or manual execution.
        
        Args:
            symbol (str): Trading pair symbol
            validate (bool): Whether to run validation after update
        
        Returns:
            bool: True if successful, False otherwise
        """
        self.logger.info("=" * 60)
        self.logger.info("Running pipeline (single execution)")
        self.logger.info("=" * 60)
        
        # Update data
        success = self.update_data(symbol)
        
        # Optionally validate
        if success and validate:
            self.logger.info("")
            self.logger.info("Running validation...")
            validation_results = self.validate_data('btc_15m')
            
            # Log validation report
            report = self.validator.generate_report(validation_results)
            self.logger.info("\n" + report)
        
        # Show status
        self.logger.info("")
        self.logger.info("Pipeline Status:")
        status = self.get_status()
        for table_name, table_info in status.get('tables', {}).items():
            if 'error' not in table_info:
                self.logger.info(
                    f"  {table_name}: {table_info['record_count']} records, "
                    f"{table_info['size_mb']} MB"
                )
        
        self.logger.info("=" * 60)
        
        return success
    
    def start_scheduler(self, interval_minutes: int = 15) -> None:
        """
        Start the scheduler to run pipeline automatically.
        
        Runs update_data() immediately, then schedules it to run
        every N minutes. This is a blocking call.
        
        Args:
            interval_minutes (int): Update interval in minutes (default: 15)
        """
        self.logger.info("=" * 60)
        self.logger.info(f"Starting scheduler (interval: {interval_minutes} minutes)")
        self.logger.info("Press Ctrl+C to stop")
        self.logger.info("=" * 60)
        
        # Add scheduled job
        self.scheduler.add_job(
            self.update_data,
            'interval',
            minutes=interval_minutes,
            id='update_data_job',
            name='Update cryptocurrency data'
        )
        
        # Run immediately on startup
        self.logger.info("Running initial update...")
        self.update_data()
        
        # Start scheduler (blocking)
        try:
            self.scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            self.logger.info("Scheduler stopped by user")
            self.shutdown()
    
    def shutdown(self) -> None:
        """
        Gracefully shutdown the pipeline.
        
        Stops the scheduler and closes resources.
        """
        self.logger.info("Shutting down pipeline...")
        
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)
        
        # Cleanup DI container if using Clean Architecture
        if self.use_clean_architecture and self.container:
            self.container.cleanup()
            self.logger.info("DI Container cleaned up")
        
        self.logger.info("Pipeline shutdown complete")
    
    def __repr__(self) -> str:
        """
        String representation of DataPipeline.
        
        Returns:
            str: String representation
        """
        return (
            f"DataPipeline("
            f"db='{self.config.db_path}', "
            f"calculator={'TA-Lib' if TALIB_AVAILABLE else 'Fallback'}"
            f")"
        )
