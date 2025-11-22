import asyncio
import json
import logging
from datetime import datetime
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

try:
    import websockets
except ImportError:
    logger.error("websockets library not found. Please install: pip install websockets")
    sys.exit(1)

async def test_websocket():
    symbol = "btcusdt"
    interval = "1m"
    base_url = "wss://stream.binance.com:9443/ws"
    stream_name = f"{symbol.lower()}@kline_{interval}"
    url = f"{base_url}/{stream_name}"
    
    logger.info(f"Connecting to {url}...")
    
    try:
        async with websockets.connect(url) as websocket:
            logger.info("✅ Connected!")
            
            # Wait for messages
            logger.info("Waiting for messages (Ctrl+C to stop)...")
            
            count = 0
            while count < 5:
                message = await websocket.recv()
                data = json.loads(message)
                
                # Calculate latency
                if 'E' in data:
                    event_time = datetime.fromtimestamp(data['E'] / 1000)
                    latency = (datetime.now() - event_time).total_seconds() * 1000
                    logger.info(f"📩 Message received! Latency: {latency:.0f}ms")
                    logger.info(f"   Price: {data['k']['c']}")
                else:
                    logger.info(f"📩 Message received: {data}")
                
                count += 1
            
            logger.info("✅ Test passed: Received 5 messages.")
            
    except Exception as e:
        logger.error(f"❌ Connection failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    try:
        asyncio.run(test_websocket())
    except KeyboardInterrupt:
        pass
