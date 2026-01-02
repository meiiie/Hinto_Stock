#!/usr/bin/env python3
"""
Real Backend Server with Binance Connection

Starts the FastAPI server with real Binance WebSocket connection.
"""

import uvicorn
import logging
import sys
import os

# Add 'backend' directory to sys.path
backend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

if __name__ == "__main__":
    print("🚀 Starting Hinto Trading Dashboard - Real Backend")
    print("📡 Connecting to Binance WebSocket...")
    print("=" * 50)
    
    # Import app directly to avoid module path issues with uvicorn string import
    try:
        from src.api.main import app
        uvicorn.run(
            app,
            host="127.0.0.1",
            port=8000,
            log_level="info"
        )
    except ImportError as e:
        print(f"❌ Error importing app: {e}")
        sys.exit(1)
