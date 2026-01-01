"""
Circuit Breaker - Risk Management Layer

Prevents overtrading and revenge trading after consecutive losses.
SOTA Principle: Stop trading after 2 losses for 12 hours.
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional

class CircuitBreaker:
    def __init__(self, max_consecutive_losses: int = 2, cooldown_hours: int = 12):
        # Per symbol, per direction tracking
        self.state: Dict[str, Dict[str, Any]] = {} 
        self.max_losses = max_consecutive_losses
        self.cooldown_hours = cooldown_hours
        self.logger = logging.getLogger(__name__)

    def _get_state(self, symbol: str):
        if symbol not in self.state:
            self.state[symbol] = {
                'LONG': {'losses': 0, 'blocked_until': None},
                'SHORT': {'losses': 0, 'blocked_until': None}
            }
        return self.state[symbol]

    def record_trade(self, symbol: str, side: str, pnl_usd: float):
        state = self._get_state(symbol)[side]
        
        if pnl_usd > 0:
            state['losses'] = 0
            state['blocked_until'] = None
        else:
            state['losses'] += 1
            if state['losses'] >= self.max_losses:
                unblock_time = datetime.now(timezone.utc) + timedelta(hours=self.cooldown_hours)
                state['blocked_until'] = unblock_time
                self.logger.warning(f"🚨 CIRCUIT BREAKER for {symbol} {side}: Blocked until {unblock_time}")

    def is_blocked(self, symbol: str, side: str, current_time: datetime) -> bool:
        state = self._get_state(symbol).get(side)
        if not state: return False
        
        blocked_until = state['blocked_until']
        if blocked_until and current_time < blocked_until:
            return True
        return False
