import asyncio
import sys
import os
import logging
import pandas as pd

# Add project root to python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.application.services.realtime_service import RealtimeService

# Configure logging
logging.basicConfig(level=logging.INFO)

async def main():
    print("Initializing Service...")
    service = RealtimeService(symbol='btcusdt', interval='1m')
    
    print("Loading historical data...")
    await service._load_historical_data()
    
    print("Checking 1h candles...")
    candles_1h = service.get_candles('1h')
    print(f"1h Candles count: {len(candles_1h)}")
    
    if candles_1h:
        print(f"Latest 1h candle: {candles_1h[-1]}")
    
    print("Calculating 1h indicators...")
    indicators = service.get_latest_indicators('1h')
    
    print(f"Indicators keys: {indicators.keys()}")
    
    if 'stoch_rsi' in indicators:
        print(f"StochRSI: {indicators['stoch_rsi']}")
    else:
        print("StochRSI key MISSING")

    await service.stop()

if __name__ == "__main__":
    asyncio.run(main())
