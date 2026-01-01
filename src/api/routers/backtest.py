from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime, timezone, timedelta
import logging

from src.application.backtest.backtest_engine import BacktestEngine
from src.api.dependencies import get_container

router = APIRouter(prefix="/backtest", tags=["Backtest"])
logger = logging.getLogger(__name__)

class BacktestRequest(BaseModel):
    symbol: str = "BTCUSDT"
    interval: str = "15m"
    days: int = 7
    balance: float = 10000.0

@router.post("/run")
async def run_backtest(req: BacktestRequest):
    """
    Run a backtest for a specific symbol.
    """
    try:
        container = get_container()
        # Get a fresh signal generator to avoid state pollution, or use the singleton
        # Ideally, backtest should be isolated.
        signal_gen = container.get_signal_generator()
        
        engine = BacktestEngine(signal_generator=signal_gen)
        
        # Hack: Inject balance into simulator
        engine.simulator.balance = req.balance
        engine.simulator.initial_balance = req.balance
        
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(days=req.days)
        
        logger.info(f"Starting backtest for {req.symbol} ({req.days} days)")
        
        result = await engine.run(
            symbol=req.symbol.upper(),
            interval=req.interval,
            start_time=start_time,
            end_time=end_time
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Backtest failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
