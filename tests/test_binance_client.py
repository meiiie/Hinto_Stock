"""
Unit tests for Binance API client.

Tests API interactions, error handling, and data conversion using mocked responses.
"""

import pytest
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
from src.binance_client import BinanceClient
from src.config import Config


@pytest.fixture
def mock_config():
    """Fixture providing a mock Config object."""
    config = Mock(spec=Config)
    config.api_key = "test_api_key"
    config.api_secret = "test_api_secret"
    config.base_url = "https://api.binance.com/api/v3"
    return config


@pytest.fixture
def client(mock_config):
    """Fixture providing a BinanceClient instance with mock config."""
    return BinanceClient(mock_config)


@pytest.fixture
def sample_klines_response():
    """Fixture providing sample klines API response."""
    return [
        [
            1699999999000,  # open_time
            "50000.00",     # open
            "51000.00",     # high
            "49500.00",     # low
            "50500.00",     # close
            "100.5",        # volume
            1700003599999,  # close_time
            "5050000.00",   # quote_asset_volume
            1000,           # num_trades
            "50.25",        # taker_buy_base
            "2525000.00",   # taker_buy_quote
            "0"             # ignore
        ],
        [
            1700003600000,
            "50500.00",
            "52000.00",
            "50000.00",
            "51500.00",
            "150.75",
            1700007199999,
            "7762500.00",
            1500,
            "75.5",
            "3887500.00",
            "0"
        ]
    ]


