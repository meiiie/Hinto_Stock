"""
Signals Router - Signal History and Lifecycle API

Provides endpoints for:
- Signal history (paginated)
- Pending signals
- Signal execution
- Signal details

**Feature: signal-lifecycle-tracking**
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Optional
import logging

from src.api.dependencies import get_signal_lifecycle_service, get_realtime_service
from src.application.services.signal_lifecycle_service import SignalLifecycleService
from src.application.services.realtime_service import RealtimeService

router = APIRouter(
    prefix="/signals",
    tags=["signals"]
)

logger = logging.getLogger(__name__)


@router.get("/history")
async def get_signal_history(
    days: int = Query(default=7, ge=1, le=90, description="Number of days"),
    page: int = Query(default=1, ge=1, description="Page number"),
    limit: int = Query(default=20, ge=1, le=100, description="Items per page"),
    lifecycle_service: SignalLifecycleService = Depends(get_signal_lifecycle_service)
):
    """
    Get paginated signal history.
    
    Returns all signals generated in the last N days with pagination.
    
    Args:
        days: Number of days to look back (default: 7, max: 90)
        page: Page number (1-indexed)
        limit: Items per page (max: 100)
        
    Returns:
        Paginated signal history with signal details
    """
    offset = (page - 1) * limit
    
    signals = lifecycle_service.get_signal_history(
        days=days,
        limit=limit,
        offset=offset
    )
    
    total = lifecycle_service.get_total_count(days=days)
    total_pages = (total + limit - 1) // limit
    
    return {
        "signals": [s.to_dict() for s in signals],
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": total_pages
        }
    }


@router.get("/pending")
async def get_pending_signals(
    lifecycle_service: SignalLifecycleService = Depends(get_signal_lifecycle_service)
):
    """
    Get all pending signals.
    
    Returns signals that are waiting for execution.
    
    Returns:
        List of pending signals
    """
    signals = lifecycle_service.get_pending_signals()
    
    return {
        "pending_signals": [s.to_dict() for s in signals],
        "count": len(signals)
    }


@router.get("/{signal_id}")
async def get_signal_by_id(
    signal_id: str,
    lifecycle_service: SignalLifecycleService = Depends(get_signal_lifecycle_service)
):
    """
    Get signal by ID.
    
    Args:
        signal_id: UUID of the signal
        
    Returns:
        Signal details
    """
    signal = lifecycle_service.get_signal_by_id(signal_id)
    
    if not signal:
        raise HTTPException(status_code=404, detail=f"Signal not found: {signal_id}")
    
    return signal.to_dict()


@router.post("/{signal_id}/execute")
async def execute_signal(
    signal_id: str,
    lifecycle_service: SignalLifecycleService = Depends(get_signal_lifecycle_service),
    realtime_service: RealtimeService = Depends(get_realtime_service)
):
    """
    Execute a pending signal.
    
    Creates an order from the signal and links them.
    
    Args:
        signal_id: UUID of the signal to execute
        
    Returns:
        Execution result with order_id
    """
    from src.api.dependencies import get_paper_trading_service
    
    # Get the signal
    signal = lifecycle_service.get_signal_by_id(signal_id)
    
    if not signal:
        raise HTTPException(status_code=404, detail=f"Signal not found: {signal_id}")
    
    if not signal.is_actionable:
        raise HTTPException(
            status_code=400, 
            detail=f"Signal is not actionable (status: {signal.status.value})"
        )
    
    # Get current price
    latest_candle = realtime_service.get_latest_data('1m')
    if not latest_candle or latest_candle.close <= 0:
        raise HTTPException(status_code=503, detail="Cannot determine current price")
    
    # Execute via PaperTradingService - get from realtime_service's paper_service
    paper_service = realtime_service.paper_service
    if not paper_service:
        raise HTTPException(status_code=503, detail="Paper trading service not available")
    
    try:
        # Execute the trade
        order_id = paper_service.execute_trade(signal=signal, symbol="BTCUSDT")
        
        if order_id:
            # Link signal to order
            lifecycle_service.mark_executed(signal_id, order_id)
            
            return {
                "success": True,
                "signal_id": signal_id,
                "order_id": order_id,
                "message": "Signal executed successfully"
            }
        else:
            return {
                "success": False,
                "signal_id": signal_id,
                "error": "Order execution failed (position limit or insufficient balance)"
            }
            
    except Exception as e:
        logger.error(f"Error executing signal {signal_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{signal_id}/mark-pending")
async def mark_signal_pending(
    signal_id: str,
    lifecycle_service: SignalLifecycleService = Depends(get_signal_lifecycle_service)
):
    """
    Mark a signal as pending (shown to user).
    
    Args:
        signal_id: UUID of the signal
        
    Returns:
        Updated signal
    """
    signal = lifecycle_service.mark_pending(signal_id)
    
    if not signal:
        raise HTTPException(status_code=404, detail=f"Signal not found or not actionable: {signal_id}")
    
    return signal.to_dict()


@router.post("/{signal_id}/expire")
async def expire_signal(
    signal_id: str,
    lifecycle_service: SignalLifecycleService = Depends(get_signal_lifecycle_service)
):
    """
    Manually expire a signal.
    
    Args:
        signal_id: UUID of the signal
        
    Returns:
        Updated signal
    """
    signal = lifecycle_service.mark_expired(signal_id)
    
    if not signal:
        raise HTTPException(status_code=404, detail=f"Signal not found or not actionable: {signal_id}")
    
    return signal.to_dict()


@router.post("/expire-stale")
async def expire_stale_signals(
    lifecycle_service: SignalLifecycleService = Depends(get_signal_lifecycle_service)
):
    """
    Expire all stale signals (older than TTL).
    
    Returns:
        Count of expired signals
    """
    count = lifecycle_service.expire_stale_signals()
    
    return {
        "expired_count": count,
        "message": f"Expired {count} stale signals"
    }


@router.get("/order/{order_id}")
async def get_signal_for_order(
    order_id: str,
    lifecycle_service: SignalLifecycleService = Depends(get_signal_lifecycle_service)
):
    """
    Get the signal that created an order.
    
    Args:
        order_id: UUID of the order
        
    Returns:
        Signal linked to the order
    """
    signal = lifecycle_service.get_signal_for_order(order_id)
    
    if not signal:
        raise HTTPException(status_code=404, detail=f"No signal found for order: {order_id}")
    
    return signal.to_dict()
