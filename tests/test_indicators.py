"""
Unit tests for indicator calculator.

Tests technical indicator calculations using sample OHLCV data.
Uses fallback implementation if TA-Lib is not available.
"""

import pytest
import pandas as pd
import numpy as np
from src.indicators import IndicatorCalculator, IndicatorCalculatorFallback, TALIB_AVAILABLE


@pytest.fixture
def sample_ohlcv_data():
    """Fixture providing sample OHLCV data for testing."""
    # Generate 100 data points with realistic price movements
    np.random.seed(42)
    
    timestamps = pd.date_range(start='2024-01-01', periods=100, freq='15min')
    base_price = 50000.0
    
    # Generate realistic price data with trend and volatility
    close_prices = []
    current_price = base_price
    
    for i in range(100):
        # Add trend and random walk
        change = np.random.normal(0, 100)  # Random change
        current_price = current_price + change
        close_prices.append(current_price)
    
    close_prices = np.array(close_prices)
    
    df = pd.DataFrame({
        'open_time': [int(ts.timestamp() * 1000) for ts in timestamps],
        'open': close_prices * 0.999,  # Slightly lower than close
        'high': close_prices * 1.002,  # Slightly higher
        'low': close_prices * 0.998,   # Slightly lower
        'close': close_prices,
        'volume': np.random.uniform(50, 150, 100)
    })
    
    return df


@pytest.fixture
def small_ohlcv_data():
    """Fixture providing small OHLCV dataset for edge case testing."""
    df = pd.DataFrame({
        'open_time': [1699999999000 + i * 900000 for i in range(10)],
        'open': [50000.0 + i * 100 for i in range(10)],
        'high': [50100.0 + i * 100 for i in range(10)],
        'low': [49900.0 + i * 100 for i in range(10)],
        'close': [50000.0 + i * 100 for i in range(10)],
        'volume': [100.0 + i * 10 for i in range(10)]
    })
    return df


