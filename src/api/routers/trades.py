"""
Trades Router - Trade History and Performance API

**Feature: desktop-trading-dashboard**
**Validates: Requirements 7.1, 7.2, 7.3**

Provides:
- Paginated trade history endpoint
- Performance metrics endpoint
- Portfolio status endpoint
"""

from fastapi import APIRouter, Depends, Query
from typing import Optional
import logging

from src.api.dependencies import get_paper_trading_service, get_realtime_service
from src.application.services.paper_trading_service import PaperTradingService
from src.application.services.realtime_service import RealtimeService

router = APIRouter(
    prefix="/trades",
    tags=["trades"]
)

logger = logging.getLogger(__name__)


@router.get("/history")
async def get_trade_history(
    page: int = Query(default=1, ge=1, description="Page number (1-indexed)"),
    limit: int = Query(default=20, ge=1, le=100, description="Items per page"),
    paper_service: PaperTradingService = Depends(get_paper_trading_service)
):
    """
    Get paginated trade history.
    
    **Validates: Requirements 7.1, 7.2**
    
    Returns trades sorted by entry_time descending with pagination info.
    
    Args:
        page: Page number (1-indexed)
        limit: Items per page (max 100)
        
    Returns:
        Paginated trade history with all required fields
    """
    result = paper_service.get_trade_history(page=page, limit=limit)
    return result.to_dict()


@router.get("/performance")
async def get_performance_metrics(
    days: int = Query(default=7, ge=1, le=365, description="Number of days to analyze"),
    paper_service: PaperTradingService = Depends(get_paper_trading_service)
):
    """
    Get performance metrics for the specified period.
    
    **Validates: Requirements 7.3**
    
    Calculates win_rate, profit_factor, max_drawdown, total_pnl.
    
    Args:
        days: Number of days to analyze (default: 7)
        
    Returns:
        Performance metrics
    """
    metrics = paper_service.calculate_performance(days=days)
    return metrics.to_dict()


@router.get("/portfolio")
async def get_portfolio(
    service: RealtimeService = Depends(get_realtime_service),
    paper_service: PaperTradingService = Depends(get_paper_trading_service)
):
    """
    Get current portfolio status.
    
    **Validates: Requirements 4.1, 4.4**
    
    Returns virtual balance, equity, unrealized PnL, and open positions.
    """
    # Get current price from realtime service
    latest_candle = service.get_latest_data('1m')
    current_price = latest_candle.close if latest_candle else 0.0
    
    portfolio = paper_service.get_portfolio(current_price=current_price)
    return portfolio.to_dict()


@router.post("/close/{position_id}")
async def close_position(
    position_id: str,
    service: RealtimeService = Depends(get_realtime_service),
    paper_service: PaperTradingService = Depends(get_paper_trading_service)
):
    """
    Manually close a position.
    
    Args:
        position_id: ID of the position to close
        
    Returns:
        Success status
    """
    latest_candle = service.get_latest_data('1m')
    current_price = latest_candle.close if latest_candle else 0.0
    
    if current_price <= 0:
        return {"success": False, "error": "Cannot determine current price"}
    
    success = paper_service.close_position_by_id(position_id, current_price, "MANUAL_CLOSE")
    
    return {
        "success": success,
        "message": "Position closed" if success else "Position not found or already closed"
    }


@router.post("/reset")
async def reset_account(
    paper_service: PaperTradingService = Depends(get_paper_trading_service)
):
    """
    Reset paper trading account.
    
    Clears all trades and resets balance to initial value.
    """
    paper_service.reset_account()
    return {"success": True, "message": "Account reset to $10,000"}
