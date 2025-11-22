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
