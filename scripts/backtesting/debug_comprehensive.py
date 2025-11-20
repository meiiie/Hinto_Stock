"""
Comprehensive debug script to find why no trades are generated.
"""
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import logging

# Add project root to path (same pattern as run_backtest.py)
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.backtesting.data_loader import HistoricalDataLoader
from src.application.signals.signal_generator import SignalGenerator
from src.infrastructure.indicators.talib_calculator import TALibCalculator
from src.application.services.entry_price_calculator import EntryPriceCalculator
from src.application.services.tp_calculator import TPCalculator
from src.application.services.stop_loss_calculator import StopLossCalculator
from src.application.services.confidence_calculator import ConfidenceCalculator

# Setup detailed logging
logging.basicConfig(
    level=logging.DEBUG,  # Changed to DEBUG for more details
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    # Load recent data
    loader = HistoricalDataLoader()
    end = datetime.now()
    start = end - timedelta(days=7)  # Just 7 days for quick test
    
    logger.info(f"Loading data from {start} to {end}")
    candles = loader.load_candles(
        symbol='BTCUSDT',
        timeframe='15m',
        start_date=start,
        end_date=end
    )
    
    logger.info(f"Loaded {len(candles)} candles")
    
    # Initialize SignalGenerator with filters DISABLED first
    talib_calc = TALibCalculator()
    entry_calc = EntryPriceCalculator()
    tp_calc = TPCalculator()
    sl_calc = StopLossCalculator()
    conf_calc = ConfidenceCalculator()
    
    # Try with filters OFF first
    logger.info("\n" + "="*60)
    logger.info("TEST 1: SignalGenerator with use_filters=FALSE")
    logger.info("="*60)
    
    sig_gen_no_filters = SignalGenerator(
        talib_calculator=talib_calc,
        entry_calculator=entry_calc,
        tp_calculator=tp_calc,
        stop_loss_calculator=sl_calc,
        confidence_calculator=conf_calc,
        account_size=10000.0,
        use_filters=False,  # DISABLE ALL FILTERS
        strict_mode=False
    )
    
    signals_found = 0
    buy_signals = 0
    sell_signals = 0
    neutral_signals = 0
    
    # Test on last 20 windows
    window_size = 100
    for i in range(max(window_size, len(candles) - 20), len(candles)):
        window = candles[max(0, i-window_size):i+1]
        
        signal = sig_gen_no_filters.generate_signal(window)
        
        if signal:
            signals_found += 1
            if signal.signal_type.value.upper() == 'BUY':
                buy_signals += 1
                logger.info(f"✅ BUY Signal found at index {i}: Confidence={signal.confidence:.0%}, Entry={signal.entry_price}, SL={signal.stop_loss}, TP={signal.tp_levels}")
            elif signal.signal_type.value.upper() == 'SELL':
                sell_signals += 1
                logger.info(f"✅ SELL Signal found at index {i}: Confidence={signal.confidence:.0%}, Entry={signal.entry_price}, SL={signal.stop_loss}, TP={signal.tp_levels}")
            else:
                neutral_signals += 1
    
    logger.info(f"\nRESULTS (No Filters):")
    logger.info(f"  Total signals: {signals_found}")
    logger.info(f"  BUY signals: {buy_signals}")
    logger.info(f"  SELL signals: {sell_signals}")
    logger.info(f"  NEUTRAL signals: {neutral_signals}")
    
    # Try with filters ON
    logger.info("\n" + "="*60)
    logger.info("TEST 2: SignalGenerator with use_filters=TRUE")
    logger.info("="*60)
    
    sig_gen_with_filters = SignalGenerator(
        talib_calculator=talib_calc,
        entry_calculator=entry_calc,
        tp_calculator=tp_calc,
        stop_loss_calculator=sl_calc,
        confidence_calculator=conf_calc,
        account_size=10000.0,
        use_filters=True,  # ENABLE FILTERS
        strict_mode=False
    )
    
    signals_found_filtered = 0
    buy_signals_filtered = 0
    sell_signals_filtered = 0
    neutral_signals_filtered = 0
    
    for i in range(max(window_size, len(candles) - 20), len(candles)):
        window = candles[max(0, i-window_size):i+1]
        
        signal = sig_gen_with_filters.generate_signal(window)
        
        if signal:
            signals_found_filtered += 1
            if signal.signal_type.value.upper() == 'BUY':
                buy_signals_filtered += 1
                logger.info(f"✅ BUY Signal found at index {i}: Confidence={signal.confidence:.0%}")
            elif signal.signal_type.value.upper() == 'SELL':
                sell_signals_filtered += 1
                logger.info(f"✅ SELL Signal found at index {i}: Confidence={signal.confidence:.0%}")
            else:
                neutral_signals_filtered += 1
    
    logger.info(f"\nRESULTS (With Filters):")
    logger.info(f"  Total signals: {signals_found_filtered}")
    logger.info(f"  BUY signals: {buy_signals_filtered}")
    logger.info(f"  SELL signals: {sell_signals_filtered}")
    logger.info(f"  NEUTRAL signals: {neutral_signals_filtered}")
    
    logger.info("\n" + "="*60)
    logger.info("DIAGNOSIS:")
    logger.info("="*60)
    if buy_signals == 0 and sell_signals == 0:
        logger.error("❌ NO BUY/SELL signals even with filters OFF!")
        logger.error("   → Problem is in _check_buy_conditions/_check_sell_conditions")
        logger.error("   → Conditions are too strict or data doesn't meet criteria")
    elif buy_signals_filtered == 0 and sell_signals_filtered == 0 and (buy_signals > 0 or sell_signals > 0):
        logger.error("❌ Signals exist but filters are blocking them!")
        logger.error("   → Check trend filter (EMA50) or other enabled filters")
    else:
        logger.info("✅ Signals are being generated correctly")

if __name__ == "__main__":
    main()
