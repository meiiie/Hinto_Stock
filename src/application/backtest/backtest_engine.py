"""
BacktestEngine - Application Layer

The orchestrator for backtesting trading strategies.
Supports "Shark Tank" Portfolio Logic (Centralized Capital Allocation).
"""

import logging
import asyncio
from datetime import datetime
from typing import List, Optional, Dict, Any

from ...domain.entities.candle import Candle
from ...domain.entities.trading_signal import TradingSignal
from ..signals.signal_generator import SignalGenerator
from .execution_simulator import ExecutionSimulator
from ...infrastructure.data.historical_data_loader import HistoricalDataLoader


class BacktestEngine:
    """
    Event-driven backtest engine for Hinto Stock.
    """
    
    def __init__(
        self,
        signal_generator: SignalGenerator,
        loader: Optional[HistoricalDataLoader] = None,
        simulator: Optional[ExecutionSimulator] = None
    ):
        self.signal_generator = signal_generator
        self.loader = loader or HistoricalDataLoader()
        self.simulator = simulator or ExecutionSimulator()
        self.logger = logging.getLogger(__name__)

    async def run(
        self,
        symbol: str,
        interval: str,
        start_time: datetime,
        end_time: Optional[datetime] = None,
        warmup_candles: int = 50
    ) -> Dict[str, Any]:
        """Run single-asset backtest."""
        return await self.run_portfolio([symbol], interval, start_time, end_time, warmup_candles)

    async def run_portfolio(
        self,
        symbols: List[str],
        interval: str,
        start_time: datetime,
        end_time: Optional[datetime] = None,
        warmup_candles: int = 50
    ) -> Dict[str, Any]:
        """
        Run synchronized portfolio backtest.
        Supports Shark Tank mode via ExecutionSimulator.
        """
        # 1. Load aligned data
        timeline_data = await self.loader.load_portfolio_data(symbols, interval, start_time, end_time)
        
        if len(timeline_data) < warmup_candles + 10:
            self.logger.error("Insufficient data for backtest")
            return {"error": "Insufficient data"}

        self.logger.info(f"🚀 Starting PORTFOLIO backtest | {len(timeline_data)} timestamps | {len(symbols)} symbols")
        
        # State tracking
        symbol_histories: Dict[str, List[Candle]] = {s: [] for s in symbols}
        
        timestamps = sorted(timeline_data.keys())
        
        # 2. Main Time Loop
        for i, ts in enumerate(timestamps):
            current_candles_map = timeline_data[ts]
            
            # Update histories first
            for sym, candle in current_candles_map.items():
                symbol_histories[sym].append(candle)
            
            if i < warmup_candles:
                continue
                
            # Step 1: Update Simulator (Process Intrabar Price Action & Fills)
            # Checks pending orders, SL, TP using current candle data
            self.simulator.update(current_candles_map, ts)
            
            # Step 2: Generate Signals (at Close) for NEXT candle
            signals_batch = []
            for sym, candle in current_candles_map.items():
                history = symbol_histories[sym]
                if len(history) < warmup_candles: continue
                
                signal = self.signal_generator.generate_signal(history, sym)
                if signal and signal.signal_type.value != 'neutral':
                    signals_batch.append(signal)
            
            # Step 3: Shark Tank Allocation
            # Feed batch to simulator to pick the best prey
            if signals_batch:
                self.simulator.process_batch_signals(signals_batch)
            
            # Log progress
            if i % 1000 == 0:
                self.logger.info(f"Progress: {i}/{len(timestamps)} steps...")

        # 3. Compile Results
        stats = self.simulator.get_stats()
        
        self.logger.info(f"✨ Portfolio Backtest Complete!")
        self.logger.info(f"Final Balance: ${stats['final_balance']:.2f} | Return: {stats['net_return_pct']:.2f}%")
        
        return {
            "symbols": symbols,
            "interval": interval,
            "stats": stats,
            "trades": [t.__dict__ for t in self.simulator.trades],
            "equity": self.simulator.equity_curve
        }