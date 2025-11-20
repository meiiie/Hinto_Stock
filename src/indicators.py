"""
Technical indicator calculator using TA-Lib.

Provides methods to calculate technical indicators (EMA, RSI, Volume MA)
on OHLCV data using the industry-standard TA-Lib library.
"""

import pandas as pd
import numpy as np
from typing import Optional

# Try to import TA-Lib, provide helpful error if not installed
try:
    import talib
    TALIB_AVAILABLE = True
except ImportError:
    TALIB_AVAILABLE = False
    print("⚠️  Warning: TA-Lib not installed")
    print("   Download from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib")
    print("   For Python 3.13: TA_Lib-0.4.32-cp313-cp313-win_amd64.whl")
    print("   Install: pip install <downloaded_wheel_file>")


class IndicatorCalculator:
    """
    Calculator for technical indicators using TA-Lib.
    
    Provides static methods to calculate common technical indicators
    on OHLCV (Open, High, Low, Close, Volume) data.
    
    Indicators:
        - EMA (Exponential Moving Average)
        - RSI (Relative Strength Index)
        - Volume MA (Volume Moving Average)
    """
    
    @staticmethod
    def calculate_all(df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate all technical indicators on OHLCV data.
        
        Adds the following columns to the DataFrame:
            - ema_7: 7-period Exponential Moving Average
            - rsi_6: 6-period Relative Strength Index
            - volume_ma_20: 20-period Simple Moving Average of volume
        
        Args:
            df (pd.DataFrame): DataFrame with columns [open_time, open, high, low, close, volume]
        
        Returns:
            pd.DataFrame: DataFrame with added indicator columns and datetime index
        
        Raises:
            ImportError: If TA-Lib is not installed
            ValueError: If required columns are missing
        
        Example:
            >>> df = client.get_klines("BTCUSDT", "15m", 100)
            >>> df = IndicatorCalculator.calculate_all(df)
            >>> print(df[['close', 'ema_7', 'rsi_6', 'volume_ma_20']].tail())
        """
        if not TALIB_AVAILABLE:
            raise ImportError(
                "TA-Lib is not installed. "
                "Please install it from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib"
            )
        
        # Validate required columns
        required_columns = ['open_time', 'close', 'volume']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        # Create a copy to avoid modifying original
        df = df.copy()
        
        # Convert open_time to datetime and set as index
        df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
        df.set_index('open_time', inplace=True)
        
        # Ensure close and volume are float64 for TA-Lib compatibility
        close_prices = df['close'].astype('float64').values
        volume_data = df['volume'].astype('float64').values
        
        # Calculate EMA(7) - Exponential Moving Average
        df['ema_7'] = talib.EMA(close_prices, timeperiod=7)
        
        # Calculate RSI(6) - Relative Strength Index
        df['rsi_6'] = talib.RSI(close_prices, timeperiod=6)
        
        # Calculate Volume MA(20) - Simple Moving Average of volume
        df['volume_ma_20'] = talib.SMA(volume_data, timeperiod=20)
        
        return df
    
    @staticmethod
    def calculate_ema(df: pd.DataFrame, period: int = 7, column: str = 'close') -> pd.Series:
        """
        Calculate Exponential Moving Average.
        
        Args:
            df (pd.DataFrame): DataFrame with price data
            period (int): EMA period (default: 7)
            column (str): Column name to calculate EMA on (default: 'close')
        
        Returns:
            pd.Series: EMA values
        
        Raises:
            ImportError: If TA-Lib is not installed
        """
        if not TALIB_AVAILABLE:
            raise ImportError("TA-Lib is not installed")
        
        values = df[column].astype('float64').values
        return pd.Series(talib.EMA(values, timeperiod=period), index=df.index)
    
    @staticmethod
    def calculate_rsi(df: pd.DataFrame, period: int = 6, column: str = 'close') -> pd.Series:
        """
        Calculate Relative Strength Index.
        
        Args:
            df (pd.DataFrame): DataFrame with price data
            period (int): RSI period (default: 6)
            column (str): Column name to calculate RSI on (default: 'close')
        
        Returns:
            pd.Series: RSI values (0-100 range)
        
        Raises:
            ImportError: If TA-Lib is not installed
        """
        if not TALIB_AVAILABLE:
            raise ImportError("TA-Lib is not installed")
        
        values = df[column].astype('float64').values
        return pd.Series(talib.RSI(values, timeperiod=period), index=df.index)
    
    @staticmethod
    def calculate_volume_ma(df: pd.DataFrame, period: int = 20) -> pd.Series:
        """
        Calculate Simple Moving Average of volume.
        
        Args:
            df (pd.DataFrame): DataFrame with volume data
            period (int): MA period (default: 20)
        
        Returns:
            pd.Series: Volume MA values
        
        Raises:
            ImportError: If TA-Lib is not installed
        """
        if not TALIB_AVAILABLE:
            raise ImportError("TA-Lib is not installed")
        
        volume_data = df['volume'].astype('float64').values
        return pd.Series(talib.SMA(volume_data, timeperiod=period), index=df.index)
    
    @staticmethod
    def validate_indicators(df: pd.DataFrame) -> dict:
        """
        Validate calculated indicators.
        
        Checks:
            - RSI values are in range 0-100
            - No unexpected NaN values (except for initial periods)
            - Indicators are numeric
        
        Args:
            df (pd.DataFrame): DataFrame with calculated indicators
        
        Returns:
            dict: Validation results with 'valid' (bool) and 'issues' (list)
        
        Example:
            >>> df = IndicatorCalculator.calculate_all(df)
            >>> validation = IndicatorCalculator.validate_indicators(df)
            >>> if not validation['valid']:
            ...     print(f"Issues: {validation['issues']}")
        """
        issues = []
        
        # Check if indicator columns exist
        indicator_columns = ['ema_7', 'rsi_6', 'volume_ma_20']
        for col in indicator_columns:
            if col not in df.columns:
                issues.append(f"Missing indicator column: {col}")
        
        if issues:
            return {'valid': False, 'issues': issues}
        
        # Check RSI range (0-100)
        rsi_values = df['rsi_6'].dropna()
        if len(rsi_values) > 0:
            if rsi_values.min() < 0 or rsi_values.max() > 100:
                issues.append(f"RSI values out of range: [{rsi_values.min():.2f}, {rsi_values.max():.2f}]")
        
        # Check for unexpected NaN values (allow first N periods)
        for col in indicator_columns:
            # Get period for each indicator
            periods = {'ema_7': 7, 'rsi_6': 6, 'volume_ma_20': 20}
            period = periods.get(col, 0)
            
            # Check values after warmup period
            values_after_warmup = df[col].iloc[period:]
            nan_count = values_after_warmup.isna().sum()
            
            if nan_count > 0:
                issues.append(f"{col}: {nan_count} unexpected NaN values after warmup period")
        
        # Check if values are numeric
        for col in indicator_columns:
            if not pd.api.types.is_numeric_dtype(df[col]):
                issues.append(f"{col}: Non-numeric data type")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues
        }


# Fallback implementation without TA-Lib (for testing/development)
class IndicatorCalculatorFallback:
    """
    Fallback indicator calculator using pandas (without TA-Lib).
    
    Provides basic implementations for testing when TA-Lib is not available.
    Note: Results may differ slightly from TA-Lib due to different algorithms.
    """
    
    @staticmethod
    def calculate_all(df: pd.DataFrame) -> pd.DataFrame:
        """Calculate indicators using pandas (fallback method)."""
        df = df.copy()
        
        # Convert open_time to datetime and set as index
        df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
        df.set_index('open_time', inplace=True)
        
        # EMA using pandas
        df['ema_7'] = df['close'].ewm(span=7, adjust=False).mean()
        
        # RSI using pandas (simplified)
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=6).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=6).mean()
        rs = gain / loss
        df['rsi_6'] = 100 - (100 / (1 + rs))
        
        # Volume MA using pandas
        df['volume_ma_20'] = df['volume'].rolling(window=20).mean()
        
        return df
