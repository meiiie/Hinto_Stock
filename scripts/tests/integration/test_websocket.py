"""
Test WebSocket Client

Simple script to test Binance WebSocket connection and data streaming.
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.infrastructure.websocket import BinanceWebSocketClient
from src.utils.logging_config import configure_logging


async def on_candle_received(candle, metadata):
    """Callback for new candle data"""
    is_closed = "✅ CLOSED" if metadata['is_closed'] else "⏳ UPDATING"
    print(f"{is_closed} | {candle}")


async def on_connection_status(status):
    """Callback for connection status changes"""
    state_emoji = {
        'connected': '🟢',
        'disconnected': '🔴',
        'connecting': '🟡',
        'reconnecting': '🟠',
        'error': '❌'
    }
    emoji = state_emoji.get(status.state.value, '⚪')
    print(f"\n{emoji} Connection: {status.state.value.upper()}")
    print(f"   Latency: {status.latency_ms}ms")
    print(f"   Reconnects: {status.reconnect_count}")
    if status.error_message:
        print(f"   Error: {status.error_message}")
    print()


async def main():
    """Main test function"""
    # Configure logging
    configure_logging(level=20)  # INFO level
    
    print("=" * 60)
    print("🚀 Binance WebSocket Client Test")
    print("=" * 60)
    print()
    print("Testing real-time BTC/USDT 1-minute candles...")
    print("Press Ctrl+C to stop")
    print()
    
    # Create WebSocket client
    client = BinanceWebSocketClient()
    
    # Subscribe to candle updates
    client.subscribe_candle(on_candle_received)
    client.subscribe_connection_status(on_connection_status)
    
    try:
        # Connect to Binance WebSocket
        await client.connect(symbol='btcusdt', interval='1m')
        
        # Keep running for 60 seconds (or until Ctrl+C)
        print("✅ Connected! Receiving data...")
        print()
        
        await asyncio.sleep(60)
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Stopping...")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        # Disconnect
        await client.disconnect()
        print("✅ Disconnected")
        print()
        
        # Show final status
        status = client.get_connection_status()
        print("Final Status:")
        print(f"  Total reconnects: {status.reconnect_count}")
        print(f"  Last update: {status.last_update.strftime('%H:%M:%S')}")
        print(f"  Average latency: {status.latency_ms}ms")


if __name__ == "__main__":
    asyncio.run(main())