class TestIndicatorCalculator:
    """Test suite for IndicatorCalculator class."""
    
    @pytest.mark.skipif(not TALIB_AVAILABLE, reason="TA-Lib not installed")
    def test_calculate_all_with_talib(self, sample_ohlcv_data):
        """Test calculate_all with TA-Lib."""
        df = IndicatorCalculator.calculate_all(sample_ohlcv_data)
        
        # Verify indicator columns were added
        assert 'ema_7' in df.columns
        assert 'rsi_6' in df.columns
        assert 'volume_ma_20' in df.columns
        
        # Verify index is datetime
        assert isinstance(df.index, pd.DatetimeIndex)
        
        # Verify data types
        assert df['ema_7'].dtype == np.float64
        assert df['rsi_6'].dtype == np.float64
        assert df['volume_ma_20'].dtype == np.float64
        
        # Verify RSI range (0-100)
        rsi_values = df['rsi_6'].dropna()
        assert rsi_values.min() >= 0
        assert rsi_values.max() <= 100
        
        # Verify NaN values only in initial periods
        # EMA(7) should have ~6 NaN values at start
        # RSI(6) should have ~6 NaN values at start
        # Volume MA(20) should have ~19 NaN values at start
        assert df['ema_7'].isna().sum() <= 10
        assert df['rsi_6'].isna().sum() <= 10
        assert df['volume_ma_20'].isna().sum() <= 25
    
    def test_calculate_all_with_fallback(self, sample_ohlcv_data):
        """Test calculate_all with fallback implementation."""
        df = IndicatorCalculatorFallback.calculate_all(sample_ohlcv_data)
        
        # Verify indicator columns were added
        assert 'ema_7' in df.columns
        assert 'rsi_6' in df.columns
        assert 'volume_ma_20' in df.columns
        
        # Verify index is datetime
        assert isinstance(df.index, pd.DatetimeIndex)
        
        # Verify RSI range
        rsi_values = df['rsi_6'].dropna()
        if len(rsi_values) > 0:
            assert rsi_values.min() >= 0
            assert rsi_values.max() <= 100
    
    @pytest.mark.skipif(not TALIB_AVAILABLE, reason="TA-Lib not installed")
    def test_calculate_ema(self, sample_ohlcv_data):
        """Test EMA calculation."""
        df = sample_ohlcv_data.copy()
        df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
        df.set_index('open_time', inplace=True)
        
        ema = IndicatorCalculator.calculate_ema(df, period=7)
        
        assert isinstance(ema, pd.Series)
        assert len(ema) == len(df)
        assert ema.dtype == np.float64
        
        # EMA should be close to price values
        close_prices = df['close']
        ema_values = ema.dropna()
        assert ema_values.min() > close_prices.min() * 0.9
        assert ema_values.max() < close_prices.max() * 1.1
    
    @pytest.mark.skipif(not TALIB_AVAILABLE, reason="TA-Lib not installed")
    def test_calculate_rsi(self, sample_ohlcv_data):
        """Test RSI calculation."""
        df = sample_ohlcv_data.copy()
        df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
        df.set_index('open_time', inplace=True)
        
        rsi = IndicatorCalculator.calculate_rsi(df, period=6)
        
        assert isinstance(rsi, pd.Series)
        assert len(rsi) == len(df)
        
        # Check RSI range
        rsi_values = rsi.dropna()
        assert len(rsi_values) > 0
        assert rsi_values.min() >= 0
        assert rsi_values.max() <= 100
    
    @pytest.mark.skipif(not TALIB_AVAILABLE, reason="TA-Lib not installed")
    def test_calculate_volume_ma(self, sample_ohlcv_data):
        """Test Volume MA calculation."""
        df = sample_ohlcv_data.copy()
        df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
        df.set_index('open_time', inplace=True)
        
        volume_ma = IndicatorCalculator.calculate_volume_ma(df, period=20)
        
        assert isinstance(volume_ma, pd.Series)
        assert len(volume_ma) == len(df)
        
        # Volume MA should be close to actual volume values
        volume_values = df['volume']
        ma_values = volume_ma.dropna()
        assert ma_values.min() > volume_values.min() * 0.5
        assert ma_values.max() < volume_values.max() * 1.5
    
    @pytest.mark.skipif(not TALIB_AVAILABLE, reason="TA-Lib not installed")
    def test_missing_columns(self):
        """Test error handling for missing columns."""
        df = pd.DataFrame({
            'open_time': [1699999999000],
            'close': [50000.0]
            # Missing 'volume' column
        })
        
        with pytest.raises(ValueError) as exc_info:
            IndicatorCalculator.calculate_all(df)
        
        assert "Missing required columns" in str(exc_info.value)
        assert "volume" in str(exc_info.value)
    
    @pytest.mark.skipif(not TALIB_AVAILABLE, reason="TA-Lib not installed")
    def test_insufficient_data(self, small_ohlcv_data):
        """Test handling of insufficient data for indicators."""
        # Only 10 data points, but Volume MA needs 20
        df = IndicatorCalculator.calculate_all(small_ohlcv_data)
        
        # Should not crash, but volume_ma_20 will be all NaN
        assert 'volume_ma_20' in df.columns
        # All values should be NaN since we need 20 periods
        assert df['volume_ma_20'].isna().all()
        
        # But EMA(7) and RSI(6) should have some valid values
        assert not df['ema_7'].isna().all()
        assert not df['rsi_6'].isna().all()
    
    @pytest.mark.skipif(not TALIB_AVAILABLE, reason="TA-Lib not installed")
    def test_validate_indicators_success(self, sample_ohlcv_data):
        """Test indicator validation with valid data."""
        df = IndicatorCalculator.calculate_all(sample_ohlcv_data)
        validation = IndicatorCalculator.validate_indicators(df)
        
        assert validation['valid'] is True
        assert len(validation['issues']) == 0
    
    @pytest.mark.skipif(not TALIB_AVAILABLE, reason="TA-Lib not installed")
    def test_validate_indicators_missing_column(self, sample_ohlcv_data):
        """Test indicator validation with missing columns."""
        df = sample_ohlcv_data.copy()
        # Don't calculate indicators
        
        validation = IndicatorCalculator.validate_indicators(df)
        
        assert validation['valid'] is False
        assert len(validation['issues']) > 0
        assert any('Missing indicator column' in issue for issue in validation['issues'])
    
    @pytest.mark.skipif(not TALIB_AVAILABLE, reason="TA-Lib not installed")
    def test_validate_indicators_rsi_range(self, sample_ohlcv_data):
        """Test RSI range validation."""
        df = IndicatorCalculator.calculate_all(sample_ohlcv_data)
        
        # Manually corrupt RSI values
        df['rsi_6'] = 150.0  # Invalid: > 100
        
        validation = IndicatorCalculator.validate_indicators(df)
        
        assert validation['valid'] is False
        assert any('RSI values out of range' in issue for issue in validation['issues'])
    
    @pytest.mark.skipif(not TALIB_AVAILABLE, reason="TA-Lib not installed")
    def test_datetime_index_conversion(self, sample_ohlcv_data):
        """Test that open_time is properly converted to datetime index."""
        df = IndicatorCalculator.calculate_all(sample_ohlcv_data)
        
        # Verify index is DatetimeIndex
        assert isinstance(df.index, pd.DatetimeIndex)
        
        # Verify index name
        assert df.index.name == 'open_time'
        
        # Verify timestamps are in correct order
        assert df.index.is_monotonic_increasing
    
    @pytest.mark.skipif(not TALIB_AVAILABLE, reason="TA-Lib not installed")
    def test_original_dataframe_not_modified(self, sample_ohlcv_data):
        """Test that original DataFrame is not modified."""
        original_columns = sample_ohlcv_data.columns.tolist()
        original_index = sample_ohlcv_data.index.copy()
        
        # Calculate indicators
        df_with_indicators = IndicatorCalculator.calculate_all(sample_ohlcv_data)
        
        # Verify original DataFrame unchanged
        assert sample_ohlcv_data.columns.tolist() == original_columns
        assert sample_ohlcv_data.index.equals(original_index)
        assert 'ema_7' not in sample_ohlcv_data.columns
    
    @pytest.mark.skipif(not TALIB_AVAILABLE, reason="TA-Lib not installed")
    def test_type_conversion_to_float64(self, sample_ohlcv_data):
        """Test that values are properly converted to float64 for TA-Lib."""
        # Convert close to int (should be converted back to float64)
        df = sample_ohlcv_data.copy()
        df['close'] = df['close'].astype(int)
        df['volume'] = df['volume'].astype(int)
        
        # Should not raise error
        result = IndicatorCalculator.calculate_all(df)
        
        # Verify indicators are float64
        assert result['ema_7'].dtype == np.float64
        assert result['rsi_6'].dtype == np.float64
        assert result['volume_ma_20'].dtype == np.float64
    
    def test_fallback_implementation_available(self):
        """Test that fallback implementation is always available."""
        # Fallback should work even without TA-Lib
        df = pd.DataFrame({
            'open_time': [1699999999000 + i * 900000 for i in range(50)],
            'open': [50000.0 + i * 10 for i in range(50)],
            'high': [50100.0 + i * 10 for i in range(50)],
            'low': [49900.0 + i * 10 for i in range(50)],
            'close': [50000.0 + i * 10 for i in range(50)],
            'volume': [100.0 + i for i in range(50)]
        })
        
        result = IndicatorCalculatorFallback.calculate_all(df)
        
        assert 'ema_7' in result.columns
        assert 'rsi_6' in result.columns
        assert 'volume_ma_20' in result.columns


# Test for TA-Lib not installed scenario
@pytest.mark.skipif(TALIB_AVAILABLE, reason="TA-Lib is installed")
def test_talib_not_installed_error():
    """Test that appropriate error is raised when TA-Lib is not installed."""
    df = pd.DataFrame({
        'open_time': [1699999999000],
        'close': [50000.0],
        'volume': [100.0]
    })
    
    with pytest.raises(ImportError) as exc_info:
        IndicatorCalculator.calculate_all(df)
    
    assert "TA-Lib is not installed" in str(exc_info.value)
