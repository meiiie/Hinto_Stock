"""
Binance API client for fetching cryptocurrency market data.

Handles all interactions with Binance REST API including authentication,
error handling, and data conversion.
"""

import requests
import pandas as pd
from typing import Optional
from src.config import Config


class BinanceClient:
    """
    Client for interacting with Binance API.
    
    Provides methods to fetch klines (candlestick) data with proper
    error handling and data conversion to pandas DataFrame.
    
    Attributes:
        config (Config): Configuration object with API credentials
        session (requests.Session): Reusable HTTP session with auth headers
    """
    
    def __init__(self, config: Config):
        """
        Initialize Binance API client.
        
        Args:
            config (Config): Configuration object containing API credentials
        """
        self.config = config
        self.session = requests.Session()
        
        # Set authentication header
        self.session.headers.update({
            "X-MBX-APIKEY": config.api_key
        })
    
    def get_klines(
        self,
        symbol: str = "BTCUSDT",
        interval: str = "15m",
        limit: int = 100
    ) -> Optional[pd.DataFrame]:
        """
        Fetch klines (candlestick) data from Binance API.
        
        Args:
            symbol (str): Trading pair symbol (default: "BTCUSDT")
            interval (str): Timeframe interval (default: "15m")
                Valid intervals: 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M
            limit (int): Number of klines to fetch (default: 100, max: 1000)
        
        Returns:
            pd.DataFrame: DataFrame with columns [open_time, open, high, low, close, volume]
                         Returns None if an error occurs
        
        Example:
            >>> client = BinanceClient(config)
            >>> df = client.get_klines("BTCUSDT", "15m", 100)
            >>> print(df.head())
        """
        url = f"{self.config.base_url}/klines"
        
        params = {
            "symbol": symbol,
            "interval": interval,
            "limit": limit
        }
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            
            # Handle specific HTTP errors
            if response.status_code == 403:
                print(f"❌ Error 403: Forbidden - Check IP whitelist in Binance API settings")
                print(f"   Your IP may not be whitelisted for API access")
                return None
            
            if response.status_code == 429:
                print(f"❌ Error 429: Rate limit exceeded")
                print(f"   Binance rate limit: 1200 requests/minute")
                print(f"   Please wait before retrying")
                return None
            
            if response.status_code == 500:
                print(f"❌ Error 500: Binance server error")
                print(f"   This is a temporary issue on Binance's side")
                return None
            
            # Raise exception for other HTTP errors
            response.raise_for_status()
            
            # Parse JSON response
            data = response.json()
            
            # Convert to DataFrame
            df = pd.DataFrame(data, columns=[
                'open_time', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_asset_volume', 'num_trades',
                'taker_buy_base', 'taker_buy_quote', 'ignore'
            ])
            
            # Convert numeric columns to float
            df['open'] = df['open'].astype(float)
            df['high'] = df['high'].astype(float)
            df['low'] = df['low'].astype(float)
            df['close'] = df['close'].astype(float)
            df['volume'] = df['volume'].astype(float)
            
            # Return only relevant columns
            return df[['open_time', 'open', 'high', 'low', 'close', 'volume']]
            
        except requests.exceptions.Timeout:
            print(f"❌ Error: Request timeout after 10 seconds")
            print(f"   Check your internet connection")
            return None
        
        except requests.exceptions.ConnectionError:
            print(f"❌ Error: Connection failed")
            print(f"   Check your internet connection or Binance API status")
            return None
        
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching data from Binance API: {e}")
            return None
        
        except (ValueError, KeyError) as e:
            print(f"❌ Error parsing API response: {e}")
            print(f"   The API response format may have changed")
            return None
        
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return None
    
    def __repr__(self) -> str:
        """
        String representation of BinanceClient.
        
        Returns:
            str: Safe string representation
        """
        return (
            f"BinanceClient("
            f"base_url='{self.config.base_url}', "
            f"authenticated={bool(self.config.api_key)}"
            f")"
        )
