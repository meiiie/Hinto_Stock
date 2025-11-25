"""
WebSocket Manager with Pub/Sub Pattern

**Feature: desktop-trading-dashboard**
**Validates: Requirements 5.2, 5.3**

Manages WebSocket connections with:
- Connection tracking with graceful disconnect handling
- Pub/Sub broadcast mechanism from Trading Engine to connected clients
- Graceful handling of WebSocketDisconnect without crashing
"""

import asyncio
import json
import logging
from typing import Dict, List, Set, Optional, Callable, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from fastapi import WebSocket, WebSocketDisconnect


logger = logging.getLogger(__name__)


class ConnectionState(Enum):
    """WebSocket connection states."""
    CONNECTING = "connecting"
    CONNECTED = "connected"
    DISCONNECTING = "disconnecting"
    DISCONNECTED = "disconnected"


@dataclass
class ClientConnection:
    """Represents a connected WebSocket client."""
    websocket: WebSocket
    client_id: str
    symbol: str
    connected_at: datetime = field(default_factory=datetime.now)
    state: ConnectionState = ConnectionState.CONNECTING
    message_count: int = 0
    last_message_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for status reporting."""
        return {
            'client_id': self.client_id,
            'symbol': self.symbol,
            'connected_at': self.connected_at.isoformat(),
            'state': self.state.value,
            'message_count': self.message_count,
            'last_message_at': self.last_message_at.isoformat() if self.last_message_at else None
        }


class WebSocketManager:
    """
    Manages WebSocket connections with Pub/Sub pattern.
    
    Features:
    - Connection tracking per symbol (topic)
    - Graceful disconnect handling
    - Broadcast to all clients or by symbol
    - Thread-safe operations
    - Connection statistics
    
    Design Pattern: Pub/Sub
    - Publishers: Trading Engine, Signal Generator
    - Subscribers: Frontend WebSocket clients
    - Topics: Symbol names (e.g., 'btcusdt')
    """
    
    def __init__(self):
        # Connections by symbol (topic) - using Dict[client_id, ClientConnection]
        self._connections: Dict[str, Dict[str, ClientConnection]] = {}
        
        # All connections for quick lookup
        self._all_connections: Dict[str, ClientConnection] = {}
        
        # Lock for thread-safe operations
        self._lock = asyncio.Lock()
        
        # Statistics
        self._total_connections = 0
        self._total_disconnections = 0
        self._total_messages_sent = 0
        
        # Callbacks for connection events
        self._on_connect_callbacks: List[Callable] = []
        self._on_disconnect_callbacks: List[Callable] = []
        
        logger.info("WebSocketManager initialized")
    
    async def connect(self, websocket: WebSocket, symbol: str, client_id: Optional[str] = None) -> ClientConnection:
        """
        Accept and register a new WebSocket connection.
        
        Args:
            websocket: FastAPI WebSocket instance
            symbol: Symbol/topic to subscribe to
            client_id: Optional client identifier
            
        Returns:
            ClientConnection object
        """
        # Generate client_id if not provided
        if not client_id:
            client_id = f"{symbol}_{self._total_connections}_{datetime.now().timestamp()}"
        
        # Accept the WebSocket connection
        await websocket.accept()
        
        # Create connection object
        connection = ClientConnection(
            websocket=websocket,
            client_id=client_id,
            symbol=symbol,
            state=ConnectionState.CONNECTED
        )
        
        async with self._lock:
            # Add to symbol-specific dict
            if symbol not in self._connections:
                self._connections[symbol] = {}
            self._connections[symbol][client_id] = connection
            
            # Add to all connections
            self._all_connections[client_id] = connection
            
            # Update statistics
            self._total_connections += 1
        
        logger.info(f"Client connected: {client_id} for symbol {symbol}. "
                   f"Total connections: {len(self._all_connections)}")
        
        # Notify callbacks
        await self._notify_connect(connection)
        
        return connection
    
    async def disconnect(self, connection: ClientConnection) -> None:
        """
        Gracefully disconnect a client.
        
        Args:
            connection: ClientConnection to disconnect
        """
        if connection.state == ConnectionState.DISCONNECTED:
            return
        
        connection.state = ConnectionState.DISCONNECTING
        
        async with self._lock:
            # Remove from symbol dict
            symbol = connection.symbol
            if symbol in self._connections:
                if connection.client_id in self._connections[symbol]:
                    del self._connections[symbol][connection.client_id]
                
                # Clean up empty symbol dicts
                if not self._connections[symbol]:
                    del self._connections[symbol]
            
            # Remove from all connections
            if connection.client_id in self._all_connections:
                del self._all_connections[connection.client_id]
            
            # Update statistics
            self._total_disconnections += 1
        
        connection.state = ConnectionState.DISCONNECTED
        
        logger.info(f"Client disconnected: {connection.client_id}. "
                   f"Total connections: {len(self._all_connections)}")
        
        # Notify callbacks
        await self._notify_disconnect(connection)
    
    async def disconnect_by_websocket(self, websocket: WebSocket) -> None:
        """
        Disconnect by WebSocket instance (for exception handling).
        
        Args:
            websocket: WebSocket to find and disconnect
        """
        connection = None
        
        async with self._lock:
            for conn in list(self._all_connections.values()):
                if conn.websocket is websocket:
                    connection = conn
                    break
        
        if connection:
            await self.disconnect(connection)
    
    async def broadcast(self, message: Dict[str, Any], symbol: Optional[str] = None) -> int:
        """
        Broadcast message to connected clients.
        
        Args:
            message: Message dict to send
            symbol: Optional symbol to filter recipients (None = all)
            
        Returns:
            Number of clients message was sent to
        """
        json_message = json.dumps(message)
        sent_count = 0
        failed_connections: List[ClientConnection] = []
        
        async with self._lock:
            if symbol:
                # Send to specific symbol subscribers
                connections = list(self._connections.get(symbol, {}).values())
            else:
                # Send to all
                connections = list(self._all_connections.values())
        
        for connection in connections:
            if connection.state != ConnectionState.CONNECTED:
                continue
                
            try:
                await connection.websocket.send_text(json_message)
                connection.message_count += 1
                connection.last_message_at = datetime.now()
                sent_count += 1
                
            except WebSocketDisconnect:
                # Client disconnected - mark for cleanup
                logger.debug(f"Client {connection.client_id} disconnected during broadcast")
                failed_connections.append(connection)
                
            except Exception as e:
                # Other errors - log and mark for cleanup
                logger.warning(f"Error sending to {connection.client_id}: {e}")
                failed_connections.append(connection)
        
        # Clean up failed connections
        for conn in failed_connections:
            await self.disconnect(conn)
        
        # Update statistics
        self._total_messages_sent += sent_count
        
        return sent_count
    
    async def send_to_client(self, client_id: str, message: Dict[str, Any]) -> bool:
        """
        Send message to a specific client.
        
        Args:
            client_id: Target client ID
            message: Message to send
            
        Returns:
            True if sent successfully
        """
        connection = self._all_connections.get(client_id)
        
        if not connection or connection.state != ConnectionState.CONNECTED:
            return False
        
        try:
            await connection.websocket.send_text(json.dumps(message))
            connection.message_count += 1
            connection.last_message_at = datetime.now()
            return True
            
        except Exception as e:
            logger.warning(f"Error sending to {client_id}: {e}")
            await self.disconnect(connection)
            return False
    
    def get_connection_count(self, symbol: Optional[str] = None) -> int:
        """
        Get number of active connections.
        
        Args:
            symbol: Optional symbol filter
            
        Returns:
            Connection count
        """
        if symbol:
            return len(self._connections.get(symbol, {}))
        return len(self._all_connections)
    
    def get_subscribed_symbols(self) -> List[str]:
        """Get list of symbols with active subscribers."""
        return list(self._connections.keys())
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get manager statistics."""
        return {
            'active_connections': len(self._all_connections),
            'total_connections': self._total_connections,
            'total_disconnections': self._total_disconnections,
            'total_messages_sent': self._total_messages_sent,
            'subscribed_symbols': self.get_subscribed_symbols(),
            'connections_by_symbol': {
                symbol: len(conns) 
                for symbol, conns in self._connections.items()
            }
        }
    
    def get_all_connections_info(self) -> List[Dict[str, Any]]:
        """Get info about all connections."""
        return [conn.to_dict() for conn in self._all_connections.values()]
    
    def on_connect(self, callback: Callable) -> None:
        """Register callback for connection events."""
        self._on_connect_callbacks.append(callback)
    
    def on_disconnect(self, callback: Callable) -> None:
        """Register callback for disconnection events."""
        self._on_disconnect_callbacks.append(callback)
    
    async def _notify_connect(self, connection: ClientConnection) -> None:
        """Notify connect callbacks."""
        for callback in self._on_connect_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(connection)
                else:
                    callback(connection)
            except Exception as e:
                logger.error(f"Error in connect callback: {e}")
    
    async def _notify_disconnect(self, connection: ClientConnection) -> None:
        """Notify disconnect callbacks."""
        for callback in self._on_disconnect_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(connection)
                else:
                    callback(connection)
            except Exception as e:
                logger.error(f"Error in disconnect callback: {e}")
    
    def is_running(self) -> bool:
        """Check if manager has active connections."""
        return len(self._all_connections) > 0


# Global singleton instance
_manager_instance: Optional[WebSocketManager] = None


def get_websocket_manager() -> WebSocketManager:
    """Get or create the global WebSocketManager instance."""
    global _manager_instance
    if _manager_instance is None:
        _manager_instance = WebSocketManager()
    return _manager_instance
