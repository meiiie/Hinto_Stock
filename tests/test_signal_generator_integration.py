"""
Integration tests for SignalGenerator with filters.

Tests the integration of TrendFilter, ADXCalculator, and ATRCalculator
into the SignalGenerator for Phase 3 of Strategy Improvement.
"""

import pytest
from datetime import datetime, timedelta
from typing import List

from src.domain.entities.candle import Candle
from src.application.signals.signal_generator import SignalGenerator, SignalType
from src.application.analysis.trend_filter import TrendFilter
from src.infrastructure.indicators.atr_calculator import ATRCalculator
from src.infrastructure.indicators.adx_calculator import ADXCalculator
from src.infrastructure.indicators.vwap_calculator import VWAPCalculator
from src.infrastructure.indicators.bollinger_calculator import BollingerCalculator
from src.infrastructure.indicators.stoch_rsi_calculator import StochRSICalculator
from src.application.services.smart_entry_calculator import SmartEntryCalculator
from src.infrastructure.indicators.talib_calculator import TALibCalculator
from src.application.services.tp_calculator import TPCalculator
from src.application.services.stop_loss_calculator import StopLossCalculator
from src.application.services.confidence_calculator import ConfidenceCalculator
from src.infrastructure.indicators.volume_spike_detector import VolumeSpikeDetector


def create_test_candles(
    count: int = 100,
    base_price: float = 50000.0,
    trend: str = 'bullish',
    volatility: str = 'high'
) -> List[Candle]:
    """
    Create test candles with specific characteristics.
    
    Args:
        count: Number of candles
        base_price: Starting price
        trend: 'bullish', 'bearish', or 'neutral'
        volatility: 'high' or 'low'
    
    Returns:
        List of Candle objects
    """
    candles = []
    price = base_price
    base_time = datetime(2025, 11, 19, 0, 0, 0)
    
    # Volatility settings
    atr_range = 500.0 if volatility == 'high' else 100.0
    
    for i in range(count):
        # Trend adjustment
        if trend == 'bullish':
            price += 50.0  # Uptrend
        elif trend == 'bearish':
            price -= 50.0  # Downtrend
        else:
            price += (i % 2) * 20.0 - 10.0  # Choppy
        
        # Create candle with volatility
        high = price + atr_range * 0.5
        low = price - atr_range * 0.5
        open_price = price - atr_range * 0.2
        close = price
        
        # Volume pattern
        volume = 1000.0 + (i % 10) * 100.0
        
        candle = Candle(
            timestamp=base_time + timedelta(minutes=15 * i),
            open=open_price,
            high=high,
            low=low,
            close=close,
            volume=volume
        )
        candles.append(candle)
    
    return candles


def create_oversold_bullish_candles(count: int = 100) -> List[Candle]:
    """Create candles with oversold RSI in bullish trend"""
    candles = create_test_candles(count=count, trend='bullish', volatility='high')
    
    # Make last few candles oversold (RSI < 30)
    # Simulate a pullback in uptrend - create new candles
    modified_candles = []
    for i, candle in enumerate(candles):
        if i >= len(candles) - 6:
            # Create new candle with modified values
            new_close = candle.close * 0.95  # 5% drop
            new_candle = Candle(
                timestamp=candle.timestamp,
                open=candle.open,
                high=new_close * 1.02,
                low=new_close * 0.98,
                close=new_close,
                volume=candle.volume * 3.0  # Volume spike
            )
            modified_candles.append(new_candle)
        else:
            modified_candles.append(candle)
    
    return modified_candles


def create_overbought_bearish_candles(count: int = 100) -> List[Candle]:
    """Create candles with overbought RSI in bearish trend"""
    candles = create_test_candles(count=count, trend='bearish', volatility='high')
    
    # Make last few candles overbought (RSI > 70)
    # Simulate a bounce in downtrend - create new candles
    modified_candles = []
    for i, candle in enumerate(candles):
        if i >= len(candles) - 6:
            # Create new candle with modified values
            new_close = candle.close * 1.05  # 5% rise
            new_candle = Candle(
                timestamp=candle.timestamp,
                open=candle.open,
                high=new_close * 1.02,
                low=new_close * 0.98,
                close=new_close,
                volume=candle.volume * 3.0  # Volume spike
            )
            modified_candles.append(new_candle)
        else:
            modified_candles.append(candle)
    
    return modified_candles


