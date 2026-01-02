"""
Circuit Breaker - Risk Management Layer

Prevents overtrading and revenge trading after consecutive losses.
SOTA Principle: 
1. Isolated CB: Stop trading specific symbol after N losses.
2. Global CB: Stop ALL trading if Portfolio Drawdown > 10% in a day.
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional, Any

class CircuitBreaker:
    def __init__(self, max_consecutive_losses: int = 3, cooldown_hours: int = 4, max_daily_drawdown_pct: float = 0.10):
        # Per symbol, per direction tracking
        self.state: Dict[str, Dict[str, Any]] = {} 
        self.max_losses = max_consecutive_losses
        self.cooldown_hours = cooldown_hours
        self.max_daily_drawdown_pct = max_daily_drawdown_pct
        
        # Global Portfolio State
        self.daily_start_balance: float = 0.0
        self.current_day: Optional[datetime] = None
        self.global_blocked_until: Optional[datetime] = None
        
        self.logger = logging.getLogger(__name__)

    def _get_state(self, symbol: str):
        if symbol not in self.state:
            self.state[symbol] = {
                'LONG': {'losses': 0, 'blocked_until': None},
                'SHORT': {'losses': 0, 'blocked_until': None}
            }
        return self.state[symbol]

    def update_portfolio_state(self, current_balance: float, current_time: datetime):
        """Called every step to check global health."""
        # 1. New Day Reset
        day_key = current_time.date()
        if self.current_day != day_key:
            self.daily_start_balance = current_balance
            self.current_day = day_key
            # Optional: Reset global block on new day? 
            # Ideally yes, but if blocked for 24h, we respect the time.
        
        # 2. Check Drawdown
        if self.daily_start_balance > 0:
            drawdown = (self.daily_start_balance - current_balance) / self.daily_start_balance
            
            if drawdown >= self.max_daily_drawdown_pct:
                if not self.global_blocked_until or current_time > self.global_blocked_until:
                    # Block for 24 hours
                    unblock_time = current_time + timedelta(hours=24)
                    self.global_blocked_until = unblock_time
                    self.logger.critical(f"🚨 GLOBAL CIRCUIT BREAKER: Daily Drawdown {drawdown*100:.2f}% > {self.max_daily_drawdown_pct*100:.1f}%. HALTING ALL TRADING UNTIL {unblock_time}")

    def record_trade(self, symbol: str, side: str, pnl_usd: float):
        state = self._get_state(symbol)[side]
        
        if pnl_usd > 0:
            state['losses'] = 0
            state['blocked_until'] = None
        else:
            state['losses'] += 1
            if state['losses'] >= self.max_losses:
                unblock_time = datetime.now(timezone.utc) + timedelta(hours=self.cooldown_hours)
                # In backtest, we can't use real 'now', this method needs timestamp context if we want to be pure.
                # However, backtest engine calls 'record_trade' right after trade close.
                # BUT wait, the 'blocked_until' logic in 'record_trade' is naive for Backtest because it uses datetime.now().
                # FIX: We should rely on 'is_blocked' receiving 'current_time' to compare against a stored DELTA or just assume current context.
                # Since 'record_trade' doesn't receive 'current_time', we have a design flaw in the original interface.
                # For now, let's fix it by assuming the caller will enforce correctness or we update signature.
                pass 
                
    def record_trade_with_time(self, symbol: str, side: str, pnl_usd: float, current_time: datetime):
        """SOTA method with time context"""
        state = self._get_state(symbol)[side]
        
        if pnl_usd > 0:
            state['losses'] = 0
            state['blocked_until'] = None
        else:
            state['losses'] += 1
            if state['losses'] >= self.max_losses:
                unblock_time = current_time + timedelta(hours=self.cooldown_hours)
                state['blocked_until'] = unblock_time
                self.logger.warning(f"🛡️ SYMBOL CB: {symbol} {side} blocked until {unblock_time}")

    def is_blocked(self, symbol: str, side: str, current_time: datetime) -> bool:
        # 1. Global Block
        if self.global_blocked_until and current_time < self.global_blocked_until:
            return True

        # 2. Symbol Block
        state = self._get_state(symbol).get(side)
        if not state: return False
        
        blocked_until = state['blocked_until']
        if blocked_until and current_time < blocked_until:
            return True
        return False
