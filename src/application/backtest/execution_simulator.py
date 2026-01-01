"""
ExecutionSimulator - Application Layer

Simulates professional trade execution for backtesting.
SOTA Updates 2026.01.02:
1. Entry-based Leverage Calculation (Fixes >5x display issue).
2. Semantic Exit Reasoning (STOP_LOSS vs TRAILING_STOP vs BREAKEVEN).
3. Precision Rounding for Institutional Reporting.
"""

import logging
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Dict, Any

from ...domain.entities.candle import Candle
from ...domain.entities.trading_signal import TradingSignal, SignalType


@dataclass
class BacktestTrade:
    """Represents a completed trade with institutional reporting fields."""
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
    notional_value: float = 0.0
    leverage_at_entry: float = 0.0 # Fixed: Based on equity at entry


class ExecutionSimulator:
    """
    Simulates trade execution with Institutional-Grade constraints and reporting.
    """
    
    def __init__(
        self,
        initial_balance: float = 10000.0,
        commission_pct: float = 0.04,
        slippage_pct: float = 0.02,
        risk_per_trade: float = 0.01,
        breakeven_trigger_r: float = 1.5,
        trailing_stop_atr: float = 4.0,
        fixed_leverage: float = 0.0,
        mode: str = "ISOLATED",
        max_leverage: float = 5.0
    ):
        self.balance = initial_balance
        self.initial_balance = initial_balance
        self.commission_rate = commission_pct / 100.0
        self.base_slippage_rate = slippage_pct / 100.0
        self.risk_per_trade = risk_per_trade
        self.breakeven_trigger_r = breakeven_trigger_r
        self.trailing_stop_atr = trailing_stop_atr
        self.fixed_leverage = fixed_leverage
        self.mode = mode
        self.max_leverage = max_leverage
        
        self.positions: Dict[str, Dict[str, Any]] = {}
        self.pending_orders: Dict[str, Dict[str, Any]] = {}
        
        self.trades: List[BacktestTrade] = []
        self.equity_curve: List[Dict[str, Any]] = []
        
        self.logger = logging.getLogger(__name__)

    def process_batch_signals(self, signals: List[TradingSignal]):
        if not signals: return
        candidates = [s for s in signals if s.symbol not in self.positions and s.symbol not in self.pending_orders]
        if not candidates: return
        candidates.sort(key=lambda s: s.confidence, reverse=True)
        
        if self.mode == "SHARK_TANK":
            self.place_order(candidates[0])
        else:
            for signal in candidates:
                self.place_order(signal)

    def place_order(self, signal: TradingSignal):
        symbol = signal.symbol
        if symbol in self.positions or symbol in self.pending_orders: return
        
        if self.mode == "SHARK_TANK":
            if len(self.positions) + len(self.pending_orders) >= 3: return

        initial_sl = signal.stop_loss
        if not initial_sl: return
        
        target_entry = signal.entry_price or signal.price
        
        sl_dist_pct = abs(target_entry - initial_sl) / target_entry
        if sl_dist_pct < 0.005: return 
        
        # Risk Management
        if self.fixed_leverage > 0:
            notional = self.balance * self.fixed_leverage
        else:
            risk_amt = self.balance * self.risk_per_trade
            notional = risk_amt / sl_dist_pct
            
        # Hard Leverage Cap
        max_notional = self.balance * self.max_leverage
        if notional > max_notional: 
            notional = max_notional
            
        if notional < 5: return

        self.pending_orders[symbol] = {
            'id': str(uuid.uuid4())[:8],
            'symbol': symbol,
            'side': 'LONG' if signal.signal_type == SignalType.BUY else 'SHORT',
            'type': 'LIMIT' if signal.is_limit_order else 'MARKET',
            'target_price': target_entry,
            'stop_loss': initial_sl,
            'tp_levels': signal.tp_levels,
            'notional': notional,
            'entry_equity': self.balance, # Fixed: Store equity at the moment of order creation
            'initial_size': notional / target_entry,
            'remaining_size': notional / target_entry,
            'initial_risk': abs(target_entry - initial_sl),
            'is_breakeven': False,
            'tp_hit_count': 0,
            'max_price': target_entry,
            'atr': signal.indicators.get('atr', 0),
            'timestamp': signal.generated_at
        }

    def update(self, candle_map: Dict[str, Candle], timestamp: datetime):
        for symbol, candle in candle_map.items():
            self._process_symbol(symbol, candle, timestamp)
            
        unrealized_pnl = 0.0
        for sym, pos in self.positions.items():
            current_price = candle_map[sym].close if sym in candle_map else pos['entry_price']
            if pos['side'] == 'LONG':
                pnl = (current_price - pos['entry_price']) * pos['remaining_size']
            else:
                pnl = (pos['entry_price'] - current_price) * pos['remaining_size']
            unrealized_pnl += pnl
            
        total_equity = self.balance + unrealized_pnl
        self.equity_curve.append({'time': timestamp, 'balance': total_equity})

    def _process_symbol(self, symbol: str, candle: Candle, time: datetime):
        path = [
            ('OPEN', candle.open),
            ('LOW', candle.low) if candle.close >= candle.open else ('HIGH', candle.high),
            ('HIGH', candle.high) if candle.close >= candle.open else ('LOW', candle.low),
            ('CLOSE', candle.close)
        ]
            
        for stage, price in path:
            if symbol in self.pending_orders:
                order = self.pending_orders[symbol]
                is_fill = False
                if order['type'] == 'MARKET':
                    if stage == 'OPEN': is_fill = True
                elif order['type'] == 'LIMIT':
                    if order['side'] == 'LONG' and price <= order['target_price']: is_fill = True
                    elif order['side'] == 'SHORT' and price >= order['target_price']: is_fill = True
                
                if is_fill:
                    volatility = (candle.high - candle.low) / candle.open
                    slippage = self.base_slippage_rate + (volatility * 0.1)
                    self._execute_fill(order, price, time, slippage)
                    del self.pending_orders[symbol]
                    continue

            if symbol in self.positions:
                pos = self.positions[symbol]
                if pos['entry_time'] == time: continue 
                self._update_position_logic(pos, price, time, candle)

    def _update_position_logic(self, pos, price, time, candle):
        side = pos['side']
        symbol = pos['symbol']
        volatility = (candle.high - candle.low) / candle.open
        slippage = self.base_slippage_rate + (volatility * 0.1)
        
        if side == 'LONG': pos['max_price'] = max(pos['max_price'], price)
        else: pos['max_price'] = min(pos['max_price'], price)
            
        # 1. SL/Trailing Check
        sl_hit = (side == 'LONG' and price <= pos['stop_loss']) or \
                 (side == 'SHORT' and price >= pos['stop_loss'])
        if sl_hit:
            # Semantic Labeling
            pnl_approx = (pos['stop_loss'] - pos['entry_price']) if side == 'LONG' else (pos['entry_price'] - pos['stop_loss'])
            reason = "STOP_LOSS"
            if pos['is_breakeven']:
                reason = "TRAILING_STOP" if pnl_approx > 0 else "BREAKEVEN"
                
            self._close_position(symbol, pos['stop_loss'], reason, time, slippage)
            return

        # 2. TP Check
        if pos['tp_hit_count'] == 0:
            tp1 = pos['tp_levels'].get('tp1')
            if tp1:
                tp_hit = (side == 'LONG' and price >= tp1) or (side == 'SHORT' and low <= tp1)
                if tp_hit:
                    self._take_partial_profit(symbol, tp1, 0.6, "TAKE_PROFIT_1", time, slippage)
                    pos['stop_loss'] = pos['entry_price']
                    pos['is_breakeven'] = True

        # 3. Breakeven Trigger
        if not pos['is_breakeven']:
            price_diff = abs(price - pos['entry_price'])
            if price_diff >= (pos['initial_risk'] * self.breakeven_trigger_r):
                buffer = pos['entry_price'] * 0.0005
                pos['stop_loss'] = pos['entry_price'] + buffer if side == 'LONG' else pos['entry_price'] - buffer
                pos['is_breakeven'] = True

        # 4. Trailing Stop Update
        if pos['tp_hit_count'] >= 1 and pos['atr'] > 0:
            trail = pos['atr'] * self.trailing_stop_atr
            if side == 'LONG':
                new_sl = pos['max_price'] - trail
                if new_sl > pos['stop_loss']: pos['stop_loss'] = new_sl
            else:
                new_sl = pos['max_price'] + trail
                if new_sl < pos['stop_loss']: pos['stop_loss'] = new_sl

    def _execute_fill(self, order, price, time, slippage):
        fill_price = price * (1 + slippage) if order['side'] == 'LONG' else price * (1 - slippage)
        size = order['notional'] / fill_price
        self.balance -= order['notional'] * self.commission_rate
        
        self.positions[order['symbol']] = {
            'id': order['id'],
            'symbol': order['symbol'],
            'side': order['side'],
            'entry_price': fill_price,
            'entry_time': time,
            'stop_loss': order['stop_loss'],
            'tp_levels': order['tp_levels'],
            'initial_size': size,
            'remaining_size': size,
            'notional_value': order['notional'],
            'entry_equity': order['entry_equity'], # Fixed logic
            'initial_risk': abs(fill_price - order['stop_loss']),
            'is_breakeven': False,
            'tp_hit_count': 0,
            'max_price': fill_price,
            'atr': order['atr']
        }
        self.logger.debug(f"🚀 FILLED {order['symbol']} {order['side']} @ {fill_price:.2f}")

    def _take_partial_profit(self, symbol, price, pct, reason, time, slippage):
        pos = self.positions[symbol]
        close_size = min(pos['initial_size'] * pct, pos['remaining_size'])
        fill_price = price * (1 - slippage) if pos['side'] == 'LONG' else price * (1 + slippage)
        pnl = ((fill_price - pos['entry_price']) if pos['side'] == 'LONG' else (pos['entry_price'] - fill_price)) * close_size
        fee = (fill_price * close_size) * self.commission_rate
        net_pnl = pnl - fee
        self.balance += net_pnl
        pos['remaining_size'] -= close_size
        pos['tp_hit_count'] += 1
        self._record_trade(pos, fill_price, net_pnl, reason, time, close_size)

    def _close_position(self, symbol, price, reason, time, slippage):
        pos = self.positions[symbol]
        remaining = pos['remaining_size']
        fill_price = price * (1 - slippage) if pos['side'] == 'LONG' else price * (1 + slippage)
        pnl = ((fill_price - pos['entry_price']) if pos['side'] == 'LONG' else (pos['entry_price'] - fill_price)) * remaining
        fee = (fill_price * remaining) * self.commission_rate
        net_pnl = pnl - fee
        self.balance += net_pnl
        self._record_trade(pos, fill_price, net_pnl, reason, time, remaining)
        del self.positions[symbol]

    def _record_trade(self, pos, exit_price, pnl, reason, time, size):
        pct_of_original = size / pos['initial_size']
        # Fixed: Leverage is calculated against EQUITY AT ENTRY
        leverage = pos['notional_value'] / pos['entry_equity'] if pos['entry_equity'] > 0 else 0
        
        trade = BacktestTrade(
            trade_id=pos['id'],
            symbol=pos['symbol'],
            side=pos['side'],
            entry_price=pos['entry_price'],
            exit_price=exit_price,
            entry_time=pos['entry_time'],
            exit_time=time,
            pnl_usd=pnl,
            pnl_pct=(pnl / (pos['notional_value'] * pct_of_original)) * 100 if pct_of_original > 0 else 0,
            exit_reason=reason,
            position_size=size,
            notional_value=pos['notional_value'] * pct_of_original,
            leverage_at_entry=leverage
        )
        self.trades.append(trade)

    def get_stats(self) -> Dict[str, Any]:
        if not self.trades:
            return {
                "initial_balance": self.initial_balance,
                "final_balance": self.balance,
                "net_return_usd": 0.0,
                "net_return_pct": 0.0,
                "total_trades": 0,
                "win_rate": 0.0,
                "winning_trades": 0,
                "losing_trades": 0
            }
        winning_trades = [t for t in self.trades if t.pnl_usd > 0]
        total_pnl = sum(t.pnl_usd for t in self.trades)
        return {
            "initial_balance": self.initial_balance,
            "final_balance": self.balance,
            "net_return_usd": total_pnl,
            "net_return_pct": (total_pnl / self.initial_balance) * 100,
            "total_trades": len(self.trades),
            "win_rate": (len(winning_trades) / len(self.trades)) * 100,
            "winning_trades": len(winning_trades),
            "losing_trades": len(self.trades) - len(winning_trades)
        }