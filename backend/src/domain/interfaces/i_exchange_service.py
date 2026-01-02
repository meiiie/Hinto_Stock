"""
IExchangeService Interface - Domain Layer

Abstract interface for exchange operations.
Enables switching between paper trading and live trading modes
without changing application logic.

This follows the Dependency Inversion Principle:
- Application layer depends on this interface
- Infrastructure layer provides concrete implementations
"""

from abc import ABC, abstractmethod
from typing import Optional

from ..entities.exchange_models import Position, OrderStatus


class IExchangeService(ABC):
    """
    Abstract interface for exchange operations.
    
    This interface defines the contract for exchange services,
    allowing the application to work with both paper trading
    and real exchange implementations interchangeably.
    
    Implementations:
        - PaperExchangeService: Simulated trading using local database
        - BinanceExchangeService: Real trading via Binance API
    
    Usage:
        # Application code doesn't know which implementation is used
        exchange_service: IExchangeService = container.get_exchange_service()
        position = await exchange_service.get_position("BTCUSDT")
    """
    
    @abstractmethod
    async def get_position(self, symbol: str) -> Optional[Position]:
        """
        Get open position for a symbol.
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            
        Returns:
            Position object if position exists, None otherwise
            
        Raises:
            ExchangeError: If API call fails (for real exchange)
        """
        pass
    
    @abstractmethod
    async def get_order_status(self, symbol: str, order_id: str) -> OrderStatus:
        """
        Get status of a specific order.
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            order_id: Unique order identifier
            
        Returns:
            OrderStatus with current order state
            
        Raises:
            ExchangeError: If order not found or API fails
        """
        pass
    
    @abstractmethod
    def get_exchange_type(self) -> str:
        """
        Get the type of exchange service.
        
        Returns:
            'paper' for paper trading, 'binance' for real exchange
        """
        pass


class ExchangeError(Exception):
    """
    Exception raised for exchange operation errors.
    
    Attributes:
        message: Error description
        code: Optional error code from exchange
    """
    
    def __init__(self, message: str, code: Optional[str] = None):
        self.message = message
        self.code = code
        super().__init__(self.message)
    
    def __str__(self) -> str:
        if self.code:
            return f"[{self.code}] {self.message}"
        return self.message
