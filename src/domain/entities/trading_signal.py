"""
Trading Signal Entity

Defines the structure and types of trading signals.
Moved from application layer to domain layer to avoid circular dependencies.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any


class SignalType(Enum):
    """Trading signal types"""
    BUY = "buy"
    SELL = "sell"
    NEUTRAL = "neutral"


class ConfidenceLevel(Enum):
    """Confidence level categories"""
    HIGH = "high"      # >= 80%
    MEDIUM = "medium"  # 65-79%
    LOW = "low"        # < 65%


@dataclass
class TradingSignal:
    """
    Trading signal with metadata.
    
    Attributes:
        signal_type: Type of signal (BUY, SELL, NEUTRAL)
        confidence: Confidence level (0.0 to 1.0)
        timestamp: When signal was generated
        price: Price at signal generation
        indicators: Dict of indicator values
        reasons: List of reasons for the signal
        entry_price: Optional entry price for the trade
        tp_levels: Optional take profit levels dict with tp1, tp2, tp3
        stop_loss: Optional stop loss price
        position_size: Optional position size
        risk_reward_ratio: Optional risk/reward ratio
    """
    signal_type: SignalType
    confidence: float
    timestamp: datetime
    price: float
    indicators: Dict[str, Any] = field(default_factory=dict)
    reasons: List[str] = field(default_factory=list)
    # Enhanced signal fields (optional for backward compatibility)
    entry_price: Optional[float] = None
    tp_levels: Optional[Dict[str, float]] = None  # {'tp1': price, 'tp2': price, 'tp3': price}
    stop_loss: Optional[float] = None
    position_size: Optional[float] = None
    risk_reward_ratio: Optional[float] = None
    
    @property
    def confidence_level(self) -> 'ConfidenceLevel':
        """Get confidence level based on confidence score"""
        if self.confidence >= 0.80:
            return ConfidenceLevel.HIGH
        elif self.confidence >= 0.65:
            return ConfidenceLevel.MEDIUM
        else:
            return ConfidenceLevel.LOW
    
    def __str__(self) -> str:
        """String representation"""
        emoji = "🟢" if self.signal_type == SignalType.BUY else "🔴" if self.signal_type == SignalType.SELL else "⚪"
        return (
            f"{emoji} {self.signal_type.value.upper()} Signal "
            f"(Confidence: {self.confidence:.0%}) at ${self.price:,.2f}"
        )
