"""
BinanceExchangeService - Infrastructure Layer

Real Binance exchange implementation of IExchangeService.
Makes actual API calls to Binance Futures for position and order data.

NOTE: This service is for REAL trading mode. Use with caution!
"""

import logging
import requests
from typing import Optional, TYPE_CHECKING

from ...domain.interfaces.i_exchange_service import IExchangeService, ExchangeError
from ...domain.entities.exchange_models import Position, OrderStatus

if TYPE_CHECKING:
    from ..api.binance_rest_client import BinanceRestClient


class BinanceExchangeService(IExchangeService):
    """
    Real Binance exchange implementation of IExchangeService.
    
    Makes actual API calls to Binance Futures API for:
    - Position verification
    - Order status checking
    
    WARNING: This service interacts with real exchange.
    Only use in production with proper API credentials.
    
    Usage:
        rest_client = BinanceRestClient()
        binance_service = BinanceExchangeService(
            rest_client=rest_client,
            api_key="your_api_key",
            api_secret="your_api_secret"
        )
        
        position = await binance_service.get_position("BTCUSDT")
    """
    
    # Binance Futures API endpoints
    FUTURES_BASE_URL = "https://fapi.binance.com"
    
    def __init__(
        self,
        rest_client: 'BinanceRestClient',
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        timeout: int = 10
    ):
        """
        Initialize BinanceExchangeService.
        
        Args:
            rest_client: BinanceRestClient for market data
            api_key: Binance API key (required for authenticated endpoints)
            api_secret: Binance API secret (required for authenticated endpoints)
            timeout: Request timeout in seconds
        """
        self._rest_client = rest_client
        self._api_key = api_key
        self._api_secret = api_secret
        self._timeout = timeout
        self.logger = logging.getLogger(__name__)
        
        if not api_key or not api_secret:
            self.logger.warning(
                "BinanceExchangeService initialized without API credentials. "
                "Position verification will be limited."
            )
    
    async def get_position(self, symbol: str) -> Optional[Position]:
        """
        Get open position for symbol from Binance Futures API.
        
        Calls GET /fapi/v2/positionRisk to get position information.
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            
        Returns:
            Position if found, None otherwise
            
        Raises:
            ExchangeError: If API call fails
        """
        if not self._api_key or not self._api_secret:
            self.logger.warning(
                "Cannot verify position without API credentials. "
                "Assuming no position exists."
            )
            return None
        
        try:
            # Call Binance Futures API
            positions_data = self._get_position_risk(symbol)
            
            if not positions_data:
                self.logger.debug(f"No position data returned for {symbol}")
                return None
            
            # Find position with non-zero amount
            for pos_data in positions_data:
                position_amt = float(pos_data.get('positionAmt', 0))
                
                if position_amt != 0:
                    # Convert to Position entity
                    position = Position(
                        symbol=pos_data.get('symbol', symbol),
                        side='LONG' if position_amt > 0 else 'SHORT',
                        size=abs(position_amt),
                        entry_price=float(pos_data.get('entryPrice', 0)),
                        unrealized_pnl=float(pos_data.get('unRealizedProfit', 0))
                    )
                    
                    self.logger.info(
                        f"Found Binance position: {position.side} "
                        f"{position.size} @ {position.entry_price}"
                    )
                    return position
            
            self.logger.debug(f"No open position found for {symbol}")
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting Binance position: {e}")
            raise ExchangeError(f"Failed to get Binance position: {e}")
    
    async def get_order_status(self, symbol: str, order_id: str) -> OrderStatus:
        """
        Get status of a specific order from Binance Futures API.
        
        Calls GET /fapi/v1/order to get order information.
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            order_id: Unique order identifier
            
        Returns:
            OrderStatus with current order state
            
        Raises:
            ExchangeError: If order not found or API fails
        """
        if not self._api_key or not self._api_secret:
            raise ExchangeError(
                "Cannot check order status without API credentials",
                code="NO_CREDENTIALS"
            )
        
        try:
            order_data = self._get_order(symbol, order_id)
            
            if not order_data:
                raise ExchangeError(
                    f"Order {order_id} not found",
                    code="ORDER_NOT_FOUND"
                )
            
            return OrderStatus(
                order_id=str(order_data.get('orderId', order_id)),
                status=order_data.get('status', 'NEW'),
                filled_qty=float(order_data.get('executedQty', 0)),
                avg_price=float(order_data.get('avgPrice', 0)) or None
            )
            
        except ExchangeError:
            raise
        except Exception as e:
            self.logger.error(f"Error getting order status: {e}")
            raise ExchangeError(f"Failed to get order status: {e}")
    
    def get_exchange_type(self) -> str:
        """
        Get the type of exchange service.
        
        Returns:
            'binance' to indicate real Binance exchange
        """
        return "binance"
    
    def _get_position_risk(self, symbol: str) -> list:
        """
        Call Binance Futures API to get position risk.
        
        This is a placeholder - actual implementation requires
        HMAC signature for authenticated requests.
        
        Args:
            symbol: Trading pair
            
        Returns:
            List of position data dicts
        """
        # TODO: Implement actual signed request
        # For now, return empty list (no positions)
        self.logger.warning(
            "Binance position verification not fully implemented. "
            "Returning empty positions."
        )
        return []
    
    def _get_order(self, symbol: str, order_id: str) -> Optional[dict]:
        """
        Call Binance Futures API to get order details.
        
        This is a placeholder - actual implementation requires
        HMAC signature for authenticated requests.
        
        Args:
            symbol: Trading pair
            order_id: Order ID
            
        Returns:
            Order data dict or None
        """
        # TODO: Implement actual signed request
        self.logger.warning(
            "Binance order query not fully implemented. "
            "Returning None."
        )
        return None
    
    def __repr__(self) -> str:
        return f"BinanceExchangeService(has_credentials={bool(self._api_key)})"
