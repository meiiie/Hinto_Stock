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
    with open("verify_result.txt", "w", encoding="utf-8") as f:
        f.write("Initializing Service...\n")
        service = RealtimeService(symbol='btcusdt', interval='1m')
        
        f.write("Loading historical data...\n")
        await service._load_historical_data()
        
        f.write("Checking 1h candles...\n")
        candles_1h = service.get_candles('1h')
        f.write(f"1h Candles count: {len(candles_1h)}\n")
        
        if not candles_1h:
            f.write("No 1h candles found!\n")
            return

        f.write("Running StochRSICalculator...\n")
        calculator = StochRSICalculator()
        result = calculator.calculate_stoch_rsi(candles_1h)
        
        if result:
            f.write(f"StochRSI Result: K={result.k_value}, D={result.d_value}\n")
            
            # Verify UI Logic
            if result.k_value < 0.1:
                f.write("✅ UI Check: Condition (K < 0.1) met -> Status: 'EXTREME OVERSOLD'\n")
            else:
                f.write(f"ℹ️ UI Check: Condition (K < 0.1) NOT met. K is {result.k_value}\n")
                
        else:
            f.write("FAILURE! StochRSI returned None\n")

        await service.stop()

if __name__ == "__main__":
    asyncio.run(main())
