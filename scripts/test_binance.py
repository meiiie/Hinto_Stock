import sys
import os
import logging

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.infrastructure.api.binance_rest_client import BinanceRestClient

logging.basicConfig(level=logging.DEBUG)

def test_binance():
    print("Testing Binance Connection...")
    client = BinanceRestClient()
    try:
        candles = client.get_klines(symbol='BTCUSDT', interval='1m', limit=10)
        print(f"Fetched {len(candles)} candles")
        if candles:
            print(f"First candle: {candles[0]}")
            print("SUCCESS")
        else:
            print("FAILED: No candles returned")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_binance()
