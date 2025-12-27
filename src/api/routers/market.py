"""
Market Router - WebSocket and REST endpoints for market data

**Feature: desktop-trading-dashboard**
**Validates: Requirements 1.1, 1.2, 5.2, 5.3, 5.4**

Provides:
- WebSocket streaming for real-time candle data (via EventBus)
- Historical data API with indicators
- Graceful disconnect handling

Architecture:
- EventBus handles all broadcasting (decoupled from this router)
- This router only manages WebSocket connections and initial snapshots
- No more sync/async callback issues!
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from typing import List, Optional
import json
import asyncio
import logging

from src.api.dependencies import get_realtime_service, get_realtime_service_for_symbol, get_market_data_repository
from src.api.websocket_manager import get_websocket_manager, WebSocketManager
from src.api.event_bus import get_event_bus
from src.application.services.realtime_service import RealtimeService
from src.infrastructure.persistence.sqlite_market_data_repository import SQLiteMarketDataRepository

router = APIRouter(
    prefix="/ws",
    tags=["market"]
)

# Additional router for /market prefix (for frontend compatibility)
market_router = APIRouter(
    prefix="/market",
    tags=["market-rest"]
)

logger = logging.getLogger(__name__)


# NOTE: Service bridge has been REMOVED!
# Broadcasting is now handled by EventBus (see event_bus.py and main.py lifespan)
# This eliminates the async/sync callback mismatch problem


@router.websocket("/stream/{symbol}")
async def websocket_stream(
    websocket: WebSocket,
    symbol: str,
):
    """
    WebSocket endpoint for real-time market data streaming.
    
    **Validates: Requirements 1.1, 1.2, 5.2, 5.3**
    
    Features:
    - Real-time candle data with indicators (VWAP, BB, StochRSI)
    - Signal notifications (via EventBus broadcast)
    - Graceful disconnect handling
    
    Architecture:
    - Client connects here and receives initial snapshot
    - Subsequent updates are pushed via EventBus broadcast worker
    - No direct coupling between this endpoint and RealtimeService callbacks
    
    Args:
        symbol: Trading pair symbol (e.g., 'btcusdt')
    """
    # SOTA Multi-Token FIX: Get service for the requested symbol, NOT hardcoded btcusdt
    service = get_realtime_service_for_symbol(symbol)
    manager = get_websocket_manager()
    
    # Connect client to WebSocketManager
    # EventBus broadcast worker will automatically send updates to all connected clients
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
        
        # Include current signal if available
        current_signal = service.get_current_signals()
        if current_signal and current_signal.signal_type.value != 'neutral':
            initial_data['signal'] = {
                'type': current_signal.signal_type.value,
                'price': current_signal.price,
                'entry_price': getattr(current_signal, 'entry_price', current_signal.price),
                'stop_loss': getattr(current_signal, 'stop_loss', None),
                'take_profit': getattr(current_signal, 'take_profit', None),
                'confidence': current_signal.confidence,
                'risk_reward_ratio': getattr(current_signal, 'risk_reward_ratio', None),
                'timestamp': current_signal.timestamp.isoformat() if hasattr(current_signal, 'timestamp') else None
            }
        
        await websocket.send_text(json.dumps(initial_data))
        logger.info(f"Client {connection.client_id} connected, initial snapshot sent")
        
        # Keep connection alive and handle client messages
        # Actual data updates are pushed by EventBus broadcast worker
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
):
    """
    Legacy WebSocket endpoint (for backward compatibility).
    Redirects to /stream/{symbol}.
    """
    # SOTA Multi-Token FIX: Get service for the requested symbol
    service = get_realtime_service_for_symbol(symbol)
    await websocket_stream(websocket, symbol)


@router.get("/history/{symbol}")
async def get_market_history(
    symbol: str,
    timeframe: str = Query(default='15m', pattern='^(1m|15m|1h)$'),
    limit: int = Query(default=100, ge=1, le=1000),
    repo: SQLiteMarketDataRepository = Depends(get_market_data_repository)
):
    """
    Get historical market data with hybrid data source.
    
    SOTA Multi-Token: Returns data for the requested symbol.
    
    **Validates: Requirements 5.4, 2.1**
    
    Args:
        symbol: Trading pair symbol (e.g., btcusdt, ethusdt)
        timeframe: Candle timeframe (1m, 15m, 1h)
        limit: Number of candles to return (max 1000)
        
    Returns:
        List of candles with VWAP and Bollinger Bands
    """
    # SOTA: Get service for the specific symbol
    service = get_realtime_service_for_symbol(symbol)
    
    # Step 1: Try SQLite first (SOTA Multi-Symbol: per-symbol tables)
    try:
        sqlite_candles = repo.get_latest_candles(symbol.lower(), timeframe, limit)
        if len(sqlite_candles) >= limit * 0.8:  # 80% threshold
            logger.debug(f"📦 SQLite hit: {len(sqlite_candles)} candles for {symbol}/{timeframe}")
            # Sort ascending (SQLite returns DESC)
            sorted_candles = sorted(sqlite_candles, key=lambda c: c.candle.timestamp)
            
            # SOTA FIX: Calculate indicators for SQLite data (same as Binance path)
            # This ensures VWAP/BB display from history start, not just realtime
            candles = [c.candle for c in sorted_candles]
            return service.get_historical_data_with_indicators(timeframe, limit, candles=candles)
    except Exception as e:
        logger.warning(f"SQLite query failed: {e}")
    
    # Step 2: Fallback to service (Binance REST)
    logger.debug(f"📡 SQLite miss, falling back to Binance for {symbol}/{timeframe}")
    return service.get_historical_data_with_indicators(timeframe, limit)


@router.get("/status")
async def get_websocket_status():
    """
    Get WebSocket manager status and statistics.
    
    Returns:
        Connection statistics and active subscriptions
    """
    manager = get_websocket_manager()
    event_bus = get_event_bus()
    
    return {
        'websocket': manager.get_statistics(),
        'event_bus': event_bus.get_statistics()
    }


@router.get("/connections")
async def get_active_connections():
    """
    Get list of active WebSocket connections.
    
    Returns:
        List of connection info
    """
    manager = get_websocket_manager()
    return manager.get_all_connections_info()


# ============ /market/* endpoints for frontend compatibility ============

@market_router.get("/history")
async def get_market_history_rest(
    symbol: str = Query(default='btcusdt'),
    timeframe: str = Query(default='15m', pattern='^(1m|15m|1h)$'),
    limit: int = Query(default=100, ge=1, le=1000),
    repo: SQLiteMarketDataRepository = Depends(get_market_data_repository)
):
    """
    Get historical market data (REST endpoint for frontend).
    
    SOTA Phase 3: SQLite first, Binance fallback.
    
    SOTA Multi-Token: Now correctly uses symbol-specific service.
    
    Used by useMarketData hook for data gap filling after reconnect.
    
    Args:
        symbol: Trading pair symbol (default: btcusdt)
        timeframe: Candle timeframe (default: 15m)
        limit: Number of candles to return (max 1000)
        
    Returns:
        List of candles with indicators
    """
    # SOTA Multi-Token FIX: Get service for the requested symbol
    service = get_realtime_service_for_symbol(symbol)
    
    # Step 1: Try SQLite first (SOTA Multi-Symbol: per-symbol tables)
    try:
        sqlite_candles = repo.get_latest_candles(symbol.lower(), timeframe, limit)
        if len(sqlite_candles) >= limit * 0.8:  # 80% threshold
            logger.debug(f"📦 SQLite hit: {len(sqlite_candles)} candles for {timeframe}")
            sorted_candles = sorted(sqlite_candles, key=lambda c: c.candle.timestamp)
            
            # SOTA FIX: Calculate indicators for SQLite data
            candles = [c.candle for c in sorted_candles]
            return service.get_historical_data_with_indicators(timeframe, limit, candles=candles)
    except Exception as e:
        logger.warning(f"SQLite query failed: {e}")
    
    # Step 2: Fallback to service (Binance REST)
    logger.debug(f"📡 SQLite miss, falling back to Binance for {timeframe}")
    return service.get_historical_data_with_indicators(timeframe, limit)


@market_router.get("/symbols")
async def get_supported_symbols():
    """
    Get list of supported trading symbols.
    
    Returns all symbols that are actively being monitored.
    Frontend uses this to populate the token selector dropdown.
    
    Returns:
        List of symbol info with name and base currency
    """
    from src.config import MultiTokenConfig
    
    config = MultiTokenConfig()
    
    # Map symbols to displayable info
    symbol_info = []
    for symbol in config.symbols:
        base = symbol.replace("USDT", "")
        symbol_info.append({
            "symbol": symbol.lower(),
            "display": symbol,
            "base": base,
            "quote": "USDT",
            "name": _get_token_name(base),
        })
    
    return {
        "symbols": symbol_info,
        "count": len(symbol_info),
        "default": config.symbols[0].lower() if config.symbols else "btcusdt"
    }


def _get_token_name(base: str) -> str:
    """Get full name for token base currency."""
    names = {
        "BTC": "Bitcoin",
        "ETH": "Ethereum",
        "SOL": "Solana",
        "BNB": "BNB",
        "TAO": "Bittensor",
        "FET": "Fetch.ai",
        "ONDO": "Ondo Finance",
        "XRP": "Ripple",
        "ADA": "Cardano",
        "DOGE": "Dogecoin",
    }
    return names.get(base, base)
