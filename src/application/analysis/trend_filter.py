"""
Trend Filter - Application Layer

Filter trades based on higher timeframe trend using EMA(50).
"""

import logging
from typing import List, Tuple
from enum import Enum

from ...domain.entities.candle import Candle


class TrendDirection(Enum):
    """Trend direction classification"""
    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"


class TrendFilter:
    """
    Filter trades based on higher timeframe trend.
    
    Uses EMA(50) to determine trend direction:
    - BULLISH: Price > EMA(50) × 1.01 (1% above)
    - BEARISH: Price < EMA(50) × 0.99 (1% below)
    - NEUTRAL: Price within ±1% of EMA(50)
    
    The 1% buffer zone prevents whipsaw trades during consolidation.
    
    Trading Rules:
    - BUY signals only allowed in BULLISH trend
    - SELL signals only allowed in BEARISH trend
    - No trading in NEUTRAL zone
    
    Usage:
        filter = TrendFilter(ema_period=50)
        trend = filter.get_trend_direction(candles)
        
        if trend == TrendDirection.BULLISH:
            allowed, reason = filter.is_trade_allowed('BUY', candles)
            if allowed:
                # Execute BUY trade
    """
    
    def __init__(self, ema_period: int = 50, buffer_pct: float = 0.01):
        """
        Initialize trend filter.
        
        Args:
            ema_period: EMA period for trend detection (default: 50)
            buffer_pct: Buffer percentage for neutral zone (default: 0.01 = 1%)
        
        Raises:
            ValueError: If ema_period < 1 or buffer_pct < 0
        """
        if ema_period < 1:
            raise ValueError("EMA period must be at least 1")
        
        if buffer_pct < 0 or buffer_pct > 0.05:
            raise ValueError("Buffer percentage must be between 0 and 0.05 (5%)")
        
        self.ema_period = ema_period
        self.buffer_pct = buffer_pct
        self.logger = logging.getLogger(__name__)
        
        self.logger.info(
            f"TrendFilter initialized: period={ema_period}, buffer={buffer_pct:.1%}"
        )
    
    def get_trend_direction(self, candles: List[Candle]) -> TrendDirection:
        """
        Determine trend direction using EMA(50).
        
        Args:
            candles: List of Candle entities (chronological order)
        
        Returns:
            TrendDirection enum (BULLISH, BEARISH, or NEUTRAL)
        
        Example:
            >>> filter = TrendFilter(ema_period=50)
            >>> candles = load_candles()
            >>> trend = filter.get_trend_direction(candles)
            >>> if trend == TrendDirection.BULLISH:
            ...     print("Market is in uptrend")
        """
        # Validate input
        if not candles or len(candles) < self.ema_period:
            self.logger.warning(
                f"Insufficient candles for trend detection: "
                f"need {self.ema_period}, got {len(candles) if candles else 0}"
            )
            return TrendDirection.NEUTRAL
        
        # Calculate EMA(50)
        ema_value = self._calculate_ema(candles, self.ema_period)
        
        if ema_value == 0:
            self.logger.warning("EMA calculation returned 0")
            return TrendDirection.NEUTRAL
        
        # Get current price
        current_price = candles[-1].close
        
        # Calculate thresholds with buffer
        bullish_threshold = ema_value * (1 + self.buffer_pct)
        bearish_threshold = ema_value * (1 - self.buffer_pct)
        
        # Determine trend
        if current_price > bullish_threshold:
            trend = TrendDirection.BULLISH
            spread_pct = ((current_price - ema_value) / ema_value) * 100
            self.logger.debug(
                f"BULLISH trend: price ${current_price:.2f} > EMA ${ema_value:.2f} "
                f"(+{spread_pct:.2f}%)"
            )
        elif current_price < bearish_threshold:
            trend = TrendDirection.BEARISH
            spread_pct = ((ema_value - current_price) / ema_value) * 100
            self.logger.debug(
                f"BEARISH trend: price ${current_price:.2f} < EMA ${ema_value:.2f} "
                f"(-{spread_pct:.2f}%)"
            )
        else:
            trend = TrendDirection.NEUTRAL
            self.logger.debug(
                f"NEUTRAL zone: price ${current_price:.2f} near EMA ${ema_value:.2f}"
            )
        
        return trend
    
    def is_trade_allowed(
        self,
        signal_direction: str,
        candles: List[Candle]
    ) -> Tuple[bool, str]:
        """
        Check if trade is allowed based on trend.
        
        Trading Rules:
        - BUY: Only allowed in BULLISH trend
        - SELL: Only allowed in BEARISH trend
        
        Args:
            signal_direction: 'BUY' or 'SELL'
            candles: List of candles
        
        Returns:
            Tuple of (allowed: bool, reason: str)
        
        Example:
            >>> filter = TrendFilter()
            >>> allowed, reason = filter.is_trade_allowed('BUY', candles)
            >>> if not allowed:
            ...     print(f"Trade rejected: {reason}")
        """
        # Validate signal direction
        if signal_direction not in ['BUY', 'SELL']:
            reason = f"Invalid signal direction: {signal_direction}"
            self.logger.error(reason)
            return False, reason
        
        # Get trend direction
        trend = self.get_trend_direction(candles)
        
        # Check if trade is allowed
        if signal_direction == 'BUY':
            if trend == TrendDirection.BULLISH:
                reason = f"BUY allowed: market in {trend.value} trend"
                self.logger.info(reason)
                return True, reason
            else:
                reason = f"BUY rejected: market in {trend.value} trend (need BULLISH)"
                self.logger.info(reason)
                return False, reason
        
        else:  # SELL
            if trend == TrendDirection.BEARISH:
                reason = f"SELL allowed: market in {trend.value} trend"
                self.logger.info(reason)
                return True, reason
            else:
                reason = f"SELL rejected: market in {trend.value} trend (need BEARISH)"
                self.logger.info(reason)
                return False, reason
    
    def get_trend_info(self, candles: List[Candle]) -> dict:
        """
        Get detailed trend information.
        
        Args:
            candles: List of candles
        
        Returns:
            Dictionary with trend details
        
        Example:
            >>> filter = TrendFilter()
            >>> info = filter.get_trend_info(candles)
            >>> print(f"Trend: {info['direction']}")
            >>> print(f"EMA(50): ${info['ema_value']:.2f}")
            >>> print(f"Spread: {info['spread_pct']:.2f}%")
        """
        if not candles or len(candles) < self.ema_period:
            return {
                'direction': TrendDirection.NEUTRAL.value,
                'ema_value': 0.0,
                'current_price': 0.0,
                'spread_pct': 0.0,
                'is_valid': False
            }
        
        ema_value = self._calculate_ema(candles, self.ema_period)
        current_price = candles[-1].close
        trend = self.get_trend_direction(candles)
        
        if ema_value > 0:
            spread_pct = ((current_price - ema_value) / ema_value) * 100
        else:
            spread_pct = 0.0
        
        return {
            'direction': trend.value,
            'ema_value': ema_value,
            'current_price': current_price,
            'spread_pct': spread_pct,
            'bullish_threshold': ema_value * (1 + self.buffer_pct),
            'bearish_threshold': ema_value * (1 - self.buffer_pct),
            'is_valid': True
        }
    
    def _calculate_ema(self, candles: List[Candle], period: int) -> float:
        """
        Calculate Exponential Moving Average.
        
        Uses standard EMA formula:
        - Multiplier = 2 / (period + 1)
        - EMA = (Price × Multiplier) + (Previous EMA × (1 - Multiplier))
        
        Args:
            candles: List of candles
            period: EMA period
        
        Returns:
            EMA value
        """
        if len(candles) < period:
            return 0.0
        
        # Get closing prices
        prices = [c.close for c in candles]
        
        # Calculate multiplier
        multiplier = 2 / (period + 1)
        
        # Initialize EMA with SMA of first 'period' prices
        ema = sum(prices[:period]) / period
        
        # Calculate EMA for remaining prices
        for price in prices[period:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))
        
        return ema
    
    def __repr__(self) -> str:
        """String representation"""
        return (
            f"TrendFilter(ema_period={self.ema_period}, "
            f"buffer={self.buffer_pct:.1%})"
        )
