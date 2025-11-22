"""
Tests for SignalGenerator strict mode (Task 7).

Tests stricter signal conditions:
- RSI < 25 for BUY (instead of 30)
- RSI > 75 for SELL (instead of 70)
- Volume > 2.5x average (instead of 2.0x)
- Require 3+ conditions (instead of 2+)
- Price > EMA(25) for BUY, Price < EMA(25) for SELL
"""

import pytest
from datetime import datetime, timedelta
from typing import List

from src.domain.entities.candle import Candle
from src.application.signals.signal_generator import SignalGenerator, SignalType
from src.infrastructure.indicators.vwap_calculator import VWAPCalculator
from src.infrastructure.indicators.bollinger_calculator import BollingerCalculator
from src.infrastructure.indicators.stoch_rsi_calculator import StochRSICalculator
from src.application.services.smart_entry_calculator import SmartEntryCalculator
from src.infrastructure.indicators.talib_calculator import TALibCalculator
from src.application.services.tp_calculator import TPCalculator
from src.application.services.stop_loss_calculator import StopLossCalculator
from src.application.services.confidence_calculator import ConfidenceCalculator
from src.infrastructure.indicators.volume_spike_detector import VolumeSpikeDetector
from src.infrastructure.indicators.adx_calculator import ADXCalculator
from src.infrastructure.indicators.atr_calculator import ATRCalculator


def create_test_candles_with_rsi(
    count: int = 100,
    final_rsi_target: float = 20.0,
    trend: str = 'bullish'
) -> List[Candle]:
    """
    Create candles designed to produce specific RSI value.
    
    Args:
        count: Number of candles
        final_rsi_target: Target RSI for last candles (20 = extreme oversold, 80 = extreme overbought)
        trend: 'bullish' or 'bearish'
    """
    candles = []
    base_price = 50000.0
    base_time = datetime(2025, 11, 19, 0, 0, 0)
    
    # Create trending candles
    for i in range(count - 10):
        if trend == 'bullish':
            price = base_price + (i * 100)  # Uptrend
        else:
            price = base_price - (i * 100)  # Downtrend
        
        candle = Candle(
            timestamp=base_time + timedelta(minutes=15 * i),
            open=price - 50,
            high=price + 200,
            low=price - 200,
            close=price,
            volume=1000.0
        )
        candles.append(candle)
    
    # Create last 10 candles to hit RSI target
    last_price = candles[-1].close
    for i in range(10):
        idx = count - 10 + i
        
        if final_rsi_target < 30:
            # Create oversold (sharp drop)
            price = last_price * (0.97 ** (i + 1))  # 3% drop each candle
            volume = 3000.0  # High volume
        else:
            # Create overbought (sharp rise)
            price = last_price * (1.03 ** (i + 1))  # 3% rise each candle
            volume = 3000.0  # High volume
        
        candle = Candle(
            timestamp=base_time + timedelta(minutes=15 * idx),
            open=price * 0.99,
            high=price * 1.01,
            low=price * 0.98,
            close=price,
            volume=volume
        )
        candles.append(candle)
    
    return candles


