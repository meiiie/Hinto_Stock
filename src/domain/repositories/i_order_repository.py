from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.entities.paper_position import PaperPosition

class IOrderRepository(ABC):
    """Interface for Order/Position Repository"""
    
    @abstractmethod
    def save_order(self, position: PaperPosition) -> None:
        pass

    @abstractmethod
    def update_order(self, position: PaperPosition) -> None:
        pass

    @abstractmethod
    def get_order(self, position_id: str) -> Optional[PaperPosition]:
        pass

    @abstractmethod
    def get_active_orders(self) -> List[PaperPosition]:
        pass

    @abstractmethod
    def get_pending_orders(self) -> List[PaperPosition]:
        """Get all pending orders (PENDING)"""
        pass

    @abstractmethod
    def get_closed_orders(self, limit: int = 50) -> List[PaperPosition]:
        pass
    
    @abstractmethod
    def get_account_balance(self) -> float:
        pass

    @abstractmethod
    def update_account_balance(self, balance: float) -> None:
        pass
