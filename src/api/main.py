from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import logging

from src.api.routers import system, market, settings, trades
from src.api.routers.market import market_router
from src.api.dependencies import get_realtime_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up Hinto Trader Pro API...")
    service = get_realtime_service()
    
    # Start service in background task as requested by expert
    # This prevents blocking the API startup if service.start() takes time
    asyncio.create_task(service.start())
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")
    await service.stop()

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

@app.get("/")
async def root():
    return {"message": "Hinto Trader Pro API is running"}