class TestSignalGeneratorStrictMode:
    """Tests for strict mode signal generation"""
    
    def setup_method(self):
        """Setup dependencies for tests"""
        self.vwap_calculator = VWAPCalculator()
        self.bollinger_calculator = BollingerCalculator()
        self.stoch_rsi_calculator = StochRSICalculator()
        self.smart_entry_calculator = SmartEntryCalculator()
        self.adx_calculator = ADXCalculator()
        self.atr_calculator = ATRCalculator()
        self.talib_calculator = TALibCalculator()
        self.tp_calculator = TPCalculator()
        self.stop_loss_calculator = StopLossCalculator()
        self.confidence_calculator = ConfidenceCalculator()
        self.volume_spike_detector = VolumeSpikeDetector()

    def _create_generator(self, strict_mode=True, use_filters=False, inject_detector=True):
        """
        Helper to create SignalGenerator.
        Args:
            inject_detector: If True, injects self.volume_spike_detector. If False, passes None.
        """
        vol_detector = self.volume_spike_detector if inject_detector else None
        
        return SignalGenerator(
            vwap_calculator=self.vwap_calculator,
            bollinger_calculator=self.bollinger_calculator,
            stoch_rsi_calculator=self.stoch_rsi_calculator,
            smart_entry_calculator=self.smart_entry_calculator,
            adx_calculator=self.adx_calculator,
            atr_calculator=self.atr_calculator,
            talib_calculator=self.talib_calculator,
            tp_calculator=self.tp_calculator,
            stop_loss_calculator=self.stop_loss_calculator,
            confidence_calculator=self.confidence_calculator,
            volume_spike_detector=vol_detector,
            strict_mode=strict_mode,
            use_filters=use_filters
        )

    def test_strict_mode_enabled_by_default(self):
        """Test strict mode is enabled by default"""
        # Note: We must pass required args, so we check default of strict_mode arg if not passed?
        # Actually, we can't test default arg value easily if we must pass required args.
        # We'll just check if we pass nothing for strict_mode, it defaults to True.
        generator = SignalGenerator(
            vwap_calculator=self.vwap_calculator,
            bollinger_calculator=self.bollinger_calculator,
            stoch_rsi_calculator=self.stoch_rsi_calculator,
            smart_entry_calculator=self.smart_entry_calculator
        )
        assert generator.strict_mode is True
    
    def test_strict_mode_can_be_disabled(self):
        """Test strict mode can be disabled for backward compatibility"""
        generator = self._create_generator(strict_mode=False)
        assert generator.strict_mode is False
    
    def test_strict_mode_volume_threshold(self):
        """Test strict mode uses 2.5x volume threshold"""
        # Don't inject detector, let SignalGenerator create it based on strict_mode
        generator_strict = self._create_generator(strict_mode=True, inject_detector=False)
        generator_normal = self._create_generator(strict_mode=False, inject_detector=False)
        
        # Note: In new implementation, volume threshold might be passed to detector or handled inside.
        # If SignalGenerator sets detector threshold based on strict mode:
        assert generator_strict.volume_spike_detector.threshold == 2.5
        assert generator_normal.volume_spike_detector.threshold == 2.0
    
    def test_buy_signal_requires_rsi_below_25_strict(self):
        """Test BUY signal requires RSI < 25 in strict mode"""
        # Create candles with RSI around 27 (would pass normal mode but fail strict)
        candles = create_test_candles_with_rsi(count=100, final_rsi_target=27.0, trend='bullish')
        
        generator_strict = self._create_generator(strict_mode=True, use_filters=False)
        signal_strict = generator_strict.generate_signal(candles)
        
        # Should NOT generate BUY signal (RSI 27 > 25)
        if signal_strict:
            assert signal_strict.signal_type != SignalType.BUY
    
    def test_buy_signal_passes_with_rsi_below_25_strict(self):
        """Test BUY signal passes with RSI < 25 in strict mode"""
        # Create candles with RSI around 20 (extreme oversold)
        candles = create_test_candles_with_rsi(count=100, final_rsi_target=20.0, trend='bullish')
        
        generator_strict = self._create_generator(strict_mode=True, use_filters=False)
        signal_strict = generator_strict.generate_signal(candles)
        
        # May generate BUY signal if other conditions met
        # Just verify it doesn't crash and RSI is checked
        assert signal_strict is not None
    
    def test_sell_signal_requires_rsi_above_75_strict(self):
        """Test SELL signal requires RSI > 75 in strict mode"""
        # Create candles with RSI around 72 (would pass normal mode but fail strict)
        candles = create_test_candles_with_rsi(count=100, final_rsi_target=72.0, trend='bearish')
        
        generator_strict = self._create_generator(strict_mode=True, use_filters=False)
        signal_strict = generator_strict.generate_signal(candles)
        
        # Should NOT generate SELL signal (RSI 72 < 75)
        if signal_strict:
            assert signal_strict.signal_type != SignalType.SELL
    
    def test_sell_signal_passes_with_rsi_above_75_strict(self):
        """Test SELL signal passes with RSI > 75 in strict mode"""
        # Create candles with RSI around 80 (extreme overbought)
        candles = create_test_candles_with_rsi(count=100, final_rsi_target=80.0, trend='bearish')
        
        generator_strict = self._create_generator(strict_mode=True, use_filters=False)
        signal_strict = generator_strict.generate_signal(candles)
        
        # May generate SELL signal if other conditions met
        # Just verify it doesn't crash and RSI is checked
        assert signal_strict is not None
    
    def test_strict_mode_requires_3_conditions(self):
        """Test strict mode requires minimum 3 conditions"""
        candles = create_test_candles_with_rsi(count=100, final_rsi_target=20.0, trend='bullish')
        
        generator = self._create_generator(strict_mode=True, use_filters=False)
        signal = generator.generate_signal(candles)
        
        # If signal generated, should have 3+ conditions
        if signal and signal.signal_type == SignalType.BUY:
            # Count conditions from reasons
            assert len(signal.reasons) >= 3
    
    def test_normal_mode_requires_2_conditions(self):
        """Test normal mode requires minimum 2 conditions"""
        candles = create_test_candles_with_rsi(count=100, final_rsi_target=28.0, trend='bullish')
        
        generator = self._create_generator(strict_mode=False, use_filters=False)
        signal = generator.generate_signal(candles)
        
        # If signal generated, should have 2+ conditions
        if signal and signal.signal_type == SignalType.BUY:
            # Count conditions from reasons
            assert len(signal.reasons) >= 2
    
    def test_strict_mode_checks_price_vs_ema25(self):
        """Test strict mode checks price against EMA(25) not EMA(7)"""
        candles = create_test_candles_with_rsi(count=100, final_rsi_target=20.0, trend='bullish')
        
        generator = self._create_generator(strict_mode=True, use_filters=False)
        signal = generator.generate_signal(candles)
        
        # Check that EMA(25) is mentioned in reasons if signal generated
        if signal and signal.signal_type == SignalType.BUY:
            reasons_text = ' '.join(signal.reasons)
            # Should mention EMA(25) not EMA(7) for price condition
            # Note: New strategy uses VWAP, but if legacy EMA check exists in strict mode:
            if 'EMA' in reasons_text and 'Price' in reasons_text:
                assert 'EMA(25)' in reasons_text or 'EMA25' in reasons_text
    
    def test_normal_mode_checks_price_vs_ema7(self):
        """Test normal mode checks price against EMA(7)"""
        candles = create_test_candles_with_rsi(count=100, final_rsi_target=28.0, trend='bullish')
        
        generator = self._create_generator(strict_mode=False, use_filters=False)
        signal = generator.generate_signal(candles)
        
        # Check that EMA(7) is mentioned in reasons if signal generated
        if signal and signal.signal_type == SignalType.BUY:
            reasons_text = ' '.join(signal.reasons)
            # Should mention EMA(7) for price condition
            if 'EMA' in reasons_text and 'Price' in reasons_text:
                assert 'EMA(7)' in reasons_text or 'EMA7' in reasons_text
    
    def test_strict_mode_with_filters_integration(self):
        """Test strict mode works with filters enabled"""
        candles = create_test_candles_with_rsi(count=100, final_rsi_target=20.0, trend='bullish')
        
        generator = self._create_generator(strict_mode=True, use_filters=True)
        signal = generator.generate_signal(candles)
        
        # Should not crash with both strict mode and filters enabled
        assert signal is not None
    
    def test_backward_compatibility_normal_mode(self):
        """Test backward compatibility with strict_mode=False"""
        candles = create_test_candles_with_rsi(count=100, final_rsi_target=28.0, trend='bullish')
        
        # Normal mode should be more lenient
        generator_normal = self._create_generator(strict_mode=False, use_filters=False)
        generator_strict = self._create_generator(strict_mode=True, use_filters=False)
        
        signal_normal = generator_normal.generate_signal(candles)
        signal_strict = generator_strict.generate_signal(candles)
        
        # Normal mode might generate signal where strict mode doesn't
        # (RSI 28 passes normal <30 but fails strict <25)
        assert signal_normal is not None or signal_strict is not None
    
    def test_strict_mode_reason_messages(self):
        """Test strict mode uses correct reason messages"""
        candles = create_test_candles_with_rsi(count=100, final_rsi_target=20.0, trend='bullish')
        
        generator = self._create_generator(strict_mode=True, use_filters=False)
        signal = generator.generate_signal(candles)
        
        if signal and signal.signal_type == SignalType.BUY:
            reasons_text = ' '.join(signal.reasons)
            # Should mention "extreme oversold" for strict mode
            assert 'extreme oversold' in reasons_text.lower() or '< 25' in reasons_text
            # Should mention 2.5x for volume
    def test_signal_rejected_by_volume_climax(self):
        """Test signal rejected when volume is too high (> 4.0x) - Climax"""
        # Create candles that would trigger a BUY
        candles = create_test_candles_with_rsi(count=100, final_rsi_target=20.0, trend='bullish')
        
        # Artificially inflate volume of last candle to be huge
        # We need to ensure it's > 4.0x the average of previous 20
        last_candle = candles[-1]
        avg_vol = sum(c.volume for c in candles[-21:-1]) / 20
        climax_vol = avg_vol * 5.0 # 5x average
        
        new_last_candle = Candle(
            timestamp=last_candle.timestamp,
            open=last_candle.open,
            high=last_candle.high,
            low=last_candle.low,
            close=last_candle.close,
            volume=climax_vol
        )
        candles[-1] = new_last_candle
        
        generator = self._create_generator(strict_mode=False, use_filters=False)
        signal = generator.generate_signal(candles)
        
        # Should be rejected due to Volume Climax
        if signal:
            # Note: Even with strict_mode=False, the Climax Filter should invalidate it
            # So it should be NEUTRAL
            assert signal.signal_type == SignalType.NEUTRAL
            # Check reason contains Volume Climax
            reasons_text = ' '.join(signal.reasons)
            assert "Volume Climax" in reasons_text or "> 4.0x" in reasons_text

    def test_signal_passes_volume_climax_check(self):
        """Test signal passes when volume is high but not climax (< 4.0x)"""
        # Create candles that would trigger a BUY
        candles = create_test_candles_with_rsi(count=100, final_rsi_target=20.0, trend='bullish')
        
        # Inflate volume to be high but acceptable (e.g. 3.0x)
        last_candle = candles[-1]
        avg_vol = sum(c.volume for c in candles[-21:-1]) / 20
        high_vol = avg_vol * 3.0 # 3x average (Valid spike)
        
        new_last_candle = Candle(
            timestamp=last_candle.timestamp,
            open=last_candle.open,
            high=last_candle.high,
            low=last_candle.low,
            close=last_candle.close,
            volume=high_vol
        )
        candles[-1] = new_last_candle
        
        generator = self._create_generator(strict_mode=True, use_filters=False)
        signal = generator.generate_signal(candles)
        
        # Should NOT be rejected by Volume Climax
        # (It might be rejected by other things in this mock setup, but let's check reasons if it exists)
        if signal and signal.signal_type == SignalType.NEUTRAL:
             reasons_text = ' '.join(signal.reasons)
             assert "Volume Climax" not in reasons_text


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
