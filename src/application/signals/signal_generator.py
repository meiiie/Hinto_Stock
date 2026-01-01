"""
SignalGenerator - Application Layer

Generates trading signals using Liquidity Sniper strategy (Limit Orders).
SOTA Logic: Front-running liquidity sweeps at Swing Points.
"""

import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field

from ...domain.entities.candle import Candle
from ...domain.entities.trading_signal import TradingSignal, SignalType, SignalPriority
from ...domain.interfaces import (
    IVWAPCalculator,
    IBollingerCalculator,
    IStochRSICalculator,
    ISFPDetector,
    SFPType,
    IATRCalculator
)
from ..services.tp_calculator import TPCalculator
from ..services.stop_loss_calculator import StopLossCalculator
from ...strategies.strategy_registry import StrategyRegistry, StrategyConfig


@dataclass
class MarketContext:
    candles: List[Candle]
    current_candle: Candle
    current_price: float
    vwap_result: Optional[Any] = None
    bb_result: Optional[Any] = None
    stoch_result: Optional[Any] = None
    atr_result: Optional[Any] = None
    sfp_result: Optional[Any] = None
    indicators: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_valid(self) -> bool:
        return True 


class SignalGenerator:
    def __init__(
        self,
        vwap_calculator: IVWAPCalculator,
        bollinger_calculator: IBollingerCalculator,
        stoch_rsi_calculator: IStochRSICalculator,
        sfp_detector: Optional[ISFPDetector] = None,
        atr_calculator: Optional[IATRCalculator] = None,
        volume_profile_calculator: Optional[Any] = None,
        tp_calculator: Optional[TPCalculator] = None,
        stop_loss_calculator: Optional[StopLossCalculator] = None,
        account_size: float = 100.0,
        **kwargs
    ):
        self.vwap_calculator = vwap_calculator
        self.bollinger_calculator = bollinger_calculator
        self.stoch_rsi_calculator = stoch_rsi_calculator
        self.sfp_detector = sfp_detector
        self.atr_calculator = atr_calculator
        self.volume_profile_calculator = volume_profile_calculator
        self.tp_calculator = tp_calculator or TPCalculator()
        self.stop_loss_calculator = stop_loss_calculator or StopLossCalculator()
        
        self.account_size = account_size
        self.logger = logging.getLogger(__name__)

    def _prepare_market_context(self, candles: List[Candle]) -> MarketContext:
        current_candle = candles[-1]
        ctx = MarketContext(candles=candles, current_candle=current_candle, current_price=current_candle.close)
        
        ctx.vwap_result = self.vwap_calculator.calculate_vwap(candles)
        ctx.stoch_result = self.stoch_rsi_calculator.calculate_stoch_rsi(candles)
        ctx.bb_result = self.bollinger_calculator.calculate_bands(candles, ctx.current_price)
        
        if self.atr_calculator:
            ctx.atr_result = self.atr_calculator.calculate_atr(candles)
            
        ctx.indicators = {
            'atr': ctx.atr_result.atr_value if ctx.atr_result else 0
        }
        return ctx

    def generate_signal(self, candles: List[Candle], symbol: str, htf_bias: str = 'NEUTRAL', **kwargs) -> Optional[TradingSignal]:
        if len(candles) < 50: return None
        config = StrategyRegistry.get_config(symbol)
        ctx = self._prepare_market_context(candles)
        
        # Use Limit Sniper Logic
        return self._strategy_liquidity_sniper(ctx, config, symbol, htf_bias)

    def _strategy_liquidity_sniper(self, ctx: MarketContext, config: StrategyConfig, symbol: str, htf_bias: str) -> Optional[TradingSignal]:
        if not ctx.atr_result: return None
        
        # 1. Find recent Swing High/Low
        lookback = 20
        recent_candles = ctx.candles[-(lookback+1):-1]
        swing_low = min([c.low for c in recent_candles])
        swing_high = max([c.high for c in recent_candles])
        
        # 2. Check Proximity
        current_price = ctx.current_price
        dist_to_low = (current_price - swing_low) / swing_low
        dist_to_high = (swing_high - current_price) / swing_high
        
        signal_type = None
        limit_price = 0.0
        
        # BUY: Price near Swing Low
        if 0 < dist_to_low < 0.015:
            limit_price = swing_low * 0.999
            signal_type = SignalType.BUY
            # SL = 0.5% below limit price (Institutional standard)
            stop_loss = limit_price * 0.995
            tp1 = limit_price * 1.02 # 2% Target (4:1 R:R)
            
        # SELL: Price near Swing High
        elif 0 < dist_to_high < 0.015:
            limit_price = swing_high * 1.001
            signal_type = SignalType.SELL
            stop_loss = limit_price * 1.005
            tp1 = limit_price * 0.98
            
        if not signal_type: return None

        # SOTA: HTF Bias Filter DISABLED for SFP (Counter-trend nature)
        # if signal_type == SignalType.BUY and htf_bias == 'BEARISH':
        #     return None
        # if signal_type == SignalType.SELL and htf_bias == 'BULLISH':
        #     return None

        # 3. Calculate Score (for Shark Tank)
        # Higher score if closer to VWAP stretch or other confluence
        score = 0.7 # Base
        if ctx.vwap_result:
            vwap_dist = abs(current_price - ctx.vwap_result.vwap) / ctx.vwap_result.vwap
            score += min(0.2, vwap_dist * 10) # Max +0.2 bonus

        signal = TradingSignal(
            symbol=symbol,
            signal_type=signal_type,
            confidence=score,
            generated_at=ctx.current_candle.timestamp,
            price=ctx.current_price,
            entry_price=limit_price,
            is_limit_order=True,
            stop_loss=stop_loss,
            tp_levels={'tp1': tp1, 'tp2': tp1 * 1.05, 'tp3': tp1 * 1.1},
            risk_reward_ratio=(abs(tp1 - limit_price) / abs(limit_price - stop_loss)),
            reasons=[f"Sniper Limit @ {limit_price:.2f}"],
            indicators=ctx.indicators
        )
        return signal