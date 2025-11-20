"""
Monitoring Page - Real-time System Status

Displays real-time service status, connection info, and data statistics.
"""

import streamlit as st
from datetime import datetime

from src.presentation.dashboard.components import (
    render_connection_status,
    render_service_status_card
)
from src.presentation.dashboard.utils import get_service


def render():
    """Render the monitoring page"""
    
    st.title("🔍 System Monitoring")
    st.markdown("---")
    
    # Get service from session state
    service = get_service()
    
    if not service:
        st.error("❌ Real-time Service not initialized")
        st.info("💡 Please restart the dashboard")
        return
    
    # Service Status Card
    render_service_status_card(service)
    
    st.markdown("---")
    
    # Connection Details
    st.subheader("📡 Connection Details")
    render_connection_status(service)
    
    st.markdown("---")
    
    # Data Flow Statistics
    st.subheader("📊 Data Flow Statistics")
    
    status = service.get_status()
    data = status.get('data', {})
    connection = status.get('connection', {})
    
    # Candle counts
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**1-Minute Candles**")
        candles_1m = data.get('1m_candles', 0)
        st.metric("Count", candles_1m)
        
        latest_1m = data.get('latest_1m')
        if latest_1m:
            st.caption(f"Latest: {latest_1m.strftime('%H:%M:%S')}")
        else:
            st.caption("Latest: N/A")
    
    with col2:
        st.markdown("**15-Minute Candles**")
        candles_15m = data.get('15m_candles', 0)
        st.metric("Count", candles_15m)
        
        latest_15m = data.get('latest_15m')
        if latest_15m:
            st.caption(f"Latest: {latest_15m.strftime('%H:%M:%S')}")
        else:
            st.caption("Latest: N/A")
    
    with col3:
        st.markdown("**1-Hour Candles**")
        candles_1h = data.get('1h_candles', 0)
        st.metric("Count", candles_1h)
        
        latest_1h = data.get('latest_1h')
        if latest_1h:
            st.caption(f"Latest: {latest_1h.strftime('%H:%M:%S')}")
        else:
            st.caption("Latest: N/A")
    
    st.markdown("---")
    
    # Connection Metrics
    st.subheader("🔌 Connection Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        is_connected = connection.get('is_connected', False)
        if is_connected:
            st.metric("Status", "🟢 Connected")
        else:
            st.metric("Status", "🔴 Disconnected")
    
    with col2:
        state = connection.get('state', 'unknown')
        st.metric("State", state.upper())
    
    with col3:
        latency_ms = connection.get('latency_ms', 0)
        st.metric("Latency", f"{latency_ms}ms")
        
        if latency_ms > 5000:
            st.warning("⚠️ High latency")
        elif latency_ms > 2000:
            st.info("ℹ️ Moderate latency")
    
    with col4:
        reconnect_count = connection.get('reconnect_count', 0)
        st.metric("Reconnections", reconnect_count)
        
        if reconnect_count > 5:
            st.warning("⚠️ Unstable connection")
    
    st.markdown("---")
    
    # Service Health
    st.subheader("💚 Service Health")
    
    is_running = status.get('is_running', False)
    
    if is_running:
        st.success("✅ Service is running")
        
        # Calculate uptime (simplified - would need start time tracking)
        st.caption("Service is operational and processing data")
        
        # Data flow health
        if candles_1m > 0:
            st.info(f"📈 Receiving data: {candles_1m} candles collected")
        else:
            st.warning("⚠️ No data received yet")
        
        # Connection health
        if is_connected and latency_ms < 2000:
            st.success("🔗 Connection is healthy")
        elif is_connected:
            st.warning("⚠️ Connection is slow")
        else:
            st.error("❌ Connection lost")
    else:
        st.error("❌ Service is not running")
        st.info("💡 Start the service from the Home page")
    
    st.markdown("---")
    
    # Signals Status
    st.subheader("🚨 Signals Status")
    
    signals = status.get('signals', {})
    latest_signal = signals.get('latest')
    
    if latest_signal:
        st.info(f"Latest Signal: {latest_signal}")
    else:
        st.caption("No active signals")
    
    st.markdown("---")
    
    # System Information
    st.subheader("ℹ️ System Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Service Configuration**")
        st.caption(f"• Symbol: BTCUSDT")
        st.caption(f"• Interval: 1m")
        st.caption(f"• Buffer Size: 100 candles")
        st.caption(f"• RSI Period: 6")
        st.caption(f"• Volume MA Period: 20")
    
    with col2:
        st.markdown("**Timeframes**")
        st.caption("• 1-minute (real-time)")
        st.caption("• 15-minute (aggregated)")
        st.caption("• 1-hour (aggregated)")
    
    st.markdown("---")
    
    # Refresh info
    st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    st.caption("💡 This page shows real-time service status")
    
    # Auto-refresh button
    if st.button("🔄 Refresh Now", use_container_width=True):
        st.rerun()

