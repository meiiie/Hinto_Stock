"""
Price Ticker Component

Displays current BTC/USDT price with real-time updates.
"""

import streamlit as st
from typing import Optional
from datetime import datetime

from ....application.services.realtime_service import RealtimeService
from ....domain.entities.candle import Candle
from ..config.theme_config import COLOR_BULLISH, COLOR_BEARISH, COLOR_NEUTRAL
from ..utils.formatters import format_price, format_percentage, format_timestamp


def render_price_ticker(service: RealtimeService) -> None:
    """
    Render real-time price ticker.
    
    Args:
        service: RealtimeService instance
    
    Displays:
        - Current price (large, color-coded)
        - 24h change percentage
        - Direction arrow (↑/↓)
        - Last update timestamp
    """
    try:
        # Get latest 1m candle
        latest_candle = service.get_latest_data('1m')
        
        if not latest_candle:
            st.info("⏳ Waiting for price data...")
            return
        
        # Get previous candle for comparison
        candles = service.get_candles('1m', 2)
        previous_candle = candles[0] if len(candles) >= 2 else None
        
        # Calculate price change
        current_price = latest_candle.close
        if previous_candle:
            previous_price = previous_candle.close
            price_change = current_price - previous_price
            price_change_pct = (price_change / previous_price) * 100
            is_up = price_change > 0
            is_down = price_change < 0
        else:
            price_change_pct = 0.0
            is_up = False
            is_down = False
        
        # Determine color
        if is_up:
            color = COLOR_BULLISH
            arrow = "↑"
        elif is_down:
            color = COLOR_BEARISH
            arrow = "↓"
        else:
            color = COLOR_NEUTRAL
            arrow = "→"
        
        # Display price ticker
        st.markdown("### BTC/USDT")
        
        # Large price display with color
        price_html = f"""
        <div style="font-size: 48px; font-weight: 700; color: {color}; line-height: 1.2;">
            {format_price(current_price)} {arrow}
        </div>
        """
        st.markdown(price_html, unsafe_allow_html=True)
        
        # Change percentage
        change_html = f"""
        <div style="font-size: 20px; color: {color}; margin-top: 8px;">
            {format_percentage(price_change_pct)}
        </div>
        """
        st.markdown(change_html, unsafe_allow_html=True)
        
        # Last update timestamp
        timestamp_str = format_timestamp(latest_candle.timestamp)
        st.caption(f"Last Update: {timestamp_str}")
        
    except Exception as e:
        st.error(f"❌ Error loading price ticker: {e}")


def render_price_ticker_compact(service: RealtimeService) -> None:
    """
    Render compact price ticker (for sidebar or small spaces).
    
    Args:
        service: RealtimeService instance
    """
    try:
        latest_candle = service.get_latest_data('1m')
        
        if not latest_candle:
            st.caption("⏳ Loading...")
            return
        
        # Get previous candle for comparison
        candles = service.get_candles('1m', 2)
        previous_candle = candles[0] if len(candles) >= 2 else None
        
        # Calculate change
        current_price = latest_candle.close
        if previous_candle:
            previous_price = previous_candle.close
            price_change_pct = ((current_price - previous_price) / previous_price) * 100
            is_up = price_change_pct > 0
        else:
            price_change_pct = 0.0
            is_up = False
        
        # Determine color and arrow
        color = COLOR_BULLISH if is_up else COLOR_BEARISH if price_change_pct < 0 else COLOR_NEUTRAL
        arrow = "↑" if is_up else "↓" if price_change_pct < 0 else "→"
        
        # Compact display
        st.metric(
            label="BTC/USDT",
            value=format_price(current_price),
            delta=f"{arrow} {format_percentage(price_change_pct)}"
        )
        
    except Exception as e:
        st.caption(f"❌ Error: {e}")
