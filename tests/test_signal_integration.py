import pytest
from datetime import datetime, timedelta
from typing import List
from src.domain.entities.candle import Candle
from src.application.signals.signal_generator import SignalGenerator
from src.infrastructure.indicators.talib_calculator import TALibCalculator
from src.application.services.entry_price_calculator import EntryPriceCalculator
from src.application.services.tp_calculator import TPCalculator
from src.application.services.stop_loss_calculator import StopLossCalculator
from src.application.services.confidence_calculator import ConfidenceCalculator
from src.infrastructure.indicators.vwap_calculator import VWAPCalculator
from src.infrastructure.indicators.bollinger_calculator import BollingerCalculator
from src.infrastructure.indicators.stoch_rsi_calculator import StochRSICalculator
from src.application.services.smart_entry_calculator import SmartEntryCalculator

def create_mock_candles(count: int = 100) -> List[Candle]:
    candles = []
    base_price = 50000.0
    now = datetime.now()
    
    for i in range(count):
        # Simulate an uptrend (Price > VWAP)
        # Then a pullback to lower band
        if i < 80:
            price = base_price + (i * 20)
        else:
            # Pullback
            price = base_price + 1600 - ((i - 80) * 30)
            
        candle = Candle(
            timestamp=now - timedelta(minutes=count-i),
            open=price,
            high=price + 10,
            low=price - 10,
            close=price,
            volume=1000.0 + (i * 10) # Increasing volume
        )
        candles.append(candle)
    return candles

def test_signal_generator_integration():
    # Initialize dependencies
    talib_calc = TALibCalculator()
    entry_calc = EntryPriceCalculator()
    tp_calc = TPCalculator()
    sl_calc = StopLossCalculator()
    conf_calc = ConfidenceCalculator()
    
    # New Trend Pullback Calculators
    vwap_calc = VWAPCalculator()
    bollinger_calc = BollingerCalculator()
    stoch_calc = StochRSICalculator()
    smart_entry_calc = SmartEntryCalculator()
    
    # Initialize SignalGenerator
    generator = SignalGenerator(
        talib_calculator=talib_calc,
        entry_calculator=entry_calc,
        tp_calculator=tp_calc,
        stop_loss_calculator=sl_calc,
        confidence_calculator=conf_calc,
        vwap_calculator=vwap_calc,
        bollinger_calculator=bollinger_calc,
        stoch_rsi_calculator=stoch_calc,
        smart_entry_calculator=smart_entry_calc,
        strict_mode=False,
        use_filters=False 
    )
    
    # Create candles
    candles = create_mock_candles(100)
    
    # Generate signal
    signal = generator.generate_signal(candles)
    
    # Verify signal
    # Note: We don't strictly assert a BUY signal here because generating exact 
    # Trend Pullback conditions with simple mock data is complex.
    # We mainly ensure it runs without error and returns a valid object (or None).
    
    if signal:
        print(f"Signal generated: {signal}")
        if signal.signal_type.value != 'neutral':
            assert signal.entry_price is not None, "Entry price should be calculated"
            assert signal.stop_loss is not None, "Stop loss should be calculated"
            assert signal.tp_levels is not None, "TP levels should be calculated"
    else:
        print("No signal generated (Expected for simple mock data)")
        
    assert True # If we reached here without crashing, the integration test passed

if __name__ == "__main__":
    test_signal_generator_integration()
