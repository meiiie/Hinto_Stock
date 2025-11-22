"""
Home Page - Real-time Trading Dashboard

Displays real-time price, RSI, volume, signals, and connection status.
"""

import streamlit as st
import time
from datetime import datetime


def render():
    """Render the home page"""
    
    st.title("🏠 Real-time Trading Dashboard")
    st.markdown("---")
    
    # Get service from session state
    service = st.session_state.get('service', None)
    
    if not service:
        st.error("❌ Real-time Service not initialized")
        st.info("💡 The service should initialize automatically. If you see this message, there may be an error.")
        
        # Show initialization button
        if st.button("🔄 Try Initialize Service"):
            try:
                from src.application.services.realtime_service import RealtimeService
                st.session_state.service = RealtimeService()
                st.success("✅ Service initialized!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Failed to initialize: {e}")
                import traceback
                st.code(traceback.format_exc())
        return
    
    # Check if service is running
    if not service.is_running():
        st.warning("⚠️ Real-time Service is not running")
        st.info("Click the button below to start collecting real-time data from Binance")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("▶️ Start Service", use_container_width=True, type="primary"):
                try:
                    with st.spinner("Starting service..."):
                        # Check if service is async (RealtimeService) or threaded (ThreadedRealtimeService)
                        import asyncio
                        if asyncio.iscoroutinefunction(service.start):
                            asyncio.run(service.start())
                        else:
                            service.start()
                    st.success("✅ Service started! Data will appear shortly.")
                    time.sleep(2)
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Failed to start service: {e}")
                    import traceback
                    st.code(traceback.format_exc())
        
        with col2:
            st.info("📡 Service will connect to Binance WebSocket and start collecting BTC/USDT data")
        
        return
    
    # Service is running - show data
    st.success("✅ Service is running")
    
    try:
        # Get status
        status = service.get_status()
        connection = status.get('connection', {})
        data = status.get('data', {})
        
        # Connection status
        st.subheader("📡 Connection Status")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            is_connected = connection.get('is_connected', False)
            if is_connected:
                st.success("🟢 Connected")
            else:
                st.error("🔴 Disconnected")
        
        with col2:
            latency = connection.get('latency_ms', 0)
            st.metric("Latency", f"{latency}ms")
        
        with col3:
            reconnects = connection.get('reconnect_count', 0)
            st.metric("Reconnections", reconnects)
        
        st.markdown("---")
        
        # Data statistics
        st.subheader("📊 Data Collection")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            candles_1m = data.get('1m_candles', 0)
            st.metric("1m Candles", candles_1m)
            if candles_1m > 0:
                st.caption("✅ Collecting real-time data")
            else:
                st.caption("⏳ Waiting for data...")
        
        with col2:
            candles_15m = data.get('15m_candles', 0)
            st.metric("15m Candles", candles_15m)
            if candles_15m > 0:
                st.caption("✅ Aggregation working")
            else:
                st.caption("⏳ Need 15 minutes")
        
        with col3:
            candles_1h = data.get('1h_candles', 0)
            st.metric("1h Candles", candles_1h)
            if candles_1h > 0:
                st.caption("✅ Aggregation working")
            else:
                st.caption("⏳ Need 1 hour")
        
        st.markdown("---")
        
        # Latest data
        if candles_1m > 0:
            st.subheader("💰 Latest Price Data")
            latest = service.get_latest_data('1m')
            
            if latest:
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Price", f"${latest.close:,.2f}")
                
                with col2:
                    # Show 1m volume with clarification
                    st.metric("Volume (1m)", f"{latest.volume:.2f} BTC")
                    st.caption("Current candle volume")
                
                # Get latest indicators once
                indicators = service.get_latest_indicators('1m')
                
                with col3:
                    # VWAP & Bollinger Bands
                    if indicators and 'vwap' in indicators:
                        vwap_val = indicators['vwap']
                        st.metric("VWAP", f"${vwap_val:,.2f}")
                        
                        # Check deviation
                        if latest.close > vwap_val:
                            st.caption("🟢 Bullish (> VWAP)")
                        else:
                            st.caption("🔴 Bearish (< VWAP)")
                    else:
                        st.metric("VWAP", "Calculating...")
                
                with col4:
                    # StochRSI
                    if indicators and 'stoch_rsi' in indicators:
                        stoch = indicators['stoch_rsi']
                        k = stoch.get('k', 0)
                        d = stoch.get('d', 0)
                        st.metric("StochRSI (K/D)", f"{k:.1f} / {d:.1f}")
                        
                        if k < 0.1:
                            st.caption("🔴 **EXTREME OVERSOLD**")
                        elif k < 20:
                            st.caption("🟢 Oversold")
                        elif k > 80:
                            st.caption("🔴 Overbought")
                        else:
                            st.caption("⚪ Neutral")
                    else:
                        st.metric("StochRSI", "Calculating...")
                
                st.caption(f"Last update: {latest.timestamp.strftime('%H:%M:%S')}")
                
                # Additional metrics
                st.markdown("---")
                st.subheader("📊 Extended Metrics")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    # Bollinger Bands Status
                    if indicators and 'bollinger' in indicators:
                        bb = indicators['bollinger']
                        upper = bb.get('upper_band', 0)
                        lower = bb.get('lower_band', 0)
                        bandwidth = ((upper - lower) / lower) * 100
                        
                        st.metric("BB Bandwidth", f"{bandwidth:.2f}%")
                        
                        # Check touch
                        if latest.close >= upper:
                            st.caption("🔴 Touching Upper")
                        elif latest.close <= lower:
                            st.caption("🟢 Touching Lower")
                        else:
                            st.caption("⚪ Inside Bands")
                    else:
                        st.metric("BB Status", "Calculating...")
                
                with col2:
                    # Volume Analysis
                    candles_for_volume = service.get_candles('1m', limit=20)
                    if len(candles_for_volume) > 0:
                        avg_vol = sum(c.volume for c in candles_for_volume) / len(candles_for_volume)
                        vol_ratio = latest.volume / avg_vol if avg_vol > 0 else 0
                        
                        st.metric("Volume Ratio", f"{vol_ratio:.2f}x")
                        if vol_ratio > 2.0:
                            st.caption("🚀 Spike Detected")
                        else:
                            st.caption("Normal Volume")
                    else:
                        st.metric("Volume Ratio", "Calculating...")
                
                with col3:
                    # Price change
                    candles = service.get_candles('1m', limit=60)
                    if len(candles) >= 2:
                        first_price = candles[0].close
                        last_price = candles[-1].close
                        change = last_price - first_price
                        change_pct = (change / first_price) * 100
                        st.metric(
                            f"Change (1h)",
                            f"${change:,.2f}",
                            f"{change_pct:+.2f}%"
                        )
                    else:
                        st.metric("Change", "Calculating...")
                
            else:
                st.info("⏳ Waiting for first candle...")
        else:
            st.info("⏳ Waiting for data... This may take 1-2 minutes for the first candle.")
        
        st.markdown("---")
        
        # Trading signals
        st.subheader("🚨 Trading Signals")
        
        # Get actual signal object
        latest_signal = service.get_current_signals()
        
        if latest_signal:
            # Create a nice display for the signal
            signal_type = latest_signal.signal_type.value.upper()
            color = "green" if signal_type == "BUY" else "red" if signal_type == "SELL" else "gray"
            
            st.markdown(f"""
            <div style="padding: 10px; border-radius: 5px; border: 1px solid {color}; background-color: rgba(0,0,0,0.1);">
                <h3 style="color: {color}; margin: 0;">{signal_type} SIGNAL</h3>
                <p style="margin: 0;">Price: <strong>${latest_signal.price:,.2f}</strong> | Confidence: <strong>{latest_signal.confidence:.0%}</strong></p>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**🎯 Entry**")
                if latest_signal.entry_price:
                    st.markdown(f"**${latest_signal.entry_price:,.2f}**")
                else:
                    st.markdown("Market")
                    
            with col2:
                st.markdown("**🛑 Stop Loss**")
                if latest_signal.stop_loss:
                    st.markdown(f"**${latest_signal.stop_loss:,.2f}**")
                    dist = abs(latest_signal.price - latest_signal.stop_loss) / latest_signal.price
                    st.caption(f"Risk: {dist:.2%}")
                else:
                    st.markdown("N/A")
            
            with col3:
                st.markdown("**💰 Take Profit**")
                if latest_signal.tp_levels:
                    tp1 = latest_signal.tp_levels.get('tp1', 0)
                    tp2 = latest_signal.tp_levels.get('tp2', 0)
                    tp3 = latest_signal.tp_levels.get('tp3', 0)
                    st.markdown(f"TP1: ${tp1:,.2f}")
                    st.caption(f"TP2: ${tp2:,.2f} | TP3: ${tp3:,.2f}")
                else:
                    st.markdown("N/A")
            
            # Reasons
            with st.expander("Analysis Details", expanded=True):
                for reason in latest_signal.reasons:
                    st.markdown(f"- {reason}")
                
                if latest_signal.risk_reward_ratio:
                    st.markdown(f"**R:R Ratio:** {latest_signal.risk_reward_ratio:.2f}")
                
                if latest_signal.position_size:
                    st.markdown(f"**Rec. Position:** {latest_signal.position_size:.4f} BTC")

        else:
            st.info("⏳ No active signals. Waiting for market conditions...")
            st.caption("Signals will appear here when detected.")
        
        st.markdown("---")
        
        # Auto-refresh controls
        st.subheader("🔄 Auto-refresh")
        col1, col2 = st.columns(2)
        
        with col1:
            auto_refresh = st.checkbox(
                "Enable auto-refresh",
                value=st.session_state.get('auto_refresh', True),
                key="auto_refresh_toggle"
            )
            st.session_state.auto_refresh = auto_refresh
        
        with col2:
            if auto_refresh:
                interval = st.selectbox(
                    "Refresh interval (seconds)",
                    options=[1, 2, 5, 10],
                    index=0,
                    key="refresh_interval_select"
                )
                st.session_state.refresh_interval = interval
        
        # Auto-refresh logic
        if auto_refresh:
            time.sleep(st.session_state.get('refresh_interval', 1))
            st.rerun()
        
        # Footer
        st.markdown("---")
        st.caption(f"Last refresh: {datetime.now().strftime('%H:%M:%S')}")
        st.caption("💡 Tip: Disable auto-refresh to interact with controls")
        
    except Exception as e:
        st.error(f"❌ Error displaying data: {e}")
        import traceback
        with st.expander("Show error details"):
            st.code(traceback.format_exc())
