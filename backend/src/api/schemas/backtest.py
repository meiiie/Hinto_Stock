from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

class BacktestRequest(BaseModel):
    symbols: List[str] = Field(..., example=["BTCUSDT", "ETHUSDT"])
    interval: str = Field("15m", example="15m")
    start_time: datetime = Field(..., example="2024-01-01T00:00:00")
    end_time: Optional[datetime] = Field(None, example="2024-02-01T00:00:00")
    initial_balance: float = Field(10000.0, gt=0)
    risk_per_trade: float = Field(0.01, gt=0, le=1.0)
    enable_circuit_breaker: bool = Field(True, description="Enable Circuit Breaker for risk management")
    max_positions: int = Field(3, ge=1, description="Max concurrent positions (Shark Tank Mode)")
    
    # SOTA Hardcore Configs
    leverage: float = Field(10.0, description="Fixed Leverage")
    max_order_value: float = Field(50000.0, description="Liquidity Cap (Tier 1)")
    maintenance_margin_rate: float = Field(0.004, description="Maintenance Margin Rate (0.4%)")
    max_consecutive_losses: int = Field(3, description="CB Max Losses")
    cb_cooldown_hours: int = Field(4, description="CB Cooldown Hours")
    cb_drawdown_limit: float = Field(0.15, description="CB Portfolio Drawdown Limit")

class BacktestTradeResponse(BaseModel):
    trade_id: str
    symbol: str
    side: str
    entry_price: float
    exit_price: float
    entry_time: datetime
    exit_time: datetime
    pnl_usd: float
    pnl_pct: float
    exit_reason: str
    position_size: float
    leverage_at_entry: float

class BacktestStatsResponse(BaseModel):
    initial_balance: float
    final_balance: float
    net_return_usd: float
    net_return_pct: float
    total_trades: int
    win_rate: float
    winning_trades: int
    losing_trades: int

class EquityPoint(BaseModel):
    time: datetime
    balance: float

class CandleData(BaseModel):
    time: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float

class BlockedInterval(BaseModel):
    symbol: str
    start_time: datetime
    end_time: datetime
    reason: str

class BacktestResponse(BaseModel):
    symbols: List[str]
    stats: BacktestStatsResponse
    trades: List[BacktestTradeResponse]
    equity: List[EquityPoint]
    candles: Dict[str, List[CandleData]] # Map symbol -> candles
    indicators: Dict[str, Dict[str, List[Optional[float]]]] # Map symbol -> indicator_name -> values
    blocked_periods: List[BlockedInterval] = []