from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List
import logging
from datetime import datetime

from ..schemas.backtest import BacktestRequest, BacktestResponse
from ...application.backtest.backtest_engine import BacktestEngine
from ...infrastructure.di_container import DIContainer
from ...application.analysis.trend_filter import TrendFilter
from ...application.risk_management.circuit_breaker import CircuitBreaker
from ...application.backtest.execution_simulator import ExecutionSimulator
from ...infrastructure.data.historical_data_loader import HistoricalDataLoader

router = APIRouter(
    prefix="/backtest",
    tags=["Backtest"]
)

logger = logging.getLogger(__name__)

@router.post("/run", response_model=BacktestResponse)
async def run_backtest(request: BacktestRequest):
    """
    Run a backtest on the specified symbols and time range.
    Uses the SOTA 'Liquidity Sniper' strategy with Shark Tank execution mode.
    """
    try:
        logger.info(f"Received backtest request for {request.symbols}")
        
        # 1. Initialize Components via DI where possible
        container = DIContainer()
        signal_generator = container.get_signal_generator()
        loader = HistoricalDataLoader()
        
        # 2. Simulator in Shark Tank Mode (Portfolio Risk Management)
        # SOTA: Hardcore Reality Mode Configs
        simulator = ExecutionSimulator(
            initial_balance=request.initial_balance,
            risk_per_trade=request.risk_per_trade,
            fixed_leverage=request.leverage,
            mode="SHARK_TANK", 
            max_leverage=max(5.0, request.leverage),
            max_positions=request.max_positions,
            max_order_value=request.max_order_value,
            maintenance_margin_rate=request.maintenance_margin_rate
        )
        
        # 3. Advanced Filters
        trend_filter = TrendFilter(ema_period=200)
        
        circuit_breaker = None
        if request.enable_circuit_breaker:
            circuit_breaker = CircuitBreaker(
                max_consecutive_losses=request.max_consecutive_losses,
                cooldown_hours=request.cb_cooldown_hours,
                max_daily_drawdown_pct=request.cb_drawdown_limit
            )
        
        engine = BacktestEngine(
            signal_generator=signal_generator,
            loader=loader,
            simulator=simulator,
            trend_filter=trend_filter,
            circuit_breaker=circuit_breaker
        )
        
        # 4. Run Engine
        result = await engine.run_portfolio(
            symbols=request.symbols,
            interval=request.interval,
            start_time=request.start_time,
            end_time=request.end_time
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
            
        return result

    except Exception as e:
        logger.error(f"Backtest failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
