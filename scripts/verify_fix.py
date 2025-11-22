import asyncio
import sys
import os
import logging
import pandas as pd

# Add project root to python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.application.services.realtime_service import RealtimeService
from src.infrastructure.indicators.stoch_rsi_calculator import StochRSICalculator

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
    
    if not candles_1h:
        print("No 1h candles found!")
        return

    print("Running StochRSICalculator...")
    calculator = StochRSICalculator()
    result = calculator.calculate_stoch_rsi(candles_1h)
    
    if result:
        print(f"SUCCESS! StochRSI Result: K={result.k_value}, D={result.d_value}")
    else:
        print("FAILURE! StochRSI returned None")

    await service.stop()

if __name__ == "__main__":
    asyncio.run(main())
