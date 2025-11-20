
import sys
import os
from pathlib import Path
import pandas as pd
import logging

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.backtesting.data_loader import HistoricalDataLoader
from src.application.signals.signal_generator import SignalGenerator
from src.infrastructure.indicators.talib_calculator import TALibCalculator
from src.application.services.entry_price_calculator import EntryPriceCalculator
from src.application.services.tp_calculator import TPCalculator
from src.application.services.stop_loss_calculator import StopLossCalculator
from src.application.services.confidence_calculator import ConfidenceCalculator

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def debug_signal_generation():
    logger.info("Starting debug...")
    
    # 1. Load Data
    data_loader = HistoricalDataLoader()
    # Try to load a small amount of data
    try:
        candles = data_loader.load_candles(
            symbol='BTCUSDT',
            timeframe='15m',
            limit=200 # Load enough for indicators
        )
        logger.info(f"Loaded {len(candles)} candles")
        if not candles:
            logger.error("No candles loaded!")
            return
    except Exception as e:
        logger.error(f"Error loading candles: {e}")
        return

    # 2. Initialize SignalGenerator
    talib_calc = TALibCalculator()
    entry_calc = EntryPriceCalculator()
    tp_calc = TPCalculator()
    sl_calc = StopLossCalculator()
    conf_calc = ConfidenceCalculator()

    signal_generator = SignalGenerator(
        talib_calculator=talib_calc,
        entry_calculator=entry_calc,
        tp_calculator=tp_calc,
        stop_loss_calculator=sl_calc,
        confidence_calculator=conf_calc,
        use_filters=False, # Disable filters to see if we get ANY raw signals
        strict_mode=False
    )

    # 3. Test Signal Generation on the last window
    window_size = 100
    if len(candles) < window_size:
        logger.error("Not enough candles for window")
        return

    logger.info("Testing signal generation on last 10 windows...")
    
    signals_found = 0
    for i in range(len(candles) - 10, len(candles)):
        window = candles[i-window_size:i]
        
        # Manually check indicators first
        df = pd.DataFrame({
            'open': [c.open for c in window],
            'high': [c.high for c in window],
            'low': [c.low for c in window],
            'close': [c.close for c in window],
            'volume': [c.volume for c in window]
        })
        indicators = talib_calc.calculate_all(df)
        latest_ind = indicators.iloc[-1]
        logger.info(f"Candle {i}: Close={window[-1].close}, RSI={latest_ind.get('rsi')}, EMA7={latest_ind.get('ema_7')}, EMA25={latest_ind.get('ema_25')}")

        # Generate Signal
        signal = signal_generator.generate_signal(window)
        if signal:
            logger.info(f"SIGNAL FOUND: {signal}")
            signals_found += 1
        else:
            logger.info("No signal")

    logger.info(f"Total signals found in debug run: {signals_found}")

if __name__ == "__main__":
    debug_signal_generation()