class TestBinanceClient:
    """Test suite for BinanceClient class."""
    
    def test_initialization(self, mock_config):
        """Test client initialization with config."""
        client = BinanceClient(mock_config)
        
        assert client.config == mock_config
        assert client.session is not None
        assert client.session.headers["X-MBX-APIKEY"] == "test_api_key"
    
    def test_get_klines_successful_request(self, client, sample_klines_response):
        """Test successful klines request and DataFrame conversion."""
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_klines_response
        
        with patch.object(client.session, 'get', return_value=mock_response):
            df = client.get_klines("BTCUSDT", "15m", 2)
        
        # Verify DataFrame structure
        assert df is not None
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2
        assert list(df.columns) == ['open_time', 'open', 'high', 'low', 'close', 'volume']
        
        # Verify data types
        assert df['open'].dtype == float
        assert df['high'].dtype == float
        assert df['low'].dtype == float
        assert df['close'].dtype == float
        assert df['volume'].dtype == float
        
        # Verify values
        assert df.iloc[0]['close'] == 50500.00
        assert df.iloc[1]['close'] == 51500.00
        assert df.iloc[0]['volume'] == 100.5
    
    def test_get_klines_default_parameters(self, client, sample_klines_response):
        """Test get_klines with default parameters."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_klines_response
        
        with patch.object(client.session, 'get', return_value=mock_response) as mock_get:
            df = client.get_klines()
            
            # Verify default parameters were used
            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert call_args[1]['params']['symbol'] == "BTCUSDT"
            assert call_args[1]['params']['interval'] == "15m"
            assert call_args[1]['params']['limit'] == 100
    
    def test_get_klines_custom_parameters(self, client, sample_klines_response):
        """Test get_klines with custom parameters."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_klines_response
        
        with patch.object(client.session, 'get', return_value=mock_response) as mock_get:
            df = client.get_klines("ETHUSDT", "1h", 50)
            
            # Verify custom parameters were used
            call_args = mock_get.call_args
            assert call_args[1]['params']['symbol'] == "ETHUSDT"
            assert call_args[1]['params']['interval'] == "1h"
            assert call_args[1]['params']['limit'] == 50
    
    def test_get_klines_error_403_forbidden(self, client, capsys):
        """Test handling of 403 Forbidden error."""
        mock_response = Mock()
        mock_response.status_code = 403
        
        with patch.object(client.session, 'get', return_value=mock_response):
            df = client.get_klines()
        
        assert df is None
        
        # Check error message
        captured = capsys.readouterr()
        assert "403" in captured.out
        assert "Forbidden" in captured.out
        assert "IP whitelist" in captured.out
    
    def test_get_klines_error_429_rate_limit(self, client, capsys):
        """Test handling of 429 Rate Limit error."""
        mock_response = Mock()
        mock_response.status_code = 429
        
        with patch.object(client.session, 'get', return_value=mock_response):
            df = client.get_klines()
        
        assert df is None
        
        # Check error message
        captured = capsys.readouterr()
        assert "429" in captured.out
        assert "Rate limit" in captured.out
    
    def test_get_klines_error_500_server_error(self, client, capsys):
        """Test handling of 500 Server Error."""
        mock_response = Mock()
        mock_response.status_code = 500
        
        with patch.object(client.session, 'get', return_value=mock_response):
            df = client.get_klines()
        
        assert df is None
        
        # Check error message
        captured = capsys.readouterr()
        assert "500" in captured.out
        assert "server error" in captured.out
    
    def test_get_klines_timeout_error(self, client, capsys):
        """Test handling of timeout error."""
        import requests
        
        with patch.object(client.session, 'get', side_effect=requests.exceptions.Timeout):
            df = client.get_klines()
        
        assert df is None
        
        # Check error message
        captured = capsys.readouterr()
        assert "timeout" in captured.out.lower()
    
    def test_get_klines_connection_error(self, client, capsys):
        """Test handling of connection error."""
        import requests
        
        with patch.object(client.session, 'get', side_effect=requests.exceptions.ConnectionError):
            df = client.get_klines()
        
        assert df is None
        
        # Check error message
        captured = capsys.readouterr()
        assert "Connection failed" in captured.out
    
    def test_get_klines_invalid_json_response(self, client, capsys):
        """Test handling of invalid JSON response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        
        with patch.object(client.session, 'get', return_value=mock_response):
            df = client.get_klines()
        
        assert df is None
        
        # Check error message
        captured = capsys.readouterr()
        assert "parsing" in captured.out.lower()
    
    def test_get_klines_malformed_data(self, client, capsys):
        """Test handling of malformed API data."""
        # Missing required columns
        malformed_data = [
            [1699999999000, "50000.00"]  # Only 2 columns instead of 12
        ]
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = malformed_data
        
        with patch.object(client.session, 'get', return_value=mock_response):
            df = client.get_klines()
        
        # Should handle gracefully
        assert df is None
    
    def test_repr(self, client):
        """Test string representation of client."""
        repr_str = repr(client)
        
        assert "BinanceClient" in repr_str
        assert "base_url" in repr_str
        assert "authenticated" in repr_str
        assert "https://api.binance.com/api/v3" in repr_str
    
    def test_session_reuse(self, client, sample_klines_response):
        """Test that session is reused across multiple requests."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_klines_response
        
        with patch.object(client.session, 'get', return_value=mock_response) as mock_get:
            # Make multiple requests
            client.get_klines()
            client.get_klines()
            client.get_klines()
            
            # Verify session.get was called 3 times (session reused)
            assert mock_get.call_count == 3
    
    def test_type_conversion_accuracy(self, client):
        """Test that numeric type conversion is accurate."""
        test_data = [
            [
                1699999999000,
                "12345.67890",  # High precision
                "12346.12345",
                "12344.54321",
                "12345.99999",
                "0.00001",      # Very small volume
                1700003599999,
                "123.45",
                100,
                "0.000005",
                "61.725",
                "0"
            ]
        ]
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = test_data
        
        with patch.object(client.session, 'get', return_value=mock_response):
            df = client.get_klines()
        
        # Verify precision is maintained
        assert df.iloc[0]['open'] == 12345.67890
        assert df.iloc[0]['close'] == 12345.99999
        assert df.iloc[0]['volume'] == 0.00001


# Integration-style test (can be skipped if no internet)
@pytest.mark.skip(reason="Requires internet connection and valid API key")
def test_real_api_call():
    """
    Integration test with real Binance API.
    
    This test is skipped by default. Remove @pytest.mark.skip to run.
    Requires valid API credentials in .env file.
    """
    from src.config import Config
    
    config = Config()
    config.validate()
    
    client = BinanceClient(config)
    df = client.get_klines("BTCUSDT", "15m", 5)
    
    assert df is not None
    assert len(df) == 5
    assert all(col in df.columns for col in ['open_time', 'open', 'high', 'low', 'close', 'volume'])
