from fastapi import APIRouter
from datetime import datetime

router = APIRouter(
    prefix="/system",
    tags=["system"]
)

@router.get("/status")
async def get_status():
    """
    Health check endpoint to verify system status.
    """
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "service": "hinto-trader-backend",
        "version": "0.1.0"
    }
