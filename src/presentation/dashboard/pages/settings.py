"""
Settings Page - Configuration and Controls

Provides pipeline controls, dashboard preferences, and system information.
"""

import streamlit as st
import sys


def render():
    """Render the settings page"""
    
    st.title("⚙️ Settings")
    st.markdown("---")
    
    # Pipeline Controls
    st.subheader("🔧 Pipeline Controls")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("▶️ Start Pipeline", use_container_width=True):
            st.success("Pipeline started!")
    
    with col2:
        if st.button("⏸️ Stop Pipeline", use_container_width=True):
            st.warning("Pipeline stopped!")
    
    with col3:
        if st.button("🔄 Trigger Update", use_container_width=True):
            st.info("Update triggered!")
    
    st.markdown("---")
    
    # Dashboard Preferences
    st.subheader("🎨 Dashboard Preferences")
    
    col1, col2 = st.columns(2)
    
    with col1:
        default_timeframe = st.selectbox(
            "Default Timeframe",
            ["15m", "1h"],
            index=0
        )
        
        auto_refresh = st.checkbox("Enable Auto-Refresh", value=True)
        
        if auto_refresh:
            refresh_interval = st.slider(
                "Refresh Interval (seconds)",
                min_value=5,
                max_value=60,
                value=15,
                step=5
            )
    
    with col2:
        chart_theme = st.selectbox(
            "Chart Theme",
            ["Dark", "Light"],
            index=0
        )
        
        show_indicators = st.multiselect(
            "Show Indicators",
            ["EMA(7)", "RSI(6)", "Volume MA(20)"],
            default=["EMA(7)", "RSI(6)", "Volume MA(20)"]
        )
    
    if st.button("💾 Save Preferences", use_container_width=True):
        st.success("Preferences saved!")
    
    st.markdown("---")
    
    # System Information
    st.subheader("ℹ️ System Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Environment**")
        st.text(f"Python Version: {sys.version.split()[0]}")
        st.text("Streamlit Version: 1.28.0")
        st.text("Plotly Version: 5.17.0")
    
    with col2:
        st.markdown("**Database**")
        st.text("Database: crypto_data.db")
        st.text("Size: 2.5 MB")
        st.text("Location: ./crypto_data.db")
    
    st.markdown("---")
    
    # Advanced Settings
    with st.expander("🔬 Advanced Settings"):
        st.warning("⚠️ Advanced settings - use with caution")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.number_input("API Request Timeout (s)", value=30, min_value=5, max_value=120)
            st.number_input("Max Records per Query", value=1000, min_value=100, max_value=5000)
        
        with col2:
            st.number_input("Cache TTL (seconds)", value=300, min_value=60, max_value=3600)
            st.checkbox("Enable Debug Logging", value=False)
        
        if st.button("Reset to Defaults"):
            st.info("Settings reset to defaults")
    
    st.info("📝 Settings will be functional once backend integration is complete")
