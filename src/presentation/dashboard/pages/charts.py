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
        
        # Get calculated indicators
        indicators_15m = service.get_latest_indicators('15m')
        indicators_1h = service.get_latest_indicators('1h')
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**15-Minute Timeframe**")
            if candles_15m:
                latest_15m = candles_15m[-1]
                
                col_a, col_b = st.columns(2)
                with col_a:
                    st.metric("Price", f"${latest_15m.close:,.2f}")
                    # StochRSI from indicators
                    stoch = indicators_15m.get('stoch_rsi', {})
                    if stoch:
                        k = stoch.get('k', 0)
                        d = stoch.get('d', 0)
                        status = "EXTREME OVERSOLD" if k < 0.1 else "Overbought" if k > 80 else "Oversold" if k < 20 else "Neutral"
                        st.metric("StochRSI", f"{k:.1f}/{d:.1f}", status)
                    else:
                        st.metric("StochRSI", "Calculating...")
                
                with col_b:
                    # VWAP Distance
                    vwap = indicators_15m.get('vwap', 0)
                    if vwap > 0:
                        dist = (latest_15m.close - vwap) / vwap
                        st.metric("VWAP Dist", f"{dist:.2%}")
                    else:
                        st.metric("VWAP Dist", "N/A")
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
                    # StochRSI from indicators
                    stoch = indicators_1h.get('stoch_rsi', {})
                    if stoch:
                        k = stoch.get('k', 0)
                        d = stoch.get('d', 0)
                        status = "EXTREME OVERSOLD" if k < 0.1 else "Overbought" if k > 80 else "Oversold" if k < 20 else "Neutral"
                        st.metric("StochRSI", f"{k:.1f}/{d:.1f}", status)
                    else:
                        st.metric("StochRSI", "Calculating...")
                
                with col_b:
                    # VWAP Distance
                    vwap = indicators_1h.get('vwap', 0)
                    if vwap > 0:
                        dist = (latest_1h.close - vwap) / vwap
                        st.metric("VWAP Dist", f"{dist:.2%}")
                    else:
                        st.metric("VWAP Dist", "N/A")
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
        st.caption("• VWAP - Volume Weighted Average Price (Orange)")
        st.caption("• Bollinger Bands (Shaded Blue)")
        st.caption("• StochRSI (Blue/Red lines in subplot)")
        st.caption("• Volume with MA(20) and spike detection")
        st.caption("• Smart Entry & TP/SL levels (when active)")
    
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