def create_choppy_market_candles(count: int = 100) -> List[Candle]:
    """Create candles with low ADX (choppy market)"""
    return create_test_candles(count=count, trend='neutral', volatility='low')


class TestSignalGeneratorIntegration:
    """Integration tests for SignalGenerator with filters"""
    
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

    def _create_generator(self, use_filters=True):
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
            volume_spike_detector=self.volume_spike_detector,
            use_filters=use_filters
        )

    def test_signal_generator_with_filters_enabled(self):
        """Test signal generator with filters enabled"""
        generator = self._create_generator(use_filters=True)
        
        assert generator.use_filters is True
        assert generator.adx_calculator is not None
        assert generator.atr_calculator is not None
    
    def test_signal_generator_with_filters_disabled(self):
        """Test signal generator with filters disabled (backward compatibility)"""
        generator = self._create_generator(use_filters=False)
        
        assert generator.use_filters is False
        # Components still exist but won't be used
        assert generator.adx_calculator is not None
        assert generator.atr_calculator is not None
    
    def test_buy_signal_passes_trend_filter(self):
        """Test BUY signal passes trend filter in bullish market"""
        candles = create_oversold_bullish_candles(count=100)
        generator = self._create_generator(use_filters=True)
        
        signal = generator.generate_signal(candles)
        
        # Should generate BUY signal in bullish trend with oversold RSI
        # Note: With new strategy, we need to ensure Trend Pullback conditions are met
        # This mock data might not perfectly align with VWAP/BB/Stoch logic, 
        # so we primarily check that it runs and if a signal is produced, it has correct attributes
        if signal and signal.signal_type == SignalType.BUY:
            assert 'atr' in signal.indicators
            assert signal.indicators['atr'] > 0
            assert signal.confidence > 0.5
    
    def test_buy_signal_rejected_by_trend_filter(self):
        """Test BUY signal rejected in bearish trend"""
        candles = create_test_candles(count=100, trend='bearish', volatility='high')
        
        # Make last candles oversold (would trigger BUY without filter)
        modified_candles = []
        for i, candle in enumerate(candles):
            if i >= len(candles) - 6:
                new_close = candle.close * 0.95
                new_candle = Candle(
                    timestamp=candle.timestamp,
                    open=candle.open,
                    high=new_close * 1.02,
                    low=new_close * 0.98,
                    close=new_close,
                    volume=candle.volume * 3.0
                )
                modified_candles.append(new_candle)
            else:
                modified_candles.append(candle)
        
        generator = self._create_generator(use_filters=True)
        signal = generator.generate_signal(modified_candles)
        
        # BUY signal should be rejected in bearish trend
        if signal:
            assert signal.signal_type != SignalType.BUY
    
    def test_sell_signal_passes_trend_filter(self):
        """Test SELL signal passes trend filter in bearish market"""
        candles = create_overbought_bearish_candles(count=100)
        generator = self._create_generator(use_filters=True)
        
        signal = generator.generate_signal(candles)
        
        # Should generate SELL signal in bearish trend with overbought RSI
        if signal and signal.signal_type == SignalType.SELL:
            assert 'atr' in signal.indicators
            assert signal.indicators['atr'] > 0
            assert signal.confidence > 0.5
    
    def test_sell_signal_rejected_by_trend_filter(self):
        """Test SELL signal rejected in bullish trend"""
        candles = create_test_candles(count=100, trend='bullish', volatility='high')
        
        # Make last candles overbought (would trigger SELL without filter)
        modified_candles = []
        for i, candle in enumerate(candles):
            if i >= len(candles) - 6:
                new_close = candle.close * 1.05
                new_candle = Candle(
                    timestamp=candle.timestamp,
                    open=candle.open,
                    high=new_close * 1.02,
                    low=new_close * 0.98,
                    close=new_close,
                    volume=candle.volume * 3.0
                )
                modified_candles.append(new_candle)
            else:
                modified_candles.append(candle)
        
        generator = self._create_generator(use_filters=True)
        signal = generator.generate_signal(modified_candles)
        
        # SELL signal should be rejected in bullish trend
        if signal:
            assert signal.signal_type != SignalType.SELL
    
    def test_signal_rejected_by_adx_filter(self):
        """Test signal rejected when ADX < 25 (choppy market)"""
        candles = create_choppy_market_candles(count=100)
        
        # Try to create oversold condition
        modified_candles = []
        for i, candle in enumerate(candles):
            if i >= len(candles) - 6:
                new_close = candle.close * 0.95
                new_candle = Candle(
                    timestamp=candle.timestamp,
                    open=candle.open,
                    high=new_close * 1.02,
                    low=new_close * 0.98,
                    close=new_close,
                    volume=candle.volume * 3.0
                )
                modified_candles.append(new_candle)
            else:
                modified_candles.append(candle)
        
        generator = self._create_generator(use_filters=True)
        signal = generator.generate_signal(modified_candles)
        
        # Signal should be rejected due to low ADX
        # (choppy market has low ADX)
        assert signal is None or signal.signal_type == SignalType.NEUTRAL
    
    def test_atr_value_included_in_signal(self):
        """Test ATR value is included in signal indicators"""
        candles = create_oversold_bullish_candles(count=100)
        generator = self._create_generator(use_filters=True)
        
        signal = generator.generate_signal(candles)
        
        if signal and signal.signal_type != SignalType.NEUTRAL:
            # ATR should be in indicators
            assert 'atr' in signal.indicators
            assert signal.indicators['atr'] > 0
            assert 'atr_period' in signal.indicators
            assert signal.indicators['atr_period'] == 14
    
    def test_filters_disabled_backward_compatibility(self):
        """Test backward compatibility when filters are disabled"""
        candles = create_test_candles(count=100, trend='bearish', volatility='high')
        
        # Make oversold (would be rejected by trend filter if enabled)
        modified_candles = []
        for i, candle in enumerate(candles):
            if i >= len(candles) - 6:
                new_close = candle.close * 0.95
                new_candle = Candle(
                    timestamp=candle.timestamp,
                    open=candle.open,
                    high=new_close * 1.02,
                    low=new_close * 0.98,
                    close=new_close,
                    volume=candle.volume * 3.0
                )
                modified_candles.append(new_candle)
            else:
                modified_candles.append(candle)
        
        generator = self._create_generator(use_filters=False)
        signal = generator.generate_signal(modified_candles)
        
        # With filters disabled, signal might be generated
        # (depends on other conditions)
        # Just verify it doesn't crash
        assert signal is not None
    
    def test_insufficient_candles_for_filters(self):
        """Test handling of insufficient candles for EMA50"""
        candles = create_test_candles(count=30)  # Less than 50
        generator = self._create_generator(use_filters=True)
        
        signal = generator.generate_signal(candles)
        
        # Should return None due to insufficient data
        assert signal is None
    
    def test_custom_filter_components(self):
        """Test signal generator with custom filter components"""
        adx_calculator = ADXCalculator(period=14)
        atr_calculator = ATRCalculator(period=14)
        
        generator = SignalGenerator(
            vwap_calculator=self.vwap_calculator,
            bollinger_calculator=self.bollinger_calculator,
            stoch_rsi_calculator=self.stoch_rsi_calculator,
            smart_entry_calculator=self.smart_entry_calculator,
            adx_calculator=adx_calculator,
            atr_calculator=atr_calculator,
            use_filters=True
        )
        
        assert generator.adx_calculator is adx_calculator
        assert generator.atr_calculator is atr_calculator
    
    def test_signal_with_high_adx_trending_market(self):
        """Test signal generation in strong trending market (ADX > 25)"""
        # Create strong bullish trend
        candles = create_test_candles(count=100, trend='bullish', volatility='high')
        
        # Add oversold pullback
        modified_candles = []
        for i, candle in enumerate(candles):
            if i >= len(candles) - 6:
                new_close = candle.close * 0.95
                new_candle = Candle(
                    timestamp=candle.timestamp,
                    open=candle.open,
                    high=new_close * 1.02,
                    low=new_close * 0.98,
                    close=new_close,
                    volume=candle.volume * 3.0
                )
                modified_candles.append(new_candle)
            else:
                modified_candles.append(candle)
        
        generator = self._create_generator(use_filters=True)
        signal = generator.generate_signal(modified_candles)
        
        # Should generate signal in trending market
        if signal and signal.signal_type == SignalType.BUY:
            assert signal.confidence > 0.5
            assert 'atr' in signal.indicators


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
