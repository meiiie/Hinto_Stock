"""
RSI Gauge Component

Displays RSI value with color-coded zones.
"""

import streamlit as st
from typing import List
import plotly.graph_objects as go

from ....domain.entities.candle import Candle
from ....application.analysis.rsi_monitor import RSIMonitor
from ..config.theme_config import (
    RSI_STRONG_OVERSOLD,
    RSI_OVERSOLD,
    RSI_NEUTRAL,
    RSI_OVERBOUGHT,
    RSI_STRONG_OVERBOUGHT
)


def render_rsi_gauge(candles: List[Candle]) -> None:
    """
    Render RSI gauge with color-coded zones.
    
    Args:
        candles: List of recent candles for RSI calculation
    
    Displays:
        - Horizontal gauge with 5 color zones
        - Current RSI value (large)
        - Zone label (Strong Oversold, Oversold, etc.)
        - Alert indicators for extreme zones
    """
    try:
        if not candles or len(candles) < 6:
            st.info("⏳ Waiting for RSI data (need at least 6 candles)...")
            return
        
        # Calculate RSI
        rsi_monitor = RSIMonitor(period=6)
        rsi_analysis = rsi_monitor.analyze(candles)
        
        if not rsi_analysis:
            st.warning("⚠️ Unable to calculate RSI")
            return
        
        rsi_value = rsi_analysis.current_value
        zone = rsi_analysis.zone
        
        # Determine zone color
        if rsi_value >= 80:
            zone_color = RSI_STRONG_OVERBOUGHT
            zone_label = "🔴 Strong Overbought"
            alert_emoji = "🚨"
        elif rsi_value >= 70:
            zone_color = RSI_OVERBOUGHT
            zone_label = "🟠 Overbought"
            alert_emoji = "⚠️"
        elif rsi_value >= 30:
            zone_color = RSI_NEUTRAL
            zone_label = "🟡 Neutral"
            alert_emoji = ""
        elif rsi_value >= 20:
            zone_color = RSI_OVERSOLD
            zone_label = "🟢 Oversold"
            alert_emoji = "⚠️"
        else:
            zone_color = RSI_STRONG_OVERSOLD
            zone_label = "🔵 Strong Oversold"
            alert_emoji = "🚨"
        
        # Create Plotly gauge
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=rsi_value,
            domain={'x': [0, 1], 'y': [0, 1]},
            number={'font': {'size': 40}},
            gauge={
                'axis': {
                    'range': [0, 100],
                    'tickwidth': 1,
                    'tickcolor': "darkgray"
                },
                'bar': {'color': zone_color, 'thickness': 0.75},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, 20], 'color': RSI_STRONG_OVERSOLD},
                    {'range': [20, 30], 'color': RSI_OVERSOLD},
                    {'range': [30, 70], 'color': RSI_NEUTRAL},
                    {'range': [70, 80], 'color': RSI_OVERBOUGHT},
                    {'range': [80, 100], 'color': RSI_STRONG_OVERBOUGHT}
                ],
                'threshold': {
                    'line': {'color': "black", 'width': 2},
                    'thickness': 0.75,
                    'value': rsi_value
                }
            }
        ))
        
        fig.update_layout(
            height=250,
            margin=dict(l=20, r=20, t=40, b=20),
            paper_bgcolor="white",
            font={'color': "black", 'family': "Arial"}
        )
        
        # Display title
        st.markdown("### RSI(6) Monitor")
        
        # Display gauge
        st.plotly_chart(fig, use_container_width=True)
        
        # Display zone label with alert
        zone_html = f"""
        <div style="text-align: center; font-size: 20px; font-weight: 600; color: {zone_color}; margin-top: -10px;">
            {alert_emoji} {zone_label}
        </div>
        """
        st.markdown(zone_html, unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"❌ Error loading RSI gauge: {e}")


def render_rsi_simple(candles: List[Candle]) -> None:
    """
    Render simple RSI display without gauge (for compact spaces).
    
    Args:
        candles: List of recent candles for RSI calculation
    """
    try:
        if not candles or len(candles) < 6:
            st.caption("⏳ RSI: Calculating...")
            return
        
        # Calculate RSI
        rsi_monitor = RSIMonitor(period=6)
        rsi_analysis = rsi_monitor.analyze(candles)
        
        if not rsi_analysis:
            st.caption("⚠️ RSI: N/A")
            return
        
        rsi_value = rsi_analysis.current_value
        
        # Determine zone
        if rsi_value >= 80:
            zone_label = "Strong OB"
            zone_color = RSI_STRONG_OVERBOUGHT
        elif rsi_value >= 70:
            zone_label = "Overbought"
            zone_color = RSI_OVERBOUGHT
        elif rsi_value >= 30:
            zone_label = "Neutral"
            zone_color = RSI_NEUTRAL
        elif rsi_value >= 20:
            zone_label = "Oversold"
            zone_color = RSI_OVERSOLD
        else:
            zone_label = "Strong OS"
            zone_color = RSI_STRONG_OVERSOLD
        
        # Display as metric
        st.metric(
            label="RSI(6)",
            value=f"{rsi_value:.1f}",
            delta=zone_label
        )
        
    except Exception as e:
        st.caption(f"❌ RSI error: {e}")


def render_rsi_horizontal_bar(candles: List[Candle]) -> None:
    """
    Render RSI as horizontal bar with zones.
    
    Args:
        candles: List of recent candles for RSI calculation
    """
    try:
        if not candles or len(candles) < 6:
            st.info("⏳ Calculating RSI...")
            return
        
        # Calculate RSI
        rsi_monitor = RSIMonitor(period=6)
        rsi_analysis = rsi_monitor.analyze(candles)
        
        if not rsi_analysis:
            st.warning("⚠️ RSI unavailable")
            return
        
        rsi_value = rsi_analysis.current_value
        
        # Determine color
        if rsi_value >= 80:
            color = RSI_STRONG_OVERBOUGHT
        elif rsi_value >= 70:
            color = RSI_OVERBOUGHT
        elif rsi_value >= 30:
            color = RSI_NEUTRAL
        elif rsi_value >= 20:
            color = RSI_OVERSOLD
        else:
            color = RSI_STRONG_OVERSOLD
        
        st.markdown("**RSI(6)**")
        
        # Display value
        st.markdown(f"<div style='font-size: 24px; font-weight: 700; color: {color};'>{rsi_value:.1f}</div>", 
                   unsafe_allow_html=True)
        
        # Progress bar
        st.progress(rsi_value / 100)
        
        # Zone markers
        st.caption("← 20 (Strong OS) | 30 (OS) | 70 (OB) | 80 (Strong OB) →")
        
    except Exception as e:
        st.error(f"❌ Error: {e}")
