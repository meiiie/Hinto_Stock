"""
DashboardService - Application Layer

Service providing data for the Streamlit dashboard.
"""

from datetime import datetime
from typing import Optional, Dict, List
import pandas as pd

from ...domain.repositories.market_data_repository import MarketDataRepository
from ...domain.repositories.indicator_repository import IndicatorRepository
from ..use_cases.export_data import ExportDataUseCase
from ..use_cases.validate_data import ValidateDataUseCase


class DashboardService:
    """
    Application service for dashboard data operations.
    
    This service provides methods specifically designed for
    dashboard consumption, returning DTOs and formatted data.
    """
    
    def __init__(
        self,
        market_data_repo: MarketDataRepository,
        indicator_repo: Optional[IndicatorRepository] = None,
        export_use_case: Optional[ExportDataUseCase] = None,
        validate_use_case: Optional[ValidateDataUseCase] = None
    ):
        """Initialize service with dependencies"""
        self.market_data_repo = market_data_repo
        self.indicator_repo = indicator_repo
        self.export_use_case = export_use_case
        self.validate_use_case = validate_use_case
    
    def get_chart_data(
        self,
        timeframe: str,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        limit: int = 500
    ) -> pd.DataFrame:
        """
        Get data for charts.
        
        Returns:
            DataFrame with OHLCV and indicators
        """
        # Get market data
        if start and end:
            market_data_list = self.market_data_repo.get_candles_by_date_range(
                timeframe, start, end
            )
        else:
            market_data_list = self.market_data_repo.get_latest_candles(
                timeframe, limit
            )
        
        if not market_data_list:
            return pd.DataFrame()
        
        # Convert to DataFrame
        data = [md.to_dict() for md in market_data_list]
        df = pd.DataFrame(data)
        
        # Convert timestamp to datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        return df
    
    def get_system_status(self) -> Dict:
        """Get system status for monitoring page"""
        try:
            info_15m = self.market_data_repo.get_table_info('15m')
            info_1h = self.market_data_repo.get_table_info('1h')
            
            return {
                'status': 'OPERATIONAL',
                'database': {
                    '15m': info_15m,
                    '1h': info_1h
                },
                'database_size_mb': self.market_data_repo.get_database_size()
            }
        except Exception as e:
            return {
                'status': 'ERROR',
                'message': str(e)
            }
    
    def get_recent_data(self, timeframe: str = '15m', limit: int = 10) -> pd.DataFrame:
        """Get recent data for display"""
        return self.get_chart_data(timeframe, limit=limit)
    
    def get_total_records(self, timeframe: str = '15m') -> int:
        """Get total record count"""
        try:
            return self.market_data_repo.get_record_count(timeframe)
        except:
            return 0
    
    def get_latest_price(self, timeframe: str = '15m') -> Optional[float]:
        """Get latest close price"""
        try:
            market_data_list = self.market_data_repo.get_latest_candles(timeframe, 1)
            if market_data_list:
                return market_data_list[0].close_price
        except:
            pass
        return None
    
    def export_to_csv(
        self,
        timeframe: str,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None
    ) -> str:
        """Export data to CSV"""
        if self.export_use_case:
            return self.export_use_case.execute(timeframe, start, end)
        
        # Fallback
        df = self.get_chart_data(timeframe, start, end)
        return df.to_csv(index=False)
    
    def validate_data_quality(self, timeframe: str) -> Dict:
        """Validate data quality"""
        if self.validate_use_case:
            return self.validate_use_case.execute(timeframe)
        
        # Fallback
        return {
            'status': 'UNKNOWN',
            'message': 'Validation not available'
        }
    
    def trigger_update(self) -> Dict:
        """Trigger manual data update"""
        # This would call PipelineService
        # For now, return placeholder
        return {
            'success': True,
            'message': 'Update triggered (not implemented yet)'
        }
    
    def backup_database(self, backup_path: Optional[str] = None) -> Dict:
        """Backup database"""
        try:
            if not backup_path:
                from datetime import datetime
                backup_path = f"backups/crypto_data_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            
            self.market_data_repo.backup_database(backup_path)
            
            return {
                'success': True,
                'message': f'Backup created: {backup_path}'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Backup failed: {str(e)}'
            }
