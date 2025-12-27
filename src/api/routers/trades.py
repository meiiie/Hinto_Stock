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
from datetime import datetime
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
    Get current portfolio status including pending orders.
    
    **Validates: Requirements 4.1, 4.4**
    
    Returns virtual balance, equity, unrealized PnL, open positions, and pending orders.
    """
    # Get current price from realtime service
    latest_candle = service.get_latest_data('1m')
    current_price = latest_candle.close if latest_candle else 0.0
    
    portfolio = paper_service.get_portfolio(current_price=current_price)
    
    # Get pending orders and add to response
    pending_orders = paper_service.repo.get_pending_orders()
    
    # Build response with pending orders included
    response = portfolio.to_dict()
    response['pending_orders'] = [
        {
            "id": order.id,
            "signal_id": order.id[:8],  # Short ID for display
            "symbol": order.symbol,
            "side": order.side,
            "entry_price": order.entry_price,
            "size": order.quantity,
            "stop_loss": order.stop_loss,
            "take_profits": [order.take_profit] if order.take_profit else [],
            "created_at": order.open_time.isoformat() if order.open_time else None,
            "expires_at": None,  # Would need TTL calculation
            "ttl_seconds": max(0, 45*60 - int((datetime.now() - order.open_time).total_seconds())) if order.open_time else 0
        }
        for order in pending_orders
    ]
    
    logger.info(f"📊 Portfolio: {len(response.get('open_positions', []))} positions, {len(pending_orders)} pending")
    
    return response


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


@router.get("/pending")
async def get_pending_orders(
    paper_service: PaperTradingService = Depends(get_paper_trading_service)
):
    """
    Get all pending (unfilled) orders.
    
    Returns orders with status='PENDING' waiting for price to match.
    """
    pending_orders = paper_service.repo.get_pending_orders()
    
    return {
        "count": len(pending_orders),
        "orders": [
            {
                "id": order.id,
                "symbol": order.symbol,
                "side": order.side,
                "status": order.status,
                "entry_price": order.entry_price,
                "quantity": order.quantity,
                "margin": order.margin,
                "stop_loss": order.stop_loss,
                "take_profit": order.take_profit,
                "open_time": order.open_time.isoformat() if order.open_time else None,
                "size_usd": order.quantity * order.entry_price
            }
            for order in pending_orders
        ]
    }


@router.get("/open")
async def get_open_positions(
    service: RealtimeService = Depends(get_realtime_service),
    paper_service: PaperTradingService = Depends(get_paper_trading_service)
):
    """
    Get all open (filled) positions.
    
    Returns active positions with unrealized PnL.
    """
    latest_candle = service.get_latest_data('1m')
    current_price = latest_candle.close if latest_candle else 0.0
    
    positions = paper_service.get_positions()
    
    return {
        "count": len(positions),
        "current_price": current_price,
        "positions": [
            {
                "id": pos.id,
                "symbol": pos.symbol,
                "side": pos.side,
                "status": pos.status,
                "entry_price": pos.entry_price,
                "quantity": pos.quantity,
                "margin": pos.margin,
                "stop_loss": pos.stop_loss,
                "take_profit": pos.take_profit,
                "open_time": pos.open_time.isoformat() if pos.open_time else None,
                "size_usd": pos.quantity * pos.entry_price,
                "current_value": pos.quantity * current_price,
                "unrealized_pnl": (current_price - pos.entry_price) * pos.quantity if pos.side == 'LONG' else (pos.entry_price - current_price) * pos.quantity,
                "roe_pct": pos.calculate_roe(current_price) if hasattr(pos, 'calculate_roe') else 0.0
            }
            for pos in positions
        ]
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


@router.post("/execute/{position_id}")
async def execute_pending(
    position_id: str,
    service: RealtimeService = Depends(get_realtime_service),
    paper_service: PaperTradingService = Depends(get_paper_trading_service)
):
    """
    Manually execute a PENDING order at CURRENT market price.
    
    This is a MARKET ORDER - fills immediately at current price,
    not at the original limit entry price.
    
    Use case: User sees PENDING order and wants to enter NOW
    instead of waiting for limit price to be hit.
    
    Args:
        position_id: ID of the PENDING order to execute
        
    Returns:
        Execution result with fill price
    """
    from datetime import datetime
    
    # Get current price
    latest_candle = service.get_latest_data('1m')
    if not latest_candle or latest_candle.close <= 0:
        return {"success": False, "error": "Cannot determine current price"}
    
    current_price = latest_candle.close
    
    # Find the pending order
    pending_orders = paper_service.repo.get_pending_orders()
    target_order = None
    
    for order in pending_orders:
        if order.id == position_id:
            target_order = order
            break
    
    if not target_order:
        return {
            "success": False, 
            "error": f"PENDING order not found: {position_id}"
        }
    
    # Execute at CURRENT price (market order)
    original_entry = target_order.entry_price
    target_order.entry_price = current_price  # Fill at market price
    target_order.status = 'OPEN'
    target_order.open_time = datetime.now()
    
    # Recalculate liquidation price
    if target_order.side == 'LONG':
        target_order.liquidation_price = current_price - (target_order.margin / target_order.quantity)
    else:
        target_order.liquidation_price = current_price + (target_order.margin / target_order.quantity)
    
    paper_service.repo.update_order(target_order)
    
    logger.info(
        f"✅ MARKET FILLED {target_order.side} {target_order.symbol} @ {current_price:.2f} "
        f"(was PENDING @ {original_entry:.2f})"
    )
    
    # Trigger state machine callback
    if paper_service.on_order_filled:
        try:
            paper_service.on_order_filled(target_order.id)
        except Exception as e:
            logger.error(f"Error in on_order_filled callback: {e}")
    
    return {
        "success": True,
        "message": f"Order filled at market price",
        "order_id": target_order.id,
        "side": target_order.side,
        "original_entry": original_entry,
        "fill_price": current_price,
        "size_usd": target_order.quantity * current_price
    }


@router.post("/simulate")
async def simulate_signal(
    signal_data: dict,
    service: RealtimeService = Depends(get_realtime_service),
    paper_service: PaperTradingService = Depends(get_paper_trading_service)
):
    """
    Simulate a BUY/SELL signal for testing purposes.
    
    This is a DEBUG endpoint to test the trade execution flow
    without waiting for real signals from the strategy.
    
    Args:
        signal_data: {"signal_type": "BUY" | "SELL"}
        
    Returns:
        Trade execution result
    """
    from datetime import datetime
    from src.domain.entities.trading_signal import TradingSignal, SignalType
    
    signal_type = signal_data.get("signal_type", "BUY").upper()
    
    if signal_type not in ["BUY", "SELL"]:
        return {"success": False, "error": "Invalid signal type. Use BUY or SELL"}
    
    # Get current price
    latest_candle = service.get_latest_data('1m')
    if not latest_candle or latest_candle.close <= 0:
        return {"success": False, "error": "Cannot determine current price"}
    
    current_price = latest_candle.close
    
    # Calculate SL/TP based on default risk settings
    # Default: 1.5% risk, 1.5 R:R ratio
    risk_percent = 0.015  # 1.5%
    rr_ratio = 1.5
    
    if signal_type == "BUY":
        stop_loss = current_price * (1 - risk_percent)
        take_profit = current_price * (1 + risk_percent * rr_ratio)
        sig_type = SignalType.BUY
    else:
        stop_loss = current_price * (1 + risk_percent)
        take_profit = current_price * (1 - risk_percent * rr_ratio)
        sig_type = SignalType.SELL
    
    # Create TradingSignal object (required by execute_trade)
    trading_signal = TradingSignal(
        signal_type=sig_type,
        confidence=0.75,  # Default confidence for test
        generated_at=datetime.now(),  # FIX: Use correct field name
        price=current_price,
        entry_price=current_price,
        stop_loss=stop_loss,
        tp_levels={'tp1': take_profit},
        indicators={},
        reasons=[f"SIMULATED_{signal_type}_SIGNAL"]
    )
    
    # Execute the simulated trade
    try:
        position_id = paper_service.execute_trade(
            signal=trading_signal,
            symbol="BTCUSDT"
        )
        
        if position_id:
            return {
                "success": True,
                "trade_id": position_id,
                "entry_price": current_price,
                "stop_loss": stop_loss,
                "take_profit": take_profit,
                "side": "LONG" if signal_type == "BUY" else "SHORT"
            }
        else:
            return {"success": False, "error": "Trade execution returned None (position limit or insufficient balance)"}
            
    except Exception as e:
        logger.error(f"Simulate signal error: {e}")
        return {"success": False, "error": str(e)}


@router.get("/equity-curve")
async def get_equity_curve(
    days: int = Query(default=7, ge=1, le=365, description="Number of days"),
    resolution: str = Query(default="trade", description="Resolution: 'trade' (per-trade) or 'daily'"),
    paper_service: PaperTradingService = Depends(get_paper_trading_service)
):
    """
    Get equity curve data for charting.
    
    **Validates: Requirements 7.3 - Performance visualization**
    
    Returns equity values based on trade history.
    Resolution can be 'trade' (per-trade, recommended for 15m strategy) or 'daily'.
    
    Args:
        days: Number of days to include (default: 7)
        resolution: 'trade' for per-trade updates, 'daily' for daily aggregation
        
    Returns:
        List of {time, equity, pnl, trade_id?} points
    """
    from datetime import datetime, timedelta
    
    # Get all trades for the period
    result = paper_service.get_trade_history(page=1, limit=1000)
    trades = result.trades
    
    # Calculate equity curve
    initial_balance = 10000.0
    equity_curve = []
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    if resolution == "trade":
        # TRADE-BY-TRADE RESOLUTION (New - for 15m strategy monitoring)
        # Each point represents equity after a trade closes
        
        # Filter trades within the period and sort by exit_time
        period_trades = [
            t for t in trades 
            if t.exit_time and t.exit_time >= start_date
        ]
        period_trades.sort(key=lambda t: t.exit_time)
        
        # Start with initial balance point
        equity_curve.append({
            "time": start_date.strftime('%Y-%m-%dT%H:%M:%S'),
            "equity": initial_balance,
            "pnl": 0.0,
            "trade_id": None
        })
        
        cumulative_pnl = 0.0
        
        # Add a point for each closed trade
        for trade in period_trades:
            if trade.pnl is not None:
                cumulative_pnl += trade.pnl
                current_equity = initial_balance + cumulative_pnl
                
                equity_curve.append({
                    "time": trade.exit_time.strftime('%Y-%m-%dT%H:%M:%S'),
                    "equity": round(current_equity, 2),
                    "pnl": round(trade.pnl, 2),
                    "trade_id": trade.id,
                    "side": trade.side,
                    "result": "WIN" if trade.pnl > 0 else "LOSS"
                })
        
        # Add current point (latest equity)
        if equity_curve:
            equity_curve.append({
                "time": end_date.strftime('%Y-%m-%dT%H:%M:%S'),
                "equity": equity_curve[-1]["equity"],
                "pnl": 0.0,
                "trade_id": None
            })
    else:
        # DAILY RESOLUTION (Original)
        current_equity = initial_balance
        cumulative_pnl = 0.0
        
        # Group trades by date
        trades_by_date = {}
        for trade in trades:
            if trade.exit_time:
                trade_date = trade.exit_time.strftime('%Y-%m-%d')
                if trade_date not in trades_by_date:
                    trades_by_date[trade_date] = []
                trades_by_date[trade_date].append(trade)
        
        # Build equity curve day by day
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            
            # Add PnL from trades closed on this day
            daily_pnl = 0.0
            if date_str in trades_by_date:
                for trade in trades_by_date[date_str]:
                    if trade.pnl is not None:
                        daily_pnl += trade.pnl
            
            cumulative_pnl += daily_pnl
            current_equity = initial_balance + cumulative_pnl
            
            equity_curve.append({
                "time": date_str,
                "equity": round(current_equity, 2),
                "pnl": round(daily_pnl, 2)
            })
            
            current_date += timedelta(days=1)
    
    # Include current portfolio balance for consistency check
    return {
        "equity_curve": equity_curve,
        "resolution": resolution,
        "initial_balance": initial_balance,
        "current_equity": equity_curve[-1]["equity"] if equity_curve else initial_balance
    }
