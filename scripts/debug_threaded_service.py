import sys
import os
import time
import logging

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.application.services.realtime_service_threaded import ThreadedRealtimeService
from src.utils.logging_config import configure_logging

def main():
    configure_logging(level=10)  # DEBUG level
    logger = logging.getLogger(__name__)
    
    logger.info("Starting ThreadedRealtimeService debug...")
    
    service = ThreadedRealtimeService(symbol='btcusdt', interval='1m')
    
    try:
        service.start()
        
        logger.info("Service started. Waiting for data...")
        
        # Monitor for 30 seconds
        for i in range(30):
            status = service.get_status()
            latency = status.get('connection', {}).get('latency', 0)
            candles = service.get_candles()
            
            logger.info(f"Time: {i}s | Connected: {status.get('connection', {}).get('is_connected')} | Latency: {latency}ms | Candles: {len(candles)}")
            
            if len(candles) > 0:
                logger.info(f"✅ Data received! Latest close: {candles[-1].close}")
            
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        service.stop()
        logger.info("Service stopped")

if __name__ == "__main__":
    main()
