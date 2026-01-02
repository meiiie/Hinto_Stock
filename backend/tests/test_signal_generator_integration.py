"""
Integration tests for SignalGenerator (Limit Sniper Strategy).

Tests the integration of Limit Sniper logic:
- Swing Point Liquidity Capture
- Limit Order Placement
- ATR-based filtering (implicitly via context)
"""

import pytest
from datetime import datetime, timedelta
from typing import List

from src.domain.entities.candle import Candle
from src.domain.entities.trading_signal import SignalType
from src.application.signals.signal_generator import SignalGenerator
from src.infrastructure.indicators.vwap_calculator import VWAPCalculator
from src.infrastructure.indicators.bollinger_calculator import BollingerCalculator
from src.infrastructure.indicators.stoch_rsi_calculator import StochRSICalculator
from src.infrastructure.indicators.atr_calculator import ATRCalculator
from src.application.services.tp_calculator import TPCalculator
from src.application.services.stop_loss_calculator import StopLossCalculator


def create_test_candles(count: int = 100, base_price: float = 100.0) -> List[Candle]:
    """Create basic test candles"""
    candles = []
    base_time = datetime(2025, 1, 1, 0, 0, 0)
    
    for i in range(count):
        timestamp = base_time + timedelta(minutes=15 * i)
        price = base_price + (i * 0.1) # Slow drift up
        candle = Candle(
            timestamp=timestamp,
            open=price,
            high=price + 0.5,
            low=price - 0.5,
            close=price,
            volume=1000.0
        )
        candles.append(candle)
    return candles


class TestSignalGeneratorLimitSniper:
    """Tests for Limit Sniper Strategy in SignalGenerator"""
    
    def setup_method(self):
        """Setup dependencies"""
        self.vwap_calculator = VWAPCalculator()
        self.bollinger_calculator = BollingerCalculator()
        self.stoch_rsi_calculator = StochRSICalculator()
        self.atr_calculator = ATRCalculator()
        self.tp_calculator = TPCalculator()
        self.stop_loss_calculator = StopLossCalculator()

        self.generator = SignalGenerator(
            vwap_calculator=self.vwap_calculator,
            bollinger_calculator=self.bollinger_calculator,
            stoch_rsi_calculator=self.stoch_rsi_calculator,
            atr_calculator=self.atr_calculator,
            tp_calculator=self.tp_calculator,
            stop_loss_calculator=self.stop_loss_calculator
        )

    def test_initialization(self):
        assert self.generator is not None
        assert self.generator.atr_calculator is not None

    def test_insufficient_data(self):
        """Test with too few candles"""
        candles = create_test_candles(count=30)
        signal = self.generator.generate_signal(candles, symbol="BTCUSDT")
        assert signal is None

    def test_buy_signal_swing_low(self):
        """Test Limit Buy Signal at Swing Low"""
        candles = create_test_candles(count=60, base_price=100.0)
        
        # 1. Create a Swing Low at index -10 (within lookback 20)
        # Swing Low price = 90.0
        swing_low_idx = -10
        # Create replacement candle with Low=90
        original_c = candles[swing_low_idx]
        candles[swing_low_idx] = Candle(
            timestamp=original_c.timestamp,
            open=original_c.open,
            high=original_c.high,
            low=90.0,
            close=91.0,
            volume=original_c.volume
        )
        
        # 2. Current price approaches Swing Low (e.g. 90.5)
        # Threshold is 1.5% (0.015)
        # 90.5 is within 1.5% of 90.0 ( (90.5-90)/90 = 0.0055 )
        original_last = candles[-1]
        candles[-1] = Candle(
            timestamp=original_last.timestamp,
            open=original_last.open,
            high=91.0,
            low=90.0,
            close=90.5,
            volume=original_last.volume
        )
        
        # Ensure ATR is valid (calculated from previous volatility)
        
        signal = self.generator.generate_signal(candles, symbol="BTCUSDT")
        
        assert signal is not None
        assert signal.signal_type == SignalType.BUY
        assert signal.is_limit_order is True
        # Limit price should be 0.1% below Swing Low (90.0 * 0.999 = 89.91)
        expected_limit = 90.0 * 0.999
        assert abs(signal.entry_price - expected_limit) < 0.01
        assert signal.symbol == "BTCUSDT"

    def test_sell_signal_swing_high(self):
        """Test Limit Sell Signal at Swing High"""
        candles = create_test_candles(count=60, base_price=100.0)
        
        # 1. Create a Swing High at index -10
        # Swing High price = 110.0
        swing_high_idx = -10
        original_c = candles[swing_high_idx]
        candles[swing_high_idx] = Candle(
            timestamp=original_c.timestamp,
            open=original_c.open,
            high=110.0,
            low=original_c.low,
            close=109.0,
            volume=original_c.volume
        )
        
        # 2. Current price approaches Swing High (e.g. 109.0)
        original_last = candles[-1]
        candles[-1] = Candle(
            timestamp=original_last.timestamp,
            open=original_last.open,
            high=110.0,
            low=original_last.low,
            close=109.0,
            volume=original_last.volume
        )
        
        signal = self.generator.generate_signal(candles, symbol="BTCUSDT")
        
        assert signal is not None
        assert signal.signal_type == SignalType.SELL
        assert signal.is_limit_order is True
        # Limit price should be 0.1% above Swing High (110.0 * 1.001 = 110.11)
        expected_limit = 110.0 * 1.001
        assert abs(signal.entry_price - expected_limit) < 0.01

    def test_no_signal_mid_range(self):
        """Test no signal when price is far from swing points"""
        candles = create_test_candles(count=60, base_price=100.0)
        
        # Swing Low 90, Swing High 110
        idx = -10
        orig = candles[idx]
        candles[idx] = Candle(
            timestamp=orig.timestamp,
            open=orig.open,
            high=110.0,
            low=90.0,
            close=orig.close,
            volume=orig.volume
        )
        
        # Current Price 100.0 (Mid range)
        last = candles[-1]
        candles[-1] = Candle(
            timestamp=last.timestamp,
            open=last.open,
            high=last.high,
            low=last.low,
            close=100.0,
            volume=last.volume
        )
        
        signal = self.generator.generate_signal(candles, symbol="BTCUSDT")
        
        assert signal is None
