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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI Lifespan - manages startup and shutdown.
    
    Event-Driven Architecture:
    1. Start EventBus broadcast worker FIRST
    2. Connect EventBus to RealtimeService
    3. Start RealtimeService (connects to Binance)
    4. Start DataRetentionService (SOTA cleanup)
    
    This ensures the broadcast worker is ready before any events are generated.
    """
    # Startup
    logger.info("🚀 Starting up Hinto Trader Pro API...")
    
    # 1. Get singletons
    event_bus = get_event_bus()
    ws_manager = get_websocket_manager()
    service = get_realtime_service()
    
    # Get DI container for retention service
    container = get_container()
    retention_service = container.get_data_retention_service()
    
    # 2. Start EventBus broadcast worker FIRST
    # This ensures worker is ready before service generates events
    await event_bus.start_worker(ws_manager)
    logger.info("✅ EventBus broadcast worker started")
    
    # 3. Connect EventBus to RealtimeService
    service.set_event_bus(event_bus)
    logger.info("✅ EventBus connected to RealtimeService")
    
    # 4. Start RealtimeService in background task
    # This connects to Binance and starts receiving data
    asyncio.create_task(service.start())
    logger.info("✅ RealtimeService starting...")
    
    # 5. Start DataRetentionService (SOTA auto-cleanup)
    await retention_service.start()
    logger.info("✅ DataRetentionService started (auto-cleanup enabled)")
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")
    await retention_service.stop()
    await service.stop()
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
