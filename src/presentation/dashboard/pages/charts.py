"""
Charts Page - Multi-timeframe Analysis

Displays candlestick charts with technical indicators for multiple timeframes.
"""

import streamlit as st
from datetime import datetime

from src.presentation.dashboard.components import (
    render_multi_chart,
    render_single_chart,
    render_chart_controls
)
from src.presentation.dashboard.utils import get_service


def render():
    """Render the charts page"""
    
    st.title("📊 Multi-timeframe Charts")
    st.markdown("---")
    
    # Get service from session state
    service = get_service()
    
    if not service:
        st.error("❌ Real-time Service not initialized")
        st.info("💡 Please restart the dashboard")
        return
    
    # Check if service is running
    if not service.is_running():
        st.warning("⚠️ Real-time Service is not running")
        st.info("💡 Start the service from the Home page to see charts")
        return
    
    # Chart controls
    st.subheader("⚙️ Chart Controls")
    controls = render_chart_controls()
    
    st.markdown("---")
    
    # Display charts based on selection
    if controls['chart_type'] == "Candlestick":
        # Multi-timeframe view
        st.markdown("### 📊 Side-by-Side Comparison")
        render_multi_chart(service, limit=controls['limit'])
        
        st.markdown("---")
        
        # Technical indicators summary
        st.subheader("📈 Technical Indicators Summary")
        
        # Get latest data for both timeframes
        candles_15m = service.get_candles('15m', 1)
        candles_1h = service.get_candles('1h', 1)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**15-Minute Timeframe**")
            if candles_15m:
                latest_15m = candles_15m[-1]
                
                col_a, col_b = st.columns(2)
                with col_a:
                    st.metric("Price", f"${latest_15m.close:,.2f}")
                    # Calculate RSI from service
                    if len(candles_15m) >= 7:
                        try:
                            rsi_result = service.rsi_monitor.analyze(candles_15m)
                            if rsi_result and rsi_result.rsi_value is not None:
                                rsi_status = "Overbought" if rsi_result.rsi_value > 70 else "Oversold" if rsi_result.rsi_value < 30 else "Neutral"
                                st.metric("RSI(6)", f"{rsi_result.rsi_value:.1f}", rsi_status)
                            else:
                                st.metric("RSI(6)", "Calculating...")
                        except:
                            st.metric("RSI(6)", "N/A")
                    else:
                        st.metric("RSI(6)", "Need more data...")
                
                with col_b:
                    st.metric("EMA Distance", "N/A")
                    st.metric("Volume", f"{latest_15m.volume:.2f} BTC")
            else:
                st.info("⏳ No 15m data yet")
        
        with col2:
            st.markdown("**1-Hour Timeframe**")
            if candles_1h:
                latest_1h = candles_1h[-1]
                
                col_a, col_b = st.columns(2)
                with col_a:
                    st.metric("Price", f"${latest_1h.close:,.2f}")
                    # Calculate RSI from service
                    if len(candles_1h) >= 7:
                        try:
                            rsi_result = service.rsi_monitor.analyze(candles_1h)
                            if rsi_result and rsi_result.rsi_value is not None:
                                rsi_status = "Overbought" if rsi_result.rsi_value > 70 else "Oversold" if rsi_result.rsi_value < 30 else "Neutral"
                                st.metric("RSI(6)", f"{rsi_result.rsi_value:.1f}", rsi_status)
                            else:
                                st.metric("RSI(6)", "Calculating...")
                        except:
                            st.metric("RSI(6)", "N/A")
                    else:
                        st.metric("RSI(6)", "Need more data...")
                
                with col_b:
                    st.metric("EMA Distance", "N/A")
                    st.metric("Volume", f"{latest_1h.volume:.2f} BTC")
            else:
                st.info("⏳ No 1h data yet")
    
    else:
        # Single chart view (Line chart - future enhancement)
        st.info("📈 Line chart view coming soon!")
        st.caption("Currently only candlestick charts are supported")
    
    st.markdown("---")
    
    # Data availability info
    st.subheader("ℹ️ Data Availability")
    
    status = service.get_status()
    data = status.get('data', {})
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        candles_1m = data.get('1m_candles', 0)
        st.metric("1m Candles", candles_1m)
        st.caption("Real-time data")
    
    with col2:
        candles_15m = data.get('15m_candles', 0)
        st.metric("15m Candles", candles_15m)
        if candles_15m == 0:
            st.caption("⏳ Need 15 minutes")
        else:
            st.caption("✅ Available")
    
    with col3:
        candles_1h = data.get('1h_candles', 0)
        st.metric("1h Candles", candles_1h)
        if candles_1h == 0:
            st.caption("⏳ Need 1 hour")
        else:
            st.caption("✅ Available")
    
    # Chart features info
    st.markdown("---")
    st.subheader("📚 Chart Features")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Indicators Displayed:**")
        st.caption("• Candlestick patterns (OHLC)")
        st.caption("• EMA(7) - Fast trend (Blue)")
        st.caption("• EMA(25) - Slow trend (Orange)")
        st.caption("• RSI(6) - Relative Strength Index")
        st.caption("• Volume with MA(20) and spike detection")
        st.caption("• Volume spikes highlighted (Orange bars)")
        st.caption("• Spike threshold line (2x average)")
        st.caption("• Overbought/Oversold levels (70/30)")
    
    with col2:
        st.markdown("**Interactive Features:**")
        st.caption("• Zoom in/out with mouse wheel")
        st.caption("• Pan by dragging")
        st.caption("• Hover for detailed values")
        st.caption("• Toggle indicators on/off")
        st.caption("• Download chart as PNG")
    
    # Footer
    st.markdown("---")
    st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    st.caption("💡 Tip: Charts update automatically as new data arrives")

