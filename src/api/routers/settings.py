"""
Settings API Router

Handles trading settings configuration.
Requirements: 6.3
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from src.api.dependencies import get_paper_trading_service
from src.application.services.paper_trading_service import PaperTradingService

router = APIRouter(
    prefix="/settings",
    tags=["settings"]
)


class SettingsUpdate(BaseModel):
    """Request model for updating settings"""
    risk_percent: Optional[float] = Field(None, ge=0.1, le=10.0, description="Risk per trade (0.1-10%)")
    rr_ratio: Optional[float] = Field(None, ge=1.0, le=5.0, description="Risk/Reward ratio (1.0-5.0)")
    max_positions: Optional[int] = Field(None, ge=1, le=10, description="Max concurrent positions")
    leverage: Optional[int] = Field(None, ge=1, le=20, description="Leverage (1-20x)")
    auto_execute: Optional[bool] = Field(None, description="Auto-execute signals")


class SettingsResponse(BaseModel):
    """Response model for settings"""
    risk_percent: float
    rr_ratio: float
    max_positions: int
    leverage: int
    auto_execute: bool


@router.get("", response_model=SettingsResponse)
async def get_settings(
    paper_service: PaperTradingService = Depends(get_paper_trading_service)
):
    """
    Get current trading settings.
    
    Returns all configurable trading parameters.
    """
    settings = paper_service.get_settings()
    return SettingsResponse(**settings)


@router.post("", response_model=SettingsResponse)
async def update_settings(
    settings_update: SettingsUpdate,
    paper_service: PaperTradingService = Depends(get_paper_trading_service)
):
    """
    Update trading settings.
    
    Persists settings to SQLite and applies them to subsequent signals.
    Requirements: 6.3
    """
    # Filter out None values
    update_dict = {k: v for k, v in settings_update.model_dump().items() if v is not None}
    
    if not update_dict:
        raise HTTPException(status_code=400, detail="No settings provided to update")
    
    # Update and return new settings
    updated = paper_service.update_settings(update_dict)
    return SettingsResponse(**updated)


@router.get("/strategy")
async def get_strategy_parameters():
    """
    Get current strategy parameters (read-only).
    
    Returns VWAP, Bollinger Bands, and StochRSI configuration.
    Requirements: 6.4
    """
    return {
        "vwap": {
            "enabled": True,
            "description": "Volume Weighted Average Price"
        },
        "bollinger_bands": {
            "period": 20,
            "std_dev": 2.0,
            "description": "Bollinger Bands (20, 2)"
        },
        "stoch_rsi": {
            "rsi_period": 14,
            "stoch_period": 14,
            "k_period": 3,
            "d_period": 3,
            "description": "Stochastic RSI (3, 3, 14, 14)"
        }
    }
