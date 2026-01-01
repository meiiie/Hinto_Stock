"""
HTF Trend Filter - Application Layer

Determines the Higher Timeframe bias using EMA200 logic.
SOTA Principle: Never fight the H4 trend.
"""

import logging
import pandas as pd
from typing import List, Dict, Optional
from ...domain.entities.candle import Candle

class TrendFilter:
    """
    Analyzes HTF (Higher Timeframe) data to provide a trading bias.
    """
    def __init__(self, ema_period: int = 200):
        self.ema_period = ema_period
        self.logger = logging.getLogger(__name__)

    def calculate_bias(self, htf_candles: List[Candle]) -> str:
        """
        Returns 'BULLISH', 'BEARISH', or 'NEUTRAL'.
        """
        if len(htf_candles) < self.ema_period:
            return 'NEUTRAL'
            
        # Convert to DataFrame for calculation
        df = pd.DataFrame([{'close': c.close} for c in htf_candles])
        ema = df['close'].ewm(span=self.ema_period, adjust=False).mean()
        
        current_price = htf_candles[-1].close
        current_ema = ema.iloc[-1]
        
        # SOTA: Add a small buffer (0.5%) to avoid whipsaws around EMA
        buffer = current_ema * 0.005 
        
        if current_price > (current_ema + buffer):
            return 'BULLISH'
        elif current_price < (current_ema - buffer):
            return 'BEARISH'
        else:
            return 'NEUTRAL'