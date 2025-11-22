import requests
import pandas as pd
from datetime import datetime, timedelta
import os
import time

def fetch_binance_data_extended(symbol="BTCUSDT", interval="15m", days=90):
    """Fetch historical klines from Binance with pagination"""
    url = "https://api.binance.com/api/v3/klines"
    limit = 1000
    
    # Calculate start time (ms)
    end_time = int(time.time() * 1000)
    start_time = int((time.time() - (days * 24 * 3600)) * 1000)
    
    all_data = []
    current_start = start_time
    
    print(f"⬇️ Fetching {days} days of {interval} data for {symbol}...")
    
    while True:
        params = {
            "symbol": symbol,
            "interval": interval,
            "limit": limit,
            "startTime": current_start
        }
        
        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            if not data or not isinstance(data, list):
                break
                
            all_data.extend(data)
            print(f"   Fetched {len(data)} candles... Total: {len(all_data)}")
            
            # Update start time for next batch: Last candle close time + 1ms
            last_close_time = data[-1][6]
            current_start = last_close_time + 1
            
            # Stop if we reached current time or no new data
            if len(data) < limit or current_start > end_time:
                break
                
            # Respect API limits
            time.sleep(0.1)
            
        except Exception as e:
            print(f"❌ Error fetching batch: {e}")
            break
    
    # Convert to DataFrame
    df = pd.DataFrame(all_data, columns=[
        "timestamp", "open", "high", "low", "close", "volume",
        "close_time", "quote_asset_volume", "number_of_trades",
        "taker_buy_base_asset_volume", "taker_buy_quote_asset_volume", "ignore"
    ])
    
    # Convert types
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df["open"] = df["open"].astype(float)
    df["high"] = df["high"].astype(float)
    df["low"] = df["low"].astype(float)
    df["close"] = df["close"].astype(float)
    df["volume"] = df["volume"].astype(float)
    
    # Select relevant columns
    df = df[["timestamp", "open", "high", "low", "close", "volume"]]
    
    # Drop duplicates just in case
    df = df.drop_duplicates(subset=['timestamp'])
    
    return df

if __name__ == "__main__":
    try:
        # Fetch 90 days (3 months)
        df = fetch_binance_data_extended(days=90)
        
        # Save to data folder
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        os.makedirs(data_dir, exist_ok=True)
        filepath = os.path.join(data_dir, 'btc_15m.csv')
        
        df.to_csv(filepath, index=False)
        print(f"✅ Data saved to: {filepath}")
        print(f"📊 Total Candles: {len(df)}")
        print(f"📅 Range: {df['timestamp'].min()} to {df['timestamp'].max()}")
        
    except Exception as e:
        print(f"❌ Error fetching data: {e}")
