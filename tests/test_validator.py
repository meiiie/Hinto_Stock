"""
Unit tests for data validator.

Tests validation logic using synthetic data with known issues.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from src.validator import DataValidator
from src.database import DatabaseManager


@pytest.fixture
def in_memory_db():
    """Fixture providing an in-memory database."""
    return DatabaseManager(db_path=":memory:")


@pytest.fixture
def validator(in_memory_db):
    """Fixture providing a DataValidator instance."""
    return DataValidator(in_memory_db)


@pytest.fixture
def valid_data():
    """Fixture providing valid data without issues."""
    timestamps = pd.date_range(start='2024-01-01', periods=50, freq='15min')
    
    df = pd.DataFrame({
        'open': np.random.uniform(49000, 51000, 50),
        'high': np.random.uniform(50000, 52000, 50),
        'low': np.random.uniform(48000, 50000, 50),
        'close': np.random.uniform(49500, 50500, 50),
        'volume': np.random.uniform(100, 200, 50),
        'ema_7': np.random.uniform(49500, 50500, 50),
        'rsi_6': np.random.uniform(30, 70, 50),
        'volume_ma_20': np.random.uniform(120, 180, 50)
    }, index=timestamps)
    
    df.index.name = 'open_time'
    return df


class TestDataValidator:
    """Test suite for DataValidator class."""
    
    def test_initialization(self, in_memory_db):
        """Test validator initialization."""
        validator = DataValidator(in_memory_db)
        
        assert validator.db_manager == in_memory_db
        assert isinstance(validator, DataValidator)
    
    def test_check_record_counts_empty_table(self, validator):
        """Test record count check on empty table."""
        result = validator.check_record_counts('btc_15m')
        
        assert result['table'] == 'btc_15m'
        assert result['count'] == 0
        assert result['status'] == 'empty'
    
    def test_check_record_counts_with_data(self, validator, in_memory_db, valid_data):
        """Test record count check with data."""
        in_memory_db.save_data(valid_data, 'btc_15m')
        
        result = validator.check_record_counts('btc_15m')
        
        assert result['table'] == 'btc_15m'
        assert result['count'] == len(valid_data)
        assert result['status'] == 'ok'
    
    def test_check_missing_values_no_data(self, validator):
        """Test missing values check on empty table."""
        result = validator.check_missing_values('btc_15m')
        
        assert result['has_issues'] is True
        assert 'No data to validate' in result['issues']
    
    def test_check_missing_values_valid_data(self, validator, in_memory_db, valid_data):
        """Test missing values check with valid data."""
        in_memory_db.save_data(valid_data, 'btc_15m')
        
        result = validator.check_missing_values('btc_15m', limit=50)
        
        # Should have no issues (warnings for initial NaN are ok)
        assert result['has_issues'] is False
    
    def test_check_missing_values_with_gaps(self, validator, in_memory_db):
        """Test missing values detection with data gaps."""
        timestamps = pd.date_range(start='2024-01-01', periods=50, freq='15min')
        
        df = pd.DataFrame({
            'open': np.random.uniform(49000, 51000, 50),
            'high': np.random.uniform(50000, 52000, 50),
            'low': np.random.uniform(48000, 50000, 50),
            'close': np.random.uniform(49500, 50500, 50),
            'volume': np.random.uniform(100, 200, 50),
            'ema_7': [np.nan] * 30 + list(np.random.uniform(49500, 50500, 20)),  # Too many NaN
            'rsi_6': np.random.uniform(30, 70, 50),
            'volume_ma_20': np.random.uniform(120, 180, 50)
        }, index=timestamps)
        
        df.index.name = 'open_time'
        in_memory_db.save_data(df, 'btc_15m')
        
        result = validator.check_missing_values('btc_15m', limit=50)
        
        # Should detect excessive missing values in ema_7
        assert result['has_issues'] is True
        assert any('ema_7' in issue for issue in result['issues'])
    
    def test_check_time_continuity_insufficient_data(self, validator, in_memory_db):
        """Test time continuity check with insufficient data."""
        timestamps = pd.date_range(start='2024-01-01', periods=1, freq='15min')
        
        df = pd.DataFrame({
            'open': [50000],
            'high': [51000],
            'low': [49000],
            'close': [50500],
            'volume': [100],
            'ema_7': [50500],
            'rsi_6': [50],
            'volume_ma_20': [100]
        }, index=timestamps)
        
        df.index.name = 'open_time'
        in_memory_db.save_data(df, 'btc_15m')
        
        result = validator.check_time_continuity('btc_15m', limit=10)
        
        assert result['has_warnings'] is True
        assert 'Insufficient data' in result['warnings'][0]
    
    def test_check_time_continuity_valid(self, validator, in_memory_db, valid_data):
        """Test time continuity check with valid continuous data."""
        in_memory_db.save_data(valid_data, 'btc_15m')
        
        result = validator.check_time_continuity('btc_15m', limit=50)
        
        # Should have no issues with continuous data
        assert result['has_issues'] is False
        assert result['details']['gaps_found'] == 0
    
    def test_check_time_continuity_with_gaps(self, validator, in_memory_db):
        """Test time continuity detection with time gaps."""
        # Create data with gaps
        timestamps1 = pd.date_range(start='2024-01-01 00:00', periods=10, freq='15min')
        timestamps2 = pd.date_range(start='2024-01-01 03:00', periods=10, freq='15min')  # 30min gap
        all_timestamps = timestamps1.append(timestamps2)
        
        df = pd.DataFrame({
            'open': np.random.uniform(49000, 51000, 20),
            'high': np.random.uniform(50000, 52000, 20),
            'low': np.random.uniform(48000, 50000, 20),
            'close': np.random.uniform(49500, 50500, 20),
            'volume': np.random.uniform(100, 200, 20),
            'ema_7': np.random.uniform(49500, 50500, 20),
            'rsi_6': np.random.uniform(30, 70, 20),
            'volume_ma_20': np.random.uniform(120, 180, 20)
        }, index=all_timestamps)
        
        df.index.name = 'open_time'
        in_memory_db.save_data(df, 'btc_15m')
        
        result = validator.check_time_continuity('btc_15m', limit=20)
        
        # Should detect the gap
        assert result['details']['gaps_found'] > 0
    
    def test_check_indicator_ranges_valid(self, validator, in_memory_db, valid_data):
        """Test indicator range check with valid data."""
        in_memory_db.save_data(valid_data, 'btc_15m')
        
        result = validator.check_indicator_ranges('btc_15m', limit=50)
        
        # Should have no issues
        assert result['has_issues'] is False
        
        # RSI should be in valid range
        if 'rsi_6' in result['details']:
            assert 0 <= result['details']['rsi_6']['min'] <= 100
            assert 0 <= result['details']['rsi_6']['max'] <= 100
    
    def test_check_indicator_ranges_rsi_out_of_range(self, validator, in_memory_db):
        """Test RSI range validation with out-of-range values."""
        timestamps = pd.date_range(start='2024-01-01', periods=20, freq='15min')
        
        df = pd.DataFrame({
            'open': np.random.uniform(49000, 51000, 20),
            'high': np.random.uniform(50000, 52000, 20),
            'low': np.random.uniform(48000, 50000, 20),
            'close': np.random.uniform(49500, 50500, 20),
            'volume': np.random.uniform(100, 200, 20),
            'ema_7': np.random.uniform(49500, 50500, 20),
            'rsi_6': [150.0] * 20,  # Invalid: > 100
            'volume_ma_20': np.random.uniform(120, 180, 20)
        }, index=timestamps)
        
        df.index.name = 'open_time'
        in_memory_db.save_data(df, 'btc_15m')
        
        result = validator.check_indicator_ranges('btc_15m', limit=20)
        
        # Should detect RSI out of range
        assert result['has_issues'] is True
        assert any('RSI out of range' in issue for issue in result['issues'])
    
    def test_check_indicator_ranges_negative_price(self, validator, in_memory_db):
        """Test price validation with negative values."""
        timestamps = pd.date_range(start='2024-01-01', periods=20, freq='15min')
        
        df = pd.DataFrame({
            'open': np.random.uniform(49000, 51000, 20),
            'high': np.random.uniform(50000, 52000, 20),
            'low': np.random.uniform(48000, 50000, 20),
            'close': [-100.0] * 20,  # Invalid: negative
            'volume': np.random.uniform(100, 200, 20),
            'ema_7': np.random.uniform(49500, 50500, 20),
            'rsi_6': np.random.uniform(30, 70, 20),
            'volume_ma_20': np.random.uniform(120, 180, 20)
        }, index=timestamps)
        
        df.index.name = 'open_time'
        in_memory_db.save_data(df, 'btc_15m')
        
        result = validator.check_indicator_ranges('btc_15m', limit=20)
        
        # Should detect negative price
        assert result['has_issues'] is True
        assert any('close' in issue and 'non-positive' in issue for issue in result['issues'])
    
    def test_validate_all_empty_table(self, validator):
        """Test validate_all on empty table."""
        results = validator.validate_all('btc_15m')
        
        assert results['valid'] is False
        assert results['table_name'] == 'btc_15m'
        assert 'No data' in results['issues'][0]
    
    def test_validate_all_valid_data(self, validator, in_memory_db, valid_data):
        """Test validate_all with valid data."""
        in_memory_db.save_data(valid_data, 'btc_15m')
        
        results = validator.validate_all('btc_15m', limit=50)
        
        # Should pass all checks (warnings are ok)
        assert results['valid'] is True
        assert results['table_name'] == 'btc_15m'
        assert 'record_count' in results['checks']
        assert 'missing_values' in results['checks']
        assert 'time_continuity' in results['checks']
        assert 'indicator_ranges' in results['checks']
    
    def test_validate_all_with_issues(self, validator, in_memory_db):
        """Test validate_all with data containing issues."""
        timestamps = pd.date_range(start='2024-01-01', periods=20, freq='15min')
        
        df = pd.DataFrame({
            'open': np.random.uniform(49000, 51000, 20),
            'high': np.random.uniform(50000, 52000, 20),
            'low': np.random.uniform(48000, 50000, 20),
            'close': np.random.uniform(49500, 50500, 20),
            'volume': np.random.uniform(100, 200, 20),
            'ema_7': [np.nan] * 20,  # All NaN - issue
            'rsi_6': [150.0] * 20,   # Out of range - issue
            'volume_ma_20': np.random.uniform(120, 180, 20)
        }, index=timestamps)
        
        df.index.name = 'open_time'
        in_memory_db.save_data(df, 'btc_15m')
        
        results = validator.validate_all('btc_15m', limit=20)
        
        # Should fail validation
        assert results['valid'] is False
        assert len(results['issues']) > 0
    
    def test_generate_report(self, validator, in_memory_db, valid_data):
        """Test report generation."""
        in_memory_db.save_data(valid_data, 'btc_15m')
        
        results = validator.validate_all('btc_15m', limit=50)
        report = validator.generate_report(results)
        
        assert isinstance(report, str)
        assert 'DATA VALIDATION REPORT' in report
        assert 'btc_15m' in report
        assert 'Overall Status' in report
        
        # Should show passed status
        if results['valid']:
            assert '✅ PASSED' in report
        else:
            assert '❌ FAILED' in report
    
    def test_generate_report_with_issues(self, validator, in_memory_db):
        """Test report generation with issues."""
        timestamps = pd.date_range(start='2024-01-01', periods=20, freq='15min')
        
        df = pd.DataFrame({
            'open': np.random.uniform(49000, 51000, 20),
            'high': np.random.uniform(50000, 52000, 20),
            'low': np.random.uniform(48000, 50000, 20),
            'close': np.random.uniform(49500, 50500, 20),
            'volume': np.random.uniform(100, 200, 20),
            'ema_7': np.random.uniform(49500, 50500, 20),
            'rsi_6': [150.0] * 20,  # Out of range
            'volume_ma_20': np.random.uniform(120, 180, 20)
        }, index=timestamps)
        
        df.index.name = 'open_time'
        in_memory_db.save_data(df, 'btc_15m')
        
        results = validator.validate_all('btc_15m', limit=20)
        report = validator.generate_report(results)
        
        assert '❌ FAILED' in report
        assert '🔴 ISSUES FOUND' in report
        assert 'RSI' in report
    
    def test_repr(self, validator, in_memory_db):
        """Test string representation."""
        repr_str = repr(validator)
        
        assert 'DataValidator' in repr_str
        assert in_memory_db.db_path in repr_str
    
    def test_validate_different_tables(self, validator, in_memory_db, valid_data):
        """Test validation on different tables."""
        # Save 15m data to btc_15m table
        in_memory_db.save_data(valid_data, 'btc_15m')
        
        # Create 1h data for btc_1h table
        timestamps_1h = pd.date_range(start='2024-01-01', periods=24, freq='1h')
        data_1h = pd.DataFrame({
            'open': np.random.uniform(49000, 51000, 24),
            'high': np.random.uniform(50000, 52000, 24),
            'low': np.random.uniform(48000, 50000, 24),
            'close': np.random.uniform(49500, 50500, 24),
            'volume': np.random.uniform(100, 200, 24),
            'ema_7': np.random.uniform(49500, 50500, 24),
            'rsi_6': np.random.uniform(30, 70, 24),
            'volume_ma_20': np.random.uniform(120, 180, 24)
        }, index=timestamps_1h)
        data_1h.index.name = 'open_time'
        
        in_memory_db.save_data(data_1h, 'btc_1h')
        
        # Validate both
        results_15m = validator.validate_all('btc_15m')
        results_1h = validator.validate_all('btc_1h')
        
        assert results_15m['table_name'] == 'btc_15m'
        assert results_1h['table_name'] == 'btc_1h'
        
        # Both should be valid
        assert results_15m['valid'] is True
        assert results_1h['valid'] is True
    
    def test_check_time_continuity_1h_table(self, validator, in_memory_db):
        """Test time continuity check for 1h table."""
        timestamps = pd.date_range(start='2024-01-01', periods=24, freq='1h')
        
        df = pd.DataFrame({
            'open': np.random.uniform(49000, 51000, 24),
            'high': np.random.uniform(50000, 52000, 24),
            'low': np.random.uniform(48000, 50000, 24),
            'close': np.random.uniform(49500, 50500, 24),
            'volume': np.random.uniform(100, 200, 24),
            'ema_7': np.random.uniform(49500, 50500, 24),
            'rsi_6': np.random.uniform(30, 70, 24),
            'volume_ma_20': np.random.uniform(120, 180, 24)
        }, index=timestamps)
        
        df.index.name = 'open_time'
        in_memory_db.save_data(df, 'btc_1h')
        
        result = validator.check_time_continuity('btc_1h', limit=24)
        
        # Should detect 1h intervals correctly
        assert result['details']['expected_interval'] == '1:00:00'
        assert result['has_issues'] is False
