from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class PaperPosition:
    """
    Represents a Futures Position (Long/Short).
    """
    id: str
    symbol: str
    side: str # 'LONG' or 'SHORT'
    status: str # 'OPEN' or 'CLOSED'
    entry_price: float
    quantity: float
    leverage: int
    margin: float
    liquidation_price: Optional[float]
    stop_loss: float
    take_profit: float
    open_time: datetime = field(default_factory=datetime.now)
    close_time: Optional[datetime] = None
    realized_pnl: float = 0.0
    exit_reason: Optional[str] = None
    
    # For Trailing Stop
    highest_price: float = 0.0 # For Long: Max price reached since open
    lowest_price: float = 0.0  # For Short: Min price reached since open

    @property
    def notional_value(self) -> float:
        return self.entry_price * self.quantity

    def calculate_unrealized_pnl(self, current_price: float) -> float:
        if self.side == 'LONG':
            return (current_price - self.entry_price) * self.quantity
        else:
            return (self.entry_price - current_price) * self.quantity
            
    def calculate_roe(self, current_price: float) -> float:
        pnl = self.calculate_unrealized_pnl(current_price)
        if self.margin == 0: return 0.0
        return (pnl / self.margin) * 100

    def to_dict(self) -> dict:
        """Convert to dictionary for API response."""
        return {
            "id": self.id,
            "symbol": self.symbol,
            "side": self.side,
            "status": self.status,
            "entry_price": self.entry_price,
            "quantity": self.quantity,
            "leverage": self.leverage,
            "margin": self.margin,
            "liquidation_price": self.liquidation_price,
            "stop_loss": self.stop_loss,
            "take_profit": self.take_profit,
            "open_time": self.open_time.isoformat() if self.open_time else None,
            "close_time": self.close_time.isoformat() if self.close_time else None,
            "realized_pnl": self.realized_pnl,
            "exit_reason": self.exit_reason,
            "highest_price": self.highest_price,
            "lowest_price": self.lowest_price
        }
