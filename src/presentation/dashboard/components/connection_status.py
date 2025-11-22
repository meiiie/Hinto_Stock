"""
Connection Status Component

Displays WebSocket connection status and latency.
"""

import streamlit as st
from typing import Dict

from ....application.services.realtime_service import RealtimeService
from ..config.theme_config import (
    STATUS_CONNECTED,
    STATUS_DISCONNECTED,
    STATUS_RECONNECTING
)
from ..utils.formatters import format_latency, format_datetime


def render_connection_status(service: RealtimeService) -> None:
    """
    Render connection status indicator.
    
    Args:
        service: RealtimeService instance
    
    Displays:
        - Connection state (Connected/Disconnected/Reconnecting)
        - Latency in milliseconds
        - Warning if latency > 5000ms
    """
    try:
        # Get service status
        status = service.get_status()
        connection = status.get('connection', {})
        
        is_connected = connection.get('is_connected', False)
        state = connection.get('state', 'disconnected')
        latency_ms = connection.get('latency_ms', 0)
        reconnect_count = connection.get('reconnect_count', 0)
        
        # Determine status color and text
        if is_connected:
            status_color = STATUS_CONNECTED
            status_emoji = "🟢"
            status_text = "Connected"
        elif state == 'reconnecting':
            status_color = STATUS_RECONNECTING
            status_emoji = "🟠"
            status_text = "Reconnecting..."
        else:
            status_color = STATUS_DISCONNECTED
            status_emoji = "🔴"
            status_text = "Disconnected"
        
        # Display connection status
        col1, col2 = st.columns([1, 1])
        
        with col1:
            status_html = f"""
            <div style="display: flex; align-items: center; gap: 8px;">
                <span style="font-size: 24px;">{status_emoji}</span>
                <span style="font-size: 18px; font-weight: 600; color: {status_color};">
                    {status_text}
                </span>
            </div>
            """
            st.markdown(status_html, unsafe_allow_html=True)
        
        with col2:
            # Display latency
            if is_connected:
                # Use absolute value to handle potential timezone differences
                latency_str = format_latency(abs(latency_ms))
                
                # Warning for high latency
                if latency_ms > 5000:
                    st.warning(f"⚠️ High Latency: {latency_str}")
                else:
                    st.metric("Latency", latency_str)
            else:
                st.caption("Latency: N/A")
        
        # Show reconnection count if > 0
        if reconnect_count > 0:
            st.caption(f"Reconnections: {reconnect_count}")
        
    except Exception as e:
        st.error(f"❌ Error loading connection status: {e}")


def render_connection_status_compact(service: RealtimeService) -> None:
    """
    Render compact connection status (for sidebar or small spaces).
    
    Args:
        service: RealtimeService instance
    """
    try:
        status = service.get_status()
        connection = status.get('connection', {})
        
        is_connected = connection.get('is_connected', False)
        latency_ms = connection.get('latency_ms', 0)
        
        if is_connected:
            st.success(f"🟢 Connected ({format_latency(latency_ms)})")
        else:
            st.error("🔴 Disconnected")
            
    except Exception as e:
        st.caption(f"❌ Status error: {e}")


def render_service_status_card(service: RealtimeService) -> None:
    """
    Render detailed service status card.
    
    Args:
        service: RealtimeService instance
    
    Displays:
        - Connection status
        - Data statistics
        - Latest update times
    """
    try:
        status = service.get_status()
        
        st.subheader("📡 Service Status")
        
        # Connection info
        connection = status.get('connection', {})
        is_connected = connection.get('is_connected', False)
        state = connection.get('state', 'unknown')
        latency_ms = connection.get('latency_ms', 0)
        reconnect_count = connection.get('reconnect_count', 0)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if is_connected:
                st.metric("Connection", "🟢 Connected")
            else:
                st.metric("Connection", "🔴 Disconnected")
        
        with col2:
            st.metric("Latency", format_latency(latency_ms))
        
        with col3:
            st.metric("Reconnects", reconnect_count)
        
        # Data statistics
        st.markdown("---")
        st.subheader("📊 Data Statistics")
        
        data = status.get('data', {})
        candles_1m = data.get('1m_candles', 0)
        candles_15m = data.get('15m_candles', 0)
        candles_1h = data.get('1h_candles', 0)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("1m Candles", candles_1m)
        
        with col2:
            st.metric("15m Candles", candles_15m)
        
        with col3:
            st.metric("1h Candles", candles_1h)
        
        # Latest updates
        latest_1m = data.get('latest_1m')
        latest_15m = data.get('latest_15m')
        latest_1h = data.get('latest_1h')
        
        if latest_1m or latest_15m or latest_1h:
            st.markdown("---")
            st.caption("**Latest Updates:**")
            
            if latest_1m:
                st.caption(f"• 1m: {format_datetime(latest_1m)}")
            if latest_15m:
                st.caption(f"• 15m: {format_datetime(latest_15m)}")
            if latest_1h:
                st.caption(f"• 1h: {format_datetime(latest_1h)}")
        
    except Exception as e:
        st.error(f"❌ Error loading service status: {e}")
