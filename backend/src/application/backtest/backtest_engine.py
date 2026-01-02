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
from ...domain.interfaces.i_historical_data_loader import IHistoricalDataLoader
from ..analysis.trend_filter import TrendFilter
from ..risk_management.circuit_breaker import CircuitBreaker


class BacktestEngine:
    def __init__(
        self,
        signal_generator: SignalGenerator,
        loader: IHistoricalDataLoader,
        simulator: Optional[ExecutionSimulator] = None,
        trend_filter: Optional[TrendFilter] = None,
        circuit_breaker: Optional[CircuitBreaker] = None
    ):
        self.signal_generator = signal_generator
        self.loader = loader 
        self.simulator = simulator or ExecutionSimulator()
        self.trend_filter = trend_filter or TrendFilter(ema_period=200)
        self.circuit_breaker = circuit_breaker
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
                # 1. Update Portfolio Health (Global Drawdown Check)
                self.circuit_breaker.update_portfolio_state(self.simulator.balance, ts)
                
                # 2. Record Completed Trades
                for trade in self.simulator.trades:
                    if trade.exit_time == ts:
                        self.circuit_breaker.record_trade_with_time(trade.symbol, trade.side, trade.pnl_usd, ts)

            # E. Signal Generation
            signals_batch = []
            for sym, candle in current_ltf_map.items():
                if len(symbol_histories_ltf[sym]) < warmup_candles: continue
                
                # Check Circuit Breaker
                if self.circuit_breaker:
                    # Global Block or Symbol Block
                    if self.circuit_breaker.is_blocked(sym, 'LONG', ts):
                        continue # Skip this symbol entirely if blocked (simplification, ideally check per side)
                        # Actually 'is_blocked' checks global internally too. 
                        # If LONG is blocked, we might still want SHORT? 
                        # The original code skipped the symbol entirely if EITHER was blocked.
                        # Let's refine:
                        
                    is_long_blocked = self.circuit_breaker.is_blocked(sym, 'LONG', ts)
                    is_short_blocked = self.circuit_breaker.is_blocked(sym, 'SHORT', ts)
                    
                    # Optimization: If Global Block is active, is_blocked returns True for everything.
                    if is_long_blocked and is_short_blocked:
                        continue

                signal = self.signal_generator.generate_signal(
                    symbol_histories_ltf[sym], sym, htf_bias=htf_bias_map.get(sym, 'NEUTRAL')
                )
                
                if signal and signal.signal_type.value != 'neutral':
                    # Filter signal by CB
                    if self.circuit_breaker:
                        if signal.signal_type.value == 'buy' and is_long_blocked: continue
                        if signal.signal_type.value == 'sell' and is_short_blocked: continue
                        
                    signals_batch.append(signal)
            
            # F. Shark Tank Execution
            if signals_batch:
                self.simulator.process_batch_signals(signals_batch)
            
            if i % 1000 == 0:
                self.logger.info(f"Progress: {i}/{len(ltf_ts_list)} steps...")

        # Prepare candle data for API
        candles_output = {}
        indicators_output = {}
        
        for sym, hist in symbol_histories_ltf.items():
            # 1. Candles
            candles_output[sym] = [
                {
                    "time": c.timestamp,
                    "open": c.open,
                    "high": c.high,
                    "low": c.low,
                    "close": c.close,
                    "volume": c.volume
                } for c in hist
            ]
            
            # 2. Visualization Indicators (Batch Calculation)
            # We use pandas for efficient batch processing for the frontend chart
            if not hist:
                continue
                
            try:
                import pandas as pd
                import numpy as np
                
                df = pd.DataFrame([vars(c) for c in hist])
                df.set_index('timestamp', inplace=True)
                df.sort_index(inplace=True)
                
                # A. Bollinger Bands (20, 2.0)
                # Matches standard Liquidity Sniper settings
                df['tp'] = (df['high'] + df['low'] + df['close']) / 3
                df['ma'] = df['tp'].rolling(window=20).mean()
                df['std'] = df['tp'].rolling(window=20).std()
                df['bb_upper'] = df['ma'] + (2.0 * df['std'])
                df['bb_lower'] = df['ma'] - (2.0 * df['std'])
                
                # B. VWAP (Rolling 24h = 96 periods of 15m)
                # Standard crypto intraday VWAP approximation
                v = df['volume'].values
                tp = df['tp'].values
                df['vwap'] = (df['volume'] * df['tp']).rolling(window=96).sum() / df['volume'].rolling(window=96).sum()
                
                # C. Limit Sniper Levels (Swing High/Low 20 + 0.1%)
                # Visualization only - to show where the bot IS LOOKING to enter
                df['swing_high'] = df['high'].rolling(window=20).max()
                df['swing_low'] = df['low'].rolling(window=20).min()
                df['limit_sell'] = df['swing_high'] * 1.001
                df['limit_buy'] = df['swing_low'] * 0.999

                # Fill NaN
                df.fillna(0, inplace=True) # Or keep None for chart to skip
                
                indicators_output[sym] = {
                    "bb_upper": df['bb_upper'].replace({np.nan: None}).tolist(),
                    "bb_lower": df['bb_lower'].replace({np.nan: None}).tolist(),
                    "vwap": df['vwap'].replace({np.nan: None}).tolist(),
                    "limit_sell": df['limit_sell'].replace({np.nan: None}).tolist(),
                    "limit_buy": df['limit_buy'].replace({np.nan: None}).tolist()
                }
                
            except ImportError:
                self.logger.warning("Pandas not found, skipping visualization indicators")
                indicators_output[sym] = {}
            except Exception as e:
                self.logger.error(f"Failed to calc visualization indicators for {sym}: {e}")
                indicators_output[sym] = {}
        
        # Prepare Blocked Periods (Circuit Breaker)
        blocked_periods = []
        if self.circuit_breaker:
             pass

        return {
            "symbols": symbols,
            "stats": self.simulator.get_stats(),
            "trades": [t.__dict__ for t in self.simulator.trades],
            "equity": self.simulator.equity_curve,
            "candles": candles_output,
            "indicators": indicators_output,
            "blocked_periods": blocked_periods
        }