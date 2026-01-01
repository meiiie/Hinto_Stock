"""
BacktestEngine - Application Layer

The orchestrator for backtesting trading strategies.
SOTA Feature: Multi-Timeframe Synchronization (15m + H4) with Pointer Optimization.
"""

import logging
import asyncio
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from ...domain.entities.candle import Candle
from ...domain.entities.trading_signal import TradingSignal
from ..signals.signal_generator import SignalGenerator
from .execution_simulator import ExecutionSimulator
from ...infrastructure.data.historical_data_loader import HistoricalDataLoader
from ..analysis.trend_filter import TrendFilter
from ..risk_management.circuit_breaker import CircuitBreaker


class BacktestEngine:
    def __init__(
        self,
        signal_generator: SignalGenerator,
        loader: Optional[HistoricalDataLoader] = None,
        simulator: Optional[ExecutionSimulator] = None,
        trend_filter: Optional[TrendFilter] = None,
        circuit_breaker: Optional[CircuitBreaker] = None
    ):
        self.signal_generator = signal_generator
        self.loader = loader or HistoricalDataLoader()
        self.simulator = simulator or ExecutionSimulator()
        self.trend_filter = trend_filter or TrendFilter(ema_period=200)
        self.circuit_breaker = circuit_breaker # Fixed: Accept None
        self.logger = logging.getLogger(__name__)

    async def run_portfolio(
        self,
        symbols: List[str],
        interval: str,
        start_time: datetime,
        end_time: Optional[datetime] = None,
        warmup_candles: int = 50
    ) -> Dict[str, Any]:
        # 1. Load Data
        ltf_timeline = await self.loader.load_portfolio_data(symbols, interval, start_time, end_time)
        
        # HTF need more history for EMA200
        htf_start = start_time - timedelta(days=60) 
        htf_timeline = await self.loader.load_portfolio_data(symbols, "4h", htf_start, end_time)
        
        if not ltf_timeline:
            return {"error": "No data"}

        self.logger.info(f"🚀 Starting HTF-Enabled Backtest | {len(ltf_timeline)} steps | HTF: 4h")
        
        symbol_histories_ltf: Dict[str, List[Candle]] = {s: [] for s in symbols}
        symbol_histories_htf: Dict[str, List[Candle]] = {s: [] for s in symbols}
        
        ltf_ts_list = sorted(ltf_timeline.keys())
        htf_ts_list = sorted(htf_timeline.keys())
        
        htf_ptr = 0 # Pointer for efficient HTF sync
        
        # 2. Main Time Loop
        for i, ts in enumerate(ltf_ts_list):
            # A. Update HTF histories up to current timestamp
            while htf_ptr < len(htf_ts_list) and htf_ts_list[htf_ptr] <= ts:
                h_ts = htf_ts_list[htf_ptr]
                for sym, candle in htf_timeline[h_ts].items():
                    symbol_histories_htf[sym].append(candle)
                htf_ptr += 1
            
            # B. Update LTF
            current_ltf_map = ltf_timeline[ts]
            for sym, candle in current_ltf_map.items():
                symbol_histories_ltf[sym].append(candle)
            
            # C. Determine Bias
            htf_bias_map = {}
            for sym in symbols:
                h_history = symbol_histories_htf.get(sym, [])
                if len(h_history) >= 200:
                    htf_bias_map[sym] = self.trend_filter.calculate_bias(h_history)
                else:
                    htf_bias_map[sym] = 'NEUTRAL'

            # D. Update Simulator & Circuit Breaker Record
            self.simulator.update(current_ltf_map, ts)
            
            if self.circuit_breaker:
                for trade in self.simulator.trades:
                    if trade.exit_time == ts:
                        self.circuit_breaker.record_trade(trade.symbol, trade.side, trade.pnl_usd)

            # E. Signal Generation
            signals_batch = []
            for sym, candle in current_ltf_map.items():
                if len(symbol_histories_ltf[sym]) < warmup_candles: continue
                
                # Check Circuit Breaker
                if self.circuit_breaker:
                    if self.circuit_breaker.is_blocked(sym, 'LONG', ts) or \
                       self.circuit_breaker.is_blocked(sym, 'SHORT', ts):
                        continue

                signal = self.signal_generator.generate_signal(
                    symbol_histories_ltf[sym], sym, htf_bias=htf_bias_map.get(sym, 'NEUTRAL')
                )
                if signal and signal.signal_type.value != 'neutral':
                    signals_batch.append(signal)
            
            # F. Shark Tank Execution
            if signals_batch:
                self.simulator.process_batch_signals(signals_batch)
            
            if i % 1000 == 0:
                self.logger.info(f"Progress: {i}/{len(ltf_ts_list)} steps...")

        return {
            "symbols": symbols,
            "stats": self.simulator.get_stats(),
            "trades": [t.__dict__ for t in self.simulator.trades],
            "equity": self.simulator.equity_curve
        }
