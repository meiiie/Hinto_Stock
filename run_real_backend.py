#!/usr/bin/env python3
"""
Real Backend Server with Binance Connection

Starts the FastAPI server with real Binance WebSocket connection.
"""

import uvicorn
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

if __name__ == "__main__":
    print("🚀 Starting Hinto Trading Dashboard - Real Backend")
    print("📡 Connecting to Binance WebSocket...")
    print("=" * 50)
    
    uvicorn.run(
        "src.api.main:app",
        host="127.0.0.1",
        port=8000,
        log_level="info",
        reload=False
    )
