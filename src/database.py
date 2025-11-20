"""
Database manager for SQLite operations.

Handles all database interactions including table creation, data insertion,
and querying for the Binance Data Pipeline.
"""

import sqlite3
import pandas as pd
from typing import Optional, List
from contextlib import contextmanager
from pathlib import Path


class DatabaseManager:
    """
    Manager for SQLite database operations.
    
    Provides methods to create tables, save data, and query records
    with proper connection management and error handling.
    
    Attributes:
        db_path (str): Path to SQLite database file
    """
    
    def __init__(self, db_path: str = "crypto_data.db"):
        """
        Initialize database manager.
        
        Args:
            db_path (str): Path to SQLite database file (default: "crypto_data.db")
        """
        self.db_path = db_path
        # For in-memory databases, keep a persistent connection
        self._memory_conn = None
        if db_path == ":memory:":
            self._memory_conn = sqlite3.connect(":memory:")
        self.init_database()
    
    @contextmanager
    def get_connection(self):
        """
        Context manager for database connections.
        
        Ensures connections are properly closed after use.
        For in-memory databases, reuses the persistent connection.
        
        Yields:
            sqlite3.Connection: Database connection
        
        Example:
            >>> with db_manager.get_connection() as conn:
            ...     cursor = conn.cursor()
            ...     cursor.execute("SELECT * FROM btc_15m LIMIT 5")
        """
        if self._memory_conn:
            # For in-memory, use persistent connection
            yield self._memory_conn
        else:
            # For file-based, create new connection
            conn = sqlite3.connect(self.db_path)
            try:
                yield conn
            finally:
                conn.close()
    
    def init_database(self) -> None:
        """
        Initialize database and create tables if they don't exist.
        
        Creates two tables:
            - btc_15m: For 15-minute timeframe data
            - btc_1h: For 1-hour timeframe data
        
        Both tables have the same schema with timestamp as PRIMARY KEY
        to prevent duplicate records.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Create table for 15-minute data
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS btc_15m (
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
            
            # Create table for 1-hour data
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS btc_1h (
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
    
    def save_data(self, df: pd.DataFrame, table_name: str) -> int:
        """
        Save DataFrame to database table.
        
        Uses 'replace' strategy to handle duplicate timestamps.
        The DataFrame index should be datetime (timestamp).
        
        Args:
            df (pd.DataFrame): DataFrame with indicator data and datetime index
            table_name (str): Target table name ('btc_15m' or 'btc_1h')
        
        Returns:
            int: Number of rows inserted/updated
        
        Raises:
            ValueError: If table_name is invalid or DataFrame is empty
            sqlite3.Error: If database operation fails
        
        Example:
            >>> df = client.get_klines("BTCUSDT", "15m", 100)
            >>> df = IndicatorCalculator.calculate_all(df)
            >>> rows_saved = db_manager.save_data(df, "btc_15m")
            >>> print(f"Saved {rows_saved} rows")
        """
        # Validate table name
        valid_tables = ['btc_15m', 'btc_1h']
        if table_name not in valid_tables:
            raise ValueError(f"Invalid table name: {table_name}. Must be one of {valid_tables}")
        
        # Validate DataFrame
        if df.empty:
            raise ValueError("Cannot save empty DataFrame")
        
        # Prepare DataFrame for insertion
        df_to_save = df.copy()
        
        # Reset index to make timestamp a column
        df_to_save = df_to_save.reset_index()
        
        # Convert timestamp to string format
        if 'open_time' in df_to_save.columns:
            df_to_save['timestamp'] = df_to_save['open_time'].astype(str)
            df_to_save = df_to_save.drop('open_time', axis=1)
        else:
            # Index is already timestamp
            df_to_save['timestamp'] = df_to_save.index.astype(str)
        
        # Ensure all required columns exist
        required_columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume',
                          'ema_7', 'rsi_6', 'volume_ma_20']
        
        # Reorder columns to match table schema
        df_to_save = df_to_save[required_columns]
        
        # Save to database
        with self.get_connection() as conn:
            try:
                # Try to append data
                rows_affected = df_to_save.to_sql(
                    table_name,
                    conn,
                    if_exists='append',
                    index=False,
                    method='multi'
                )
                conn.commit()
                return len(df_to_save)
            
            except sqlite3.IntegrityError:
                # Handle duplicate timestamps by using INSERT OR REPLACE
                cursor = conn.cursor()
                
                for _, row in df_to_save.iterrows():
                    cursor.execute(f"""
                        INSERT OR REPLACE INTO {table_name}
                        (timestamp, open, high, low, close, volume, ema_7, rsi_6, volume_ma_20)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, tuple(row))
                
                conn.commit()
                return len(df_to_save)
    
    def get_record_count(self, table_name: str) -> int:
        """
        Get total number of records in a table.
        
        Args:
            table_name (str): Table name ('btc_15m' or 'btc_1h')
        
        Returns:
            int: Number of records
        
        Raises:
            ValueError: If table_name is invalid
        """
        valid_tables = ['btc_15m', 'btc_1h']
        if table_name not in valid_tables:
            raise ValueError(f"Invalid table name: {table_name}")
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            return count
    
    def get_latest_records(self, table_name: str, limit: int = 100) -> pd.DataFrame:
        """
        Fetch latest N records from a table.
        
        Records are ordered by timestamp in descending order.
        
        Args:
            table_name (str): Table name ('btc_15m' or 'btc_1h')
            limit (int): Number of records to fetch (default: 100)
        
        Returns:
            pd.DataFrame: DataFrame with latest records, empty if no data
        
        Raises:
            ValueError: If table_name is invalid or limit is invalid
        """
        valid_tables = ['btc_15m', 'btc_1h']
        if table_name not in valid_tables:
            raise ValueError(f"Invalid table name: {table_name}")
        
        if limit <= 0:
            raise ValueError("Limit must be positive")
        
        with self.get_connection() as conn:
            query = f"""
                SELECT * FROM {table_name}
                ORDER BY timestamp DESC
                LIMIT ?
            """
            df = pd.read_sql_query(query, conn, params=(limit,))
            
            # Convert timestamp back to datetime
            if not df.empty and 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df = df.set_index('timestamp')
            
            return df
    
    def get_records_by_date_range(
        self,
        table_name: str,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """
        Fetch records within a date range.
        
        Args:
            table_name (str): Table name ('btc_15m' or 'btc_1h')
            start_date (str): Start date (ISO format: 'YYYY-MM-DD HH:MM:SS')
            end_date (str): End date (ISO format: 'YYYY-MM-DD HH:MM:SS')
        
        Returns:
            pd.DataFrame: DataFrame with records in date range
        
        Raises:
            ValueError: If table_name is invalid
        """
        valid_tables = ['btc_15m', 'btc_1h']
        if table_name not in valid_tables:
            raise ValueError(f"Invalid table name: {table_name}")
        
        with self.get_connection() as conn:
            query = f"""
                SELECT * FROM {table_name}
                WHERE timestamp BETWEEN ? AND ?
                ORDER BY timestamp ASC
            """
            df = pd.read_sql_query(query, conn, params=(start_date, end_date))
            
            # Convert timestamp back to datetime
            if not df.empty and 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df = df.set_index('timestamp')
            
            return df
    
    def delete_old_records(self, table_name: str, days_to_keep: int = 90) -> int:
        """
        Delete records older than specified days.
        
        Useful for data retention management.
        
        Args:
            table_name (str): Table name ('btc_15m' or 'btc_1h')
            days_to_keep (int): Number of days to keep (default: 90)
        
        Returns:
            int: Number of records deleted
        
        Raises:
            ValueError: If table_name is invalid
        """
        valid_tables = ['btc_15m', 'btc_1h']
        if table_name not in valid_tables:
            raise ValueError(f"Invalid table name: {table_name}")
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Calculate cutoff date
            cutoff_query = f"""
                DELETE FROM {table_name}
                WHERE timestamp < datetime('now', '-{days_to_keep} days')
            """
            
            cursor.execute(cutoff_query)
            deleted_count = cursor.rowcount
            conn.commit()
            
            return deleted_count
    
    def get_table_info(self, table_name: str) -> dict:
        """
        Get information about a table.
        
        Args:
            table_name (str): Table name ('btc_15m' or 'btc_1h')
        
        Returns:
            dict: Table information including record count, date range, etc.
        """
        valid_tables = ['btc_15m', 'btc_1h']
        if table_name not in valid_tables:
            raise ValueError(f"Invalid table name: {table_name}")
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get record count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            
            # Get date range
            cursor.execute(f"""
                SELECT MIN(timestamp), MAX(timestamp)
                FROM {table_name}
            """)
            date_range = cursor.fetchone()
            
            # Get database file size (not table-specific for SQLite)
            # For in-memory databases, size is not meaningful
            size_bytes = 0
            if self.db_path != ":memory:":
                try:
                    db_file = Path(self.db_path)
                    if db_file.exists():
                        size_bytes = db_file.stat().st_size
                except Exception:
                    size_bytes = 0
            
            return {
                'table_name': table_name,
                'record_count': count,
                'earliest_record': date_range[0] if date_range[0] else None,
                'latest_record': date_range[1] if date_range[1] else None,
                'size_bytes': size_bytes,
                'size_mb': round(size_bytes / (1024 * 1024), 2) if size_bytes else 0
            }
    
    def __repr__(self) -> str:
        """
        String representation of DatabaseManager.
        
        Returns:
            str: String representation
        """
        db_exists = Path(self.db_path).exists()
        return f"DatabaseManager(db_path='{self.db_path}', exists={db_exists})"
