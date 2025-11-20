"""
Dashboard Configuration

Configuration files for the dashboard UI.
"""

from .theme_config import *

__all__ = [
    'BACKGROUND_PRIMARY',
    'BACKGROUND_SECONDARY',
    'COLOR_BULLISH',
    'COLOR_BEARISH',
    'RSI_STRONG_OVERBOUGHT',
    'RSI_OVERBOUGHT',
    'RSI_NEUTRAL',
    'RSI_OVERSOLD',
    'RSI_STRONG_OVERSOLD',
    'CUSTOM_CSS',
    'get_price_color',
    'get_rsi_color',
    'get_volume_color',
    'format_price',
    'format_volume',
    'format_percentage'
]
