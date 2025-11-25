"""
Market Router - WebSocket and REST endpoints for market data

**Feature: desktop-trading-dashboard**
**Validates: Requirements 1.1, 1.2, 5.2, 5.3, 5.4**

Provides:
- WebSocket streaming for real-time candle data
- Historical data API with indicators
- Graceful disconnect handling
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from typing import List, Optional
import json
import asyncio
import logging

from src.api.dependencies import get_realtime_service
from src.api.websocket_manager import get_websocket_manager, WebSocketManager
from src.application.services.realtime_service import RealtimeService

router = APIRouter(
    prefix="/ws",
    tags=["market"]
)

logger = logging.getLogger(__name__)


# Track if we've subscribed to the RealtimeService
_service_subscribed = False


def _setup_service_bridge(service: RealtimeService, manager: WebSocketManager) -> None:
    """
    Setup bridge between RealtimeService and WebSocketManager.
    
    This creates a Pub/Sub pattern where:
    - Publisher: RealtimeService (Trading Engine)
    - Subscriber: WebSocket clients via WebSocketManager
    """
    global _service_subscribed
    
    if _service_subscribed:
        return
    
    def on_update():
        """Bridge callback - called when RealtimeService has new data."""
        try:
            # Get latest data from service
            data = service.get_latest_indicators(timeframe='1m')
            if not data:
                return
            
            # Add candle info
            latest_candle = service.get_latest_data('1m')
            if latest_candle:
                data['type'] = 'candle'
                data['symbol'] = service.symbol
                data['timestamp'] = latest_candle.timestamp.isoformat()
                data['open'] = latest_candle.open
                data['high'] = latest_candle.high
                data['low'] = latest_candle.low
                data['close'] = latest_candle.close
                data['volume'] = latest_candle.volume
            
            # Add signal info if available
            signal = service.get_current_signals()
            if signal:
                data['signal'] = {
                    'type': signal.signal_type.value,
                    'price': signal.price,
                    'entry_price': signal.entry_price,
                    'stop_loss': signal.stop_loss,
                    'take_profit': signal.take_profit,
                    'confidence': signal.confidence,
                    'risk_reward_ratio': signal.risk_reward_ratio,
                    'reason': signal.reason
                }
            
            # Schedule broadcast (fire and forget)
            # Broadcast to all clients subscribed to this symbol
            asyncio.create_task(manager.broadcast(data, symbol=service.symbol))
            
        except Exception as e:
            logger.error(f"Error in service bridge: {e}")
    
    def on_signal(signal):
        """Bridge callback for trading signals."""
        try:
            signal_data = {
                'type': 'signal',
                'symbol': service.symbol,
                'signal': {
                    'type': signal.signal_type.value,
                    'price': signal.price,
                    'entry_price': signal.entry_price,
                    'stop_loss': signal.stop_loss,
                    'take_profit': signal.take_profit,
                    'confidence': signal.confidence,
                    'risk_reward_ratio': signal.risk_reward_ratio,
                    'reason': signal.reason,
                    'timestamp': signal.timestamp.isoformat() if hasattr(signal, 'timestamp') else None
                }
            }
            
            asyncio.create_task(manager.broadcast(signal_data, symbol=service.symbol))
            
        except Exception as e:
            logger.error(f"Error broadcasting signal: {e}")
    
    # Subscribe to service events
    service.subscribe_updates(on_update)
    service.subscribe_signals(on_signal)
    
    _service_subscribed = True
    logger.info("Service bridge established - RealtimeService → WebSocketManager")


@router.websocket("/stream/{symbol}")
async def websocket_stream(
    websocket: WebSocket,
    symbol: str,
    service: RealtimeService = Depends(get_realtime_service)
):
    """
    WebSocket endpoint for real-time market data streaming.
    
    **Validates: Requirements 1.1, 1.2, 5.2, 5.3**
    
    Features:
    - Real-time candle data with indicators (VWAP, BB, StochRSI)
    - Signal notifications
    - Graceful disconnect handling
    
    Args:
        symbol: Trading pair symbol (e.g., 'btcusdt')
    """
    manager = get_websocket_manager()
    
    # Setup service bridge if not done
    _setup_service_bridge(service, manager)
    
    # Connect client
    connection = await manager.connect(websocket, symbol.lower())
    
    try:
        # Send initial data snapshot
        initial_data = {
            'type': 'snapshot',
            'symbol': symbol.lower(),
            'data': service.get_latest_indicators(timeframe='1m')
        }
        
        latest_candle = service.get_latest_data('1m')
        if latest_candle:
            initial_data['candle'] = {
                'timestamp': latest_candle.timestamp.isoformat(),
                'open': latest_candle.open,
                'high': latest_candle.high,
                'low': latest_candle.low,
                'close': latest_candle.close,
                'volume': latest_candle.volume
            }
        
        await websocket.send_text(json.dumps(initial_data))
        
        # Keep connection alive
        while True:
            try:
                # Wait for client messages (ping/pong, subscription changes)
                data = await websocket.receive_text()
                
                # Handle client commands
                try:
                    msg = json.loads(data)
                    msg_type = msg.get('type')
                    
                    if msg_type == 'ping':
                        await websocket.send_text(json.dumps({'type': 'pong'}))
                    
                    elif msg_type == 'subscribe':
                        # Client wants to change subscription
                        new_symbol = msg.get('symbol', symbol).lower()
                        if new_symbol != connection.symbol:
                            # Disconnect from old, connect to new
                            await manager.disconnect(connection)
                            connection = await manager.connect(websocket, new_symbol)
                            logger.info(f"Client resubscribed to {new_symbol}")
                    
                except json.JSONDecodeError:
                    # Not JSON - might be a simple ping
                    pass
                    
            except asyncio.TimeoutError:
                # No message received - that's fine, just keep waiting
                continue
                
    except WebSocketDisconnect:
        # Client disconnected gracefully
        logger.debug(f"Client {connection.client_id} disconnected gracefully")
        
    except Exception as e:
        # Unexpected error - log but don't crash
        logger.error(f"WebSocket error for {connection.client_id}: {e}")
        
    finally:
        # Always clean up connection
        await manager.disconnect(connection)


@router.websocket("/market/{symbol}")
async def websocket_market_legacy(
    websocket: WebSocket,
    symbol: str,
    service: RealtimeService = Depends(get_realtime_service)
):
    """
    Legacy WebSocket endpoint (for backward compatibility).
    Redirects to /stream/{symbol}.
    """
    await websocket_stream(websocket, symbol, service)


@router.get("/history/{symbol}")
async def get_market_history(
    symbol: str,
    timeframe: str = Query(default='15m', regex='^(1m|15m|1h)$'),
    limit: int = Query(default=100, ge=1, le=1000),
    service: RealtimeService = Depends(get_realtime_service)
):
    """
    Get historical market data with pre-calculated indicators.
    
    **Validates: Requirements 5.4, 2.1**
    
    Args:
        symbol: Trading pair symbol
        timeframe: Candle timeframe (1m, 15m, 1h)
        limit: Number of candles to return (max 1000)
        
    Returns:
        List of candles with VWAP and Bollinger Bands
    """
    return service.get_historical_data_with_indicators(timeframe, limit)


@router.get("/status")
async def get_websocket_status():
    """
    Get WebSocket manager status and statistics.
    
    Returns:
        Connection statistics and active subscriptions
    """
    manager = get_websocket_manager()
    return manager.get_statistics()


@router.get("/connections")
async def get_active_connections():
    """
    Get list of active WebSocket connections.
    
    Returns:
        List of connection info
    """
    manager = get_websocket_manager()
    return manager.get_all_connections_info()
