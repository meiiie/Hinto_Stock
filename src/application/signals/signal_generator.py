"""
SignalGenerator - Application Layer

Generates trading signals by combining multiple technical indicators.

NOTE: Uses Dependency Injection - all infrastructure dependencies
are injected via constructor using domain interfaces.
"""

import logging
from datetime import datetime
import pandas as pd
from typing import List, Optional, Dict, Any, TYPE_CHECKING
from dataclasses import dataclass, field
from enum import Enum

# Domain imports (allowed)
from ...domain.entities.candle import Candle
from ...domain.entities.trading_signal import TradingSignal, SignalType, ConfidenceLevel
from ...domain.interfaces import (
    IVolumeSpikeDetector,
    IATRCalculator,
    IADXCalculator,
    IIndicatorCalculator,
    IVWAPCalculator,
    IBollingerCalculator,
    IStochRSICalculator,
)

# Application imports (allowed)
from ..services.tp_calculator import TPCalculator
from ..services.stop_loss_calculator import StopLossCalculator
from ..services.confidence_calculator import ConfidenceCalculator
from ..services.smart_entry_calculator import SmartEntryCalculator


class SignalGenerator:
    """
    Generates trading signals by combining technical indicators.
    
    Strategy: Trend Pullback
    - Trend: VWAP
    - Setup: Bollinger Bands / VWAP Pullback
    - Trigger: StochRSI
    """
    
    def __init__(
        self,
        # Required dependencies (DI) - using interfaces
        vwap_calculator: IVWAPCalculator,
        bollinger_calculator: IBollingerCalculator,
        stoch_rsi_calculator: IStochRSICalculator,
        smart_entry_calculator: SmartEntryCalculator,
        # Optional dependencies - using interfaces
        volume_spike_detector: Optional[IVolumeSpikeDetector] = None,
        adx_calculator: Optional[IADXCalculator] = None,
        atr_calculator: Optional[IATRCalculator] = None,
        talib_calculator: Optional[IIndicatorCalculator] = None,
        tp_calculator: Optional[TPCalculator] = None,
        stop_loss_calculator: Optional[StopLossCalculator] = None,
        confidence_calculator: Optional[ConfidenceCalculator] = None,
        # Config
        account_size: float = 10000.0,
        use_filters: bool = True,
        strict_mode: bool = True
    ):
        """
        Initialize signal generator with dependency injection.
        
        All infrastructure dependencies are injected via constructor.
        Application-layer services (TPCalculator, etc.) can have defaults.
        """
        # Store injected infrastructure dependencies
        self.volume_spike_detector = volume_spike_detector
        self.adx_calculator = adx_calculator
        self.atr_calculator = atr_calculator
        self.talib_calculator = talib_calculator
        
        # Application-layer services (can have defaults)
        self.tp_calculator = tp_calculator or TPCalculator()
        self.stop_loss_calculator = stop_loss_calculator or StopLossCalculator()
        self.confidence_calculator = confidence_calculator or ConfidenceCalculator()
        
        # Required injected calculators
        self.vwap_calculator = vwap_calculator
        self.bollinger_calculator = bollinger_calculator
        self.stoch_rsi_calculator = stoch_rsi_calculator
        self.smart_entry_calculator = smart_entry_calculator
        
        self.account_size = account_size
        self.use_filters = use_filters
        self.strict_mode = strict_mode
        self.logger = logging.getLogger(__name__)


    
    def generate_signal(self, candles: List[Candle]) -> Optional[TradingSignal]:
        """
        Generate trading signal based on current market conditions.
        
        Enhanced with trend and volatility filters:
        1. Check volatility filter (ADX > 25) - reject choppy market signals
        2. Calculate ATR for dynamic stop loss and take profit
        3. Apply stricter signal conditions
        
        Args:
            candles: List of Candle entities (chronological order)
        
        Returns:
            TradingSignal or None if insufficient data or filters reject
        """
        if not candles or len(candles) < 50:  # Need 50 for EMA50
            self.logger.debug("Insufficient candles for signal generation (need 50+)")
            return None
        
        try:
            # Get current candle
            current_candle = candles[-1]
            current_price = current_candle.close
            
            # Calculate indicators using TALibCalculator
            # Convert candles to DataFrame first
            df = pd.DataFrame({
                'open': [c.open for c in candles],
                'high': [c.high for c in candles],
                'low': [c.low for c in candles],
                'close': [c.close for c in candles],
                'volume': [c.volume for c in candles]
            })
            
            talib_indicators_df = self.talib_calculator.calculate_all(df)
            
            # Extract latest indicator values
            ema_7_current = talib_indicators_df['ema_7'].iloc[-1] if 'ema_7' in talib_indicators_df else None
            ema_25_current = talib_indicators_df['ema_25'].iloc[-1] if 'ema_25' in talib_indicators_df else None
            rsi_value = talib_indicators_df['rsi_6'].iloc[-1] if 'rsi_6' in talib_indicators_df else None
            
            # Calculate ATR for stop loss and take profit
            atr_result = None
            if self.use_filters:
                atr_result = self.atr_calculator.calculate_atr(candles)
                if atr_result and atr_result.atr_value > 0:
                    self.logger.debug(
                        f"ATR calculated: ${atr_result.atr_value:.2f} "
                        f"(period: {atr_result.period})"
                    )
            
            # Check volatility filter (ADX > 25)
            # Store ADX info for confidence penalty, but don't block signal
            adx_trending = True
            adx_value = None
            if self.use_filters:
                adx_result = self.adx_calculator.calculate_adx(candles)
                if adx_result and adx_result.adx_value > 0:
                    adx_value = adx_result.adx_value
                    if not adx_result.is_trending:
                        adx_trending = False
                        self.logger.warning(
                            f"Low ADX ({adx_result.adx_value:.1f}) - choppy market, "
                            f"will reduce confidence"
                        )
            
            # Detect volume spike using professional detector
            volumes = [c.volume for c in candles]
            volume_spike_result = self.volume_spike_detector.detect_spike_from_list(
                volumes=volumes,
                ma_period=20
            )
            
            # Collect indicators
            indicators = {
                'timestamp': current_candle.timestamp,  # Add timestamp for accurate backtest timing
                'rsi': rsi_value,
                'volume_spike_intensity': volume_spike_result.intensity.value if volume_spike_result else 'none',
                'volume_spike_ratio': volume_spike_result.ratio if volume_spike_result else 0.0,
                'ema_7': ema_7_current,
                'ema_25': ema_25_current,
                'price': current_price,
                'atr': atr_result.atr_value if atr_result else None,
                'atr_period': atr_result.period if atr_result else None,
                'adx_value': adx_value,
                'adx_trending': adx_trending
            }
            
            # Initialize new indicator results
            vwap_result = None
            bb_result = None
            stoch_result = None
            
            # Calculate new Trend Pullback indicators
            try:
                # VWAP - trend direction
                vwap_result = self.vwap_calculator.calculate_vwap(candles)
                if vwap_result:
                    indicators['vwap'] = vwap_result.vwap
                    indicators['price_vs_vwap'] = 'above' if current_price > vwap_result.vwap else 'below'
                    indicators['vwap_distance_pct'] = self.vwap_calculator.calculate_distance_from_vwap(
                        current_price, vwap_result.vwap
                    )
                
                # Bollinger Bands - volatility and support/resistance
                bb_result = self.bollinger_calculator.calculate_bands(candles, current_price)
                if bb_result:
                    indicators['bb_upper'] = bb_result.upper_band
                    indicators['bb_middle'] = bb_result.middle_band
                    indicators['bb_lower'] = bb_result.lower_band
                    indicators['bb_bandwidth'] = bb_result.bandwidth
                    indicators['bb_percent_b'] = bb_result.percent_b
                
                # Stochastic RSI - entry trigger
                stoch_result = self.stoch_rsi_calculator.calculate_stoch_rsi(candles)
                if stoch_result:
                    indicators['stoch_k'] = stoch_result.k_value
                    indicators['stoch_d'] = stoch_result.d_value
                    indicators['stoch_zone'] = stoch_result.zone.value
                    indicators['stoch_oversold'] = stoch_result.is_oversold
                    indicators['stoch_overbought'] = stoch_result.is_overbought
                    indicators['stoch_k_cross_up'] = stoch_result.k_cross_up
                    indicators['stoch_k_cross_down'] = stoch_result.k_cross_down
            except Exception as e:
                self.logger.warning(f"Error calculating new indicators: {e}")
                # Continue with old indicators if new ones fail
            
            
            # Generate buy signal
            buy_signal = self._check_buy_conditions(
                candles, current_price, vwap_result, bb_result, stoch_result, volume_spike_result, indicators
            )
            
            if buy_signal:
                return self._enrich_signal(buy_signal, candles, ema_7_current, ema_25_current, atr_result, vwap_result)
            
            # Generate sell signal
            sell_signal = self._check_sell_conditions(
                candles, current_price, vwap_result, bb_result, stoch_result, volume_spike_result, indicators
            )
            
            if sell_signal:
                return self._enrich_signal(sell_signal, candles, ema_7_current, ema_25_current, atr_result, vwap_result)
            
            # No signal - return neutral
            return TradingSignal(
                signal_type=SignalType.NEUTRAL,
                confidence=0.0,
                timestamp=current_candle.timestamp,  # FIX: Use candle timestamp not datetime.now()
                price=current_price,
                indicators=indicators,
                reasons=["No clear signal - waiting for better conditions"]
            )
            
        except Exception as e:
            self.logger.error(f"Error generating signal: {e}", exc_info=True)
            return None

    def _enrich_signal(
        self, 
        signal: TradingSignal, 
        candles: List[Candle],
        ema7: float,
        ema25: float,
        atr_result: Optional[Any],
        vwap_result: Optional[Any] = None
    ) -> TradingSignal:
        """
        Enrich signal with Smart Entry, TP, SL, and Confidence calculations.
        """
        direction = 'BUY' if signal.signal_type == SignalType.BUY else 'SELL'
        current_candle = candles[-1]
        
        # 1. Calculate Smart Entry Price (Limit Order)
        # We use the SmartEntryCalculator to find optimal entry within the signal candle
        entry_result = self.smart_entry_calculator.calculate_entry_price(
            signal_candle=current_candle,
            signal_type=signal.signal_type
        )
        
        # Optional: Check if VWAP is a better entry
        if vwap_result:
             vwap_entry = self.smart_entry_calculator.calculate_entry_with_vwap(
                signal_candle=current_candle,
                signal_type=signal.signal_type,
                vwap=vwap_result.vwap
             )
             # Use VWAP entry if it offers better price (lower for buy, higher for sell)
             if signal.signal_type == SignalType.BUY:
                 signal.entry_price = min(entry_result.entry_price, vwap_entry)
             else:
                 signal.entry_price = max(entry_result.entry_price, vwap_entry)
        else:
             signal.entry_price = entry_result.entry_price
             
        signal.reasons.append(f"Smart Entry: ${signal.entry_price:.2f} (Limit Order)")
            
        # 2. Calculate Stop Loss
        # Use ATR-based stop if available, otherwise Swing/EMA
        sl_result = None
        if atr_result:
             sl_result = self.stop_loss_calculator.calculate_stop_loss_atr_based(
                entry_price=signal.entry_price,
                direction=direction,
                atr_value=atr_result.atr_value
                # Note: calculate_stop_loss_atr_based doesn't accept account_size
            )
        else:
            sl_result = self.stop_loss_calculator.calculate_stop_loss(
                entry_price=signal.entry_price,
                direction=direction,
                candles=candles,
                ema25=ema25,
                account_size=self.account_size
            )
            
        if sl_result:
            signal.stop_loss = sl_result.stop_loss
            signal.reasons.append(f"Stop Loss: ${sl_result.stop_loss:.2f} ({sl_result.stop_type})")
            
        # 3. Calculate Take Profit
        if signal.stop_loss:
            tp_result = self.tp_calculator.calculate_tp_levels(
                entry_price=signal.entry_price,
                stop_loss=signal.stop_loss,
                direction=direction,
                candles=candles
            )
            
            if tp_result:
                signal.tp_levels = {
                    'tp1': tp_result.tp_levels.tp1,
                    'tp2': tp_result.tp_levels.tp2,
                    'tp3': tp_result.tp_levels.tp3
                }
                signal.risk_reward_ratio = tp_result.risk_reward_ratio
                signal.reasons.append(f"TP Targets: 3 levels (R:R {tp_result.risk_reward_ratio:.2f})")
        
        # 4. Calculate Position Size
        if signal.stop_loss:
            pos_size = self.stop_loss_calculator.calculate_position_size_with_risk(
                entry_price=signal.entry_price,
                stop_loss=signal.stop_loss,
                account_balance=self.account_size,
                risk_pct=0.01
            )
            signal.position_size = pos_size
            
        # 5. Recalculate Confidence using dedicated calculator
        # We map our conditions to the calculator's expected inputs
        # This is a simplification; ideally we'd pass the raw objects
        # But ConfidenceCalculator takes specific args.
        # Let's see what ConfidenceCalculator.calculate_confidence takes:
        # direction, ema_crossover, volume_spike, rsi_value
        
        # Extract volume spike intensity
        vol_spike = 'none'
        if signal.indicators.get('volume_spike_intensity'):
             vol_spike = signal.indicators.get('volume_spike_intensity').lower()
             
        # Extract crossover
        crossover = 'none'
            
        # Calculate
        new_confidence = self.confidence_calculator.calculate_confidence(
            direction=direction,
            ema_crossover=crossover,
            volume_spike=vol_spike,
            rsi_value=signal.indicators.get('rsi', 50)
        )
        
        # Apply ADX penalty if market is choppy
        final_confidence = new_confidence.confidence_score  # FIX: use confidence_score not score
        if not signal.indicators.get('adx_trending', True):
            adx_penalty = 0.20  # 20% reduction for choppy market
            final_confidence *= (1 - adx_penalty)
            signal.reasons.append(f"ADX penalty applied: -{adx_penalty:.0%} (choppy market)")
        
        # Update signal confidence (convert from 0-100 to 0-1 scale)
        signal.confidence = final_confidence / 100.0
        signal.reasons.append(f"Confidence: {signal.confidence:.0%}")
        
        # 6. Strict R:R Check (Master Spec)
        # If R:R < 0.8, invalidate the signal (Relaxed from 1.0 per Expert Feedback)
        if hasattr(signal, 'risk_reward_ratio') and signal.risk_reward_ratio < 0.8:
            signal.signal_type = SignalType.NEUTRAL
            signal.reasons.append(f"INVALIDATED: R:R {signal.risk_reward_ratio:.2f} < 0.8 (Strict Filter)")
            return None # Strictly return None for invalidated signals

        # 7. Volume Climax Filter (Task B)
        # If volume is too high (> 4.0x), it might be a climax/exhaustion, not a breakout
        if signal.indicators.get('volume_spike_ratio', 0) > 4.0:
            signal.signal_type = SignalType.NEUTRAL
            signal.reasons.append(f"INVALIDATED: Volume Climax (Ratio {signal.indicators.get('volume_spike_ratio'):.1f}x > 4.0x)")
            return None

        return signal

    def _check_buy_conditions(
        self,
        candles: List[Candle],
        current_price: float,
        vwap_result: Optional[Any],
        bb_result: Optional[Any],
        stoch_result: Optional[Any],
        volume_spike_result: Optional[Any],  # VolumeSpikeResult
        indicators: Dict[str, Any] = None
    ) -> Optional[TradingSignal]:
        """
        Check for BUY signal using Trend Pullback Strategy.
        
        Logic:
        1. Trend: Price > VWAP (Bullish Bias)
        2. Setup: Price pullback to Lower Band or VWAP
        3. Trigger: StochRSI Cross Up (K > D) in Oversold/Neutral zone
        4. Confirmation: Green Candle + Volume
        """
        if not (vwap_result and bb_result and stoch_result):
            return None
            
        current_candle = candles[-1]
        reasons = []
        conditions_met = 0
        
        # 1. Trend Filter: Price > VWAP
        if current_price > vwap_result.vwap:
            conditions_met += 1
            reasons.append("Trend: Price > VWAP (Bullish)")
        elif self.strict_mode:
            return None  # Strict mode requires trend alignment
            
        # 2. Setup: Pullback to Value Area (Lower Band or VWAP)
        # Check if price is near Lower Band OR near VWAP
        is_near_lower = self.bollinger_calculator.is_near_lower_band(current_price, bb_result.lower_band, threshold_pct=0.015)
        is_near_vwap = self.vwap_calculator.is_above_vwap(current_price, vwap_result.vwap, buffer_pct=0.0) and \
                       self.vwap_calculator.calculate_distance_from_vwap(current_price, vwap_result.vwap) < 1.0
                       
        if is_near_lower or is_near_vwap:
            conditions_met += 1
            reasons.append("Setup: Pullback to Value Area (Lower BB/VWAP)")
        
        # 3. Trigger: StochRSI Cross Up
        # We want K crossing above D, and ideally K is not too high yet
        # Master Spec: Threshold 30 (was 20)
        if stoch_result.k_cross_up and stoch_result.k_value < 80:
            conditions_met += 1
            reasons.append(f"Trigger: StochRSI Cross Up (K={stoch_result.k_value:.1f})")
        elif stoch_result.k_value < 30: # Oversold threshold 30
             # Alternative trigger: Just being oversold is a setup, waiting for cross
             reasons.append(f"Setup: StochRSI Oversold (K={stoch_result.k_value:.1f} < 30)")
        
        # 4. Confirmation: Candle Color & Volume
        is_green = current_candle.close > current_candle.open
        if is_green:
            conditions_met += 1
            reasons.append("Candle: Green (Bullish)")
            
        # Volume confirmation
        if volume_spike_result and volume_spike_result.is_spike:
            conditions_met += 1
            reasons.append(f"Volume: Spike {volume_spike_result.intensity.value}")
            
        # Decision Logic
        # We need at least Trend + Trigger + One Confirmation
        min_conditions = 4 if self.strict_mode else 3
        
        if conditions_met >= min_conditions:
            # Calculate confidence
            confidence = conditions_met / 5.0
            
            return TradingSignal(
                signal_type=SignalType.BUY,
                confidence=confidence,
                timestamp=current_candle.timestamp,
                price=current_price,
                reasons=reasons,
                indicators=indicators or {}
            )
            
        return None
    
    def _check_sell_conditions(
        self,
        candles: List[Candle],
        current_price: float,
        vwap_result: Optional[Any],
        bb_result: Optional[Any],
        stoch_result: Optional[Any],
        volume_spike_result: Optional[Any],  # VolumeSpikeResult
        indicators: Dict[str, Any] = None
    ) -> Optional[TradingSignal]:
        """
        Check for SELL signal using Trend Pullback Strategy.
        
        Logic:
        1. Trend: Price < VWAP (Bearish Bias)
        2. Setup: Price rally to Upper Band or VWAP
        3. Trigger: StochRSI Cross Down (K < D) in Overbought/Neutral zone
        4. Confirmation: Red Candle + Volume
        """
        if not (vwap_result and bb_result and stoch_result):
            return None
            
        current_candle = candles[-1]
        reasons = []
        conditions_met = 0
        
        # 1. Trend Filter: Price < VWAP
        if current_price < vwap_result.vwap:
            conditions_met += 1
            reasons.append("Trend: Price < VWAP (Bearish)")
        elif self.strict_mode:
            return None  # Strict mode requires trend alignment
            
        # 2. Setup: Rally to Value Area (Upper Band or VWAP)
        # Check if price is near Upper Band OR near VWAP
        is_near_upper = self.bollinger_calculator.is_near_upper_band(current_price, bb_result.upper_band, threshold_pct=0.015)
        is_near_vwap = self.vwap_calculator.is_below_vwap(current_price, vwap_result.vwap, buffer_pct=0.0) and \
                       abs(self.vwap_calculator.calculate_distance_from_vwap(current_price, vwap_result.vwap)) < 1.0
                       
        if is_near_upper or is_near_vwap:
            conditions_met += 1
            reasons.append("Setup: Rally to Value Area (Upper BB/VWAP)")
        
        # 3. Trigger: StochRSI Cross Down
        # We want K crossing below D, and ideally K is not too low yet
        # Master Spec: Threshold 70 (was 80)
        if stoch_result.k_cross_down and stoch_result.k_value > 20:
            conditions_met += 1
            reasons.append(f"Trigger: StochRSI Cross Down (K={stoch_result.k_value:.1f})")
        elif stoch_result.k_value > 70: # Overbought threshold 70
             reasons.append(f"Setup: StochRSI Overbought (K={stoch_result.k_value:.1f} > 70)")
        
        # 4. Confirmation: Candle Color & Volume
        is_red = current_candle.close < current_candle.open
        if is_red:
            conditions_met += 1
            reasons.append("Candle: Red (Bearish)")
            
        # Volume confirmation
        if volume_spike_result and volume_spike_result.is_spike:
            conditions_met += 1
            reasons.append(f"Volume: Spike {volume_spike_result.intensity.value}")
            
        # Decision Logic
        min_conditions = 4 if self.strict_mode else 3
        
        if conditions_met >= min_conditions:
            # Calculate confidence
            confidence = conditions_met / 5.0
            
            return TradingSignal(
                signal_type=SignalType.SELL,
                confidence=confidence,
                timestamp=current_candle.timestamp,
                price=current_price,
                reasons=reasons,
                indicators=indicators or {}
            )
            
        return None

    
    def __repr__(self) -> str:
        """String representation"""
        return (
            f"SignalGenerator("
            f"vwap={self.vwap_calculator}, "
            f"bb={self.bollinger_calculator}, "
            f"stoch={self.stoch_rsi_calculator}"
            f")"
        )
