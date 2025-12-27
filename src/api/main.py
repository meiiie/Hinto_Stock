from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import logging

from src.api.routers import system, market, settings, trades, signals
from src.api.routers.market import market_router
from src.api.dependencies import get_realtime_service, get_container
from src.api.event_bus import get_event_bus
from src.api.websocket_manager import get_websocket_manager
from src.config import MultiTokenConfig
from src.infrastructure.websocket.shared_binance_client import get_shared_binance_client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Multi-token configuration (loaded from env or defaults)
multi_token_config = MultiTokenConfig()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI Lifespan - manages startup and shutdown.
    
    SOTA Multi-Token Architecture (Binance Best Practices Dec 2025):
    1. Start EventBus broadcast worker
    2. Create RealtimeService per symbol and register with SharedBinanceClient
    3. Start single SharedBinanceClient (1 WebSocket for ALL symbols)
    4. Start DataRetentionService
    
    Benefits:
    - 1 WebSocket connection instead of 7 (no timeout issues)
    - Binance rate limit compliant
    - Instant startup (no staggered delays)
    """
    # Startup
    logger.info("🚀 Starting up Hinto Trader Pro API...")
    logger.info(f"📊 Multi-Token: {len(multi_token_config.symbols)} symbols configured")
    
    # 1. Get singletons
    event_bus = get_event_bus()
    ws_manager = get_websocket_manager()
    container = get_container()
    retention_service = container.get_data_retention_service()
    shared_client = get_shared_binance_client()
    
    # 2. Start EventBus broadcast worker
    await event_bus.start_worker(ws_manager)
    logger.info("✅ EventBus broadcast worker started")
    
    # 3. SOTA: Create RealtimeService per symbol and register with SharedBinanceClient
    services = []
    for symbol in multi_token_config.symbols:
        service = container.get_realtime_service(symbol.lower())
        service.set_event_bus(event_bus)
        
        # Start service in shared_client_mode (loads historical data, skips WebSocket)
        await service.start(shared_client_mode=True)
        
        # Register service's candle handler with shared client
        shared_client.register_handler(symbol.lower(), service.on_candle_update)
        services.append(service)
        logger.info(f"📝 Registered handler for {symbol}")
    
    # Store services in app state for shutdown
    app.state.realtime_services = services
    app.state.shared_client = shared_client
    
    # 4. SOTA: Start single combined WebSocket connection for ALL symbols
    # This is the key improvement - 1 connection instead of 7!
    try:
        await shared_client.connect()
        logger.info(f"✅ SOTA: Combined Streams connected ({len(multi_token_config.symbols)} symbols × 3 timeframes = {len(multi_token_config.symbols) * 3} streams)")
    except Exception as e:
        logger.error(f"❌ Failed to connect shared client: {e}")
    
    # 5. Start DataRetentionService (SOTA auto-cleanup)
    await retention_service.start()
    logger.info("✅ DataRetentionService started (auto-cleanup enabled)")
    
    logger.info("🎯 All services started successfully!")
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")
    await retention_service.stop()
    await shared_client.disconnect()
    await event_bus.stop_worker()
    logger.info("✅ Shutdown complete")

app = FastAPI(
    title="Hinto Trader Pro API",
    description="Backend API for Hinto Trader Pro Desktop App",
    version="0.1.0",
    lifespan=lifespan
)

# Configure CORS
# Allowing all origins for development convenience with Tauri
origins = [
    "http://localhost:1420",  # Tauri dev
    "http://127.0.0.1:1420",
    "*" # Allow all for now to ensure smooth dev experience
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(system.router)
app.include_router(market.router)
app.include_router(market_router)  # /market/* endpoints
app.include_router(settings.router)
app.include_router(trades.router)
app.include_router(signals.router)  # Signal lifecycle tracking

@app.get("/")
async def root():
    return {"message": "Hinto Trader Pro API is running"}
