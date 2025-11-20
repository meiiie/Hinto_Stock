"""
SQLiteMarketDataRepository - Infrastructure Layer

SQLite implementation of MarketDataRepository interface.
"""

import sqlite3
import shutil
from datetime import datetime
from typing import List, Optional
from pathlib import Path
from contextlib import contextmanager

from ...domain.repositories.market_data_repository import MarketDataRepository, RepositoryError
from ...domain.entities.candle import Candle
from ...domain.entities.indicator import Indicator
from ...domain.entities.market_data import MarketData


class SQLiteMarketDataRepository(MarketDataRepository):
    """SQLite implementation of MarketDataRepository"""
    
    def __init__(self, db_path: str = "crypto_data.db"):
        self.db_path = db_path
        self._memory_conn = None
        if db_path == ":memory:":
            self._memory_conn = sqlite3.connect(":memory:")
        self._init_database()
    
    @contextmanager
    def _get_connection(self):
        """Context manager for database connections"""
        if self._memory_conn:
            yield self._memory_conn
        else:
            conn = sqlite3.connect(self.db_path)
            try:
                yield conn
            finally:
                conn.close()
    
    def _init_database(self) -> None:
        """Initialize database tables"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            for table in ['btc_15m', 'btc_1h']:
                cursor.execute(f'''
                    CREATE TABLE IF NOT EXISTS {table} (
                        timestamp TEXT PRIMARY KEY,
                        open REAL,
                        high REAL,
                        low REAL,
                        close REAL,
                        volume REAL,
                        ema_7 REAL,
                        rsi_6 REAL,
                        volume_ma_20 REAL
                    )
                ''')
            
            conn.commit()
    
    def _get_table_name(self, timeframe: str) -> str:
        """Convert timeframe to table name"""
        return f"btc_{timeframe}"
    
    def save_candle(self, candle: Candle, indicator: Indicator, timeframe: str) -> None:
        """Save candle with indicators"""
        try:
            table = self._get_table_name(timeframe)
            
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(f'''
                    INSERT OR REPLACE INTO {table}
                    (timestamp, open, high, low, close, volume, ema_7, rsi_6, volume_ma_20)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    candle.timestamp.isoformat(),
                    candle.open,
                    candle.high,
                    candle.low,
                    candle.close,
                    candle.volume,
                    indicator.ema_7,
                    indicator.rsi_6,
                    indicator.volume_ma_20
                ))
                conn.commit()
        except Exception as e:
            raise RepositoryError(f"Failed to save candle: {e}", e)
    
    def save_market_data(self, market_data: MarketData) -> None:
        """Save market data aggregate"""
        self.save_candle(
            market_data.candle,
            market_data.indicator,
            market_data.timeframe
        )
    
    def get_latest_candles(self, timeframe: str, limit: int = 100) -> List[MarketData]:
        """Get latest N candles"""
        try:
            table = self._get_table_name(timeframe)
            
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(f'''
                    SELECT timestamp, open, high, low, close, volume,
                           ema_7, rsi_6, volume_ma_20
                    FROM {table}
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (limit,))
                
                results = []
                for row in cursor.fetchall():
                    candle = Candle(
                        timestamp=datetime.fromisoformat(row[0]),
                        open=row[1],
                        high=row[2],
                        low=row[3],
                        close=row[4],
                        volume=row[5]
                    )
                    indicator = Indicator(
                        ema_7=row[6],
                        rsi_6=row[7],
                        volume_ma_20=row[8]
                    )
                    market_data = MarketData(candle, indicator, timeframe)
                    results.append(market_data)
                
                return results
        except Exception as e:
            raise RepositoryError(f"Failed to get candles: {e}", e)
    
    def get_candles_by_date_range(
        self,
        timeframe: str,
        start: datetime,
        end: datetime
    ) -> List[MarketData]:
        """Get candles within date range"""
        try:
            table = self._get_table_name(timeframe)
            
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(f'''
                    SELECT timestamp, open, high, low, close, volume,
                           ema_7, rsi_6, volume_ma_20
                    FROM {table}
                    WHERE timestamp BETWEEN ? AND ?
                    ORDER BY timestamp DESC
                ''', (start.isoformat(), end.isoformat()))
                
                results = []
                for row in cursor.fetchall():
                    candle = Candle(
                        timestamp=datetime.fromisoformat(row[0]),
                        open=row[1], high=row[2], low=row[3],
                        close=row[4], volume=row[5]
                    )
                    indicator = Indicator(ema_7=row[6], rsi_6=row[7], volume_ma_20=row[8])
                    results.append(MarketData(candle, indicator, timeframe))
                
                return results
        except Exception as e:
            raise RepositoryError(f"Failed to get candles by date range: {e}", e)
    
    def get_candle_by_timestamp(
        self,
        timeframe: str,
        timestamp: datetime
    ) -> Optional[MarketData]:
        """Get specific candle by timestamp"""
        try:
            table = self._get_table_name(timeframe)
            
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(f'''
                    SELECT timestamp, open, high, low, close, volume,
                           ema_7, rsi_6, volume_ma_20
                    FROM {table}
                    WHERE timestamp = ?
                ''', (timestamp.isoformat(),))
                
                row = cursor.fetchone()
                if not row:
                    return None
                
                candle = Candle(
                    timestamp=datetime.fromisoformat(row[0]),
                    open=row[1], high=row[2], low=row[3],
                    close=row[4], volume=row[5]
                )
                indicator = Indicator(ema_7=row[6], rsi_6=row[7], volume_ma_20=row[8])
                return MarketData(candle, indicator, timeframe)
        except Exception as e:
            raise RepositoryError(f"Failed to get candle: {e}", e)
    
    def get_record_count(self, timeframe: str) -> int:
        """Get total record count"""
        try:
            table = self._get_table_name(timeframe)
            
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(f'SELECT COUNT(*) FROM {table}')
                return cursor.fetchone()[0]
        except Exception as e:
            raise RepositoryError(f"Failed to get record count: {e}", e)
    
    def get_latest_timestamp(self, timeframe: str) -> Optional[datetime]:
        """Get latest timestamp"""
        try:
            table = self._get_table_name(timeframe)
            
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(f'SELECT MAX(timestamp) FROM {table}')
                result = cursor.fetchone()[0]
                return datetime.fromisoformat(result) if result else None
        except Exception as e:
            raise RepositoryError(f"Failed to get latest timestamp: {e}", e)
    
    def delete_candles_before(self, timeframe: str, before: datetime) -> int:
        """Delete candles before date"""
        try:
            table = self._get_table_name(timeframe)
            
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(f'''
                    DELETE FROM {table}
                    WHERE timestamp < ?
                ''', (before.isoformat(),))
                conn.commit()
                return cursor.rowcount
        except Exception as e:
            raise RepositoryError(f"Failed to delete candles: {e}", e)
    
    def get_database_size(self) -> float:
        """Get database size in MB"""
        try:
            if self.db_path == ":memory:":
                return 0.0
            
            path = Path(self.db_path)
            if path.exists():
                return path.stat().st_size / (1024 * 1024)
            return 0.0
        except Exception as e:
            raise RepositoryError(f"Failed to get database size: {e}", e)
    
    def backup_database(self, backup_path: str) -> None:
        """Backup database"""
        try:
            if self.db_path == ":memory:":
                raise RepositoryError("Cannot backup in-memory database")
            
            # Create backup directory if needed
            Path(backup_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Copy database file
            shutil.copy2(self.db_path, backup_path)
        except Exception as e:
            raise RepositoryError(f"Failed to backup database: {e}", e)
    
    def get_table_info(self, timeframe: str) -> dict:
        """Get table information"""
        try:
            table = self._get_table_name(timeframe)
            
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Get record count
                cursor.execute(f'SELECT COUNT(*) FROM {table}')
                record_count = cursor.fetchone()[0]
                
                # Get latest record
                cursor.execute(f'SELECT MAX(timestamp) FROM {table}')
                latest = cursor.fetchone()[0]
                
                # Get oldest record
                cursor.execute(f'SELECT MIN(timestamp) FROM {table}')
                oldest = cursor.fetchone()[0]
                
                return {
                    'record_count': record_count,
                    'size_mb': self.get_database_size(),
                    'latest_record': latest,
                    'oldest_record': oldest
                }
        except Exception as e:
            raise RepositoryError(f"Failed to get table info: {e}", e)
