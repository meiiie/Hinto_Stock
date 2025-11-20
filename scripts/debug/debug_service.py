#!/usr/bin/env python3
"""
Debug script to test RealtimeService initialization and WebSocket connection.
"""

import asyncio
import sys
import os
import logging
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def test_websocket_connection():
    """Test WebSocket connection to Binance"""
    logger.info("=" * 60)
    logger.info("Testing WebSocket Connection")
    logger.info("=" * 60)
    
    try:
        from src.infrastructure.websocket import BinanceWebSocketClient
        
        client = BinanceWebSocketClient()
        logger.info(f"Created WebSocket client: {client}")
        
        # Define callback
        def on_candle(candle, metadata):
            logger.info(f"✅ Received candle: {candle.timestamp} - Close: ${candle.close:,.2f}")
        
        client.subscribe_candle(on_candle)
        logger.info("Subscribed to candle updates")
        
        # Connect
        logger.info("Attempting to connect to Binance WebSocket...")
        await client.connect(symbol='btcusdt', interval='1m')
        logger.info("✅ WebSocket connected!")
        
        # Wait for data
        logger.info("Waiting 10 seconds for data...")
        await asyncio.sleep(10)
        
        # Check status
        status = client.get_connection_status()
        logger.info(f"Connection status: {status}")
        
        # Disconnect
        await client.disconnect()
        logger.info("✅ WebSocket disconnected")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ WebSocket test failed: {e}", exc_info=True)
        return False


async def test_realtime_service():
    """Test RealtimeService initialization and startup"""
    logger.info("=" * 60)
    logger.info("Testing RealtimeService")
    logger.info("=" * 60)
    
    try:
        from src.application.services.realtime_service import RealtimeService
        
        service = RealtimeService()
        logger.info(f"Created service: {service}")
        
        # Start service
        logger.info("Starting service...")
        await service.start()
        logger.info("✅ Service started!")
        
        # Wait for data
        logger.info("Waiting 70 seconds for data collection (need full candle cycle)...")
        for i in range(70):
            await asyncio.sleep(1)
            status = service.get_status()
            candles_1m = status['data'].get('1m_candles', 0)
            if i % 10 == 0 or candles_1m > 0:
                logger.info(f"[{i+1}s] 1m candles: {candles_1m}")
        
        # Get final status
        status = service.get_status()
        logger.info(f"Final status: {status}")
        
        # Stop service
        logger.info("Stopping service...")
        await service.stop()
        logger.info("✅ Service stopped")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Service test failed: {e}", exc_info=True)
        return False


async def main():
    """Run all tests"""
    logger.info("\n" + "=" * 60)
    logger.info("REALTIME SERVICE DEBUG")
    logger.info("=" * 60 + "\n")
    
    # Test 1: WebSocket
    logger.info("\n[TEST 1] WebSocket Connection")
    ws_result = await test_websocket_connection()
    
    # Test 2: RealtimeService
    logger.info("\n[TEST 2] RealtimeService")
    service_result = await test_realtime_service()
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("TEST SUMMARY")
    logger.info("=" * 60)
    logger.info(f"WebSocket Connection: {'✅ PASS' if ws_result else '❌ FAIL'}")
    logger.info(f"RealtimeService: {'✅ PASS' if service_result else '❌ FAIL'}")
    logger.info("=" * 60 + "\n")
    
    return ws_result and service_result


if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        logger.info("\n⚠️ Interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
