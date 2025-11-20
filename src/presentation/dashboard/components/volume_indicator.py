"""
Volume Indicator Component

Displays volume analysis with spike detection.
"""

import streamlit as st
from typing import List

from ....domain.entities.candle import Candle
from ....application.analysis.volume_analyzer import VolumeAnalyzer
from ..config.theme_config import (
    VOLUME_ABOVE_AVG,
    VOLUME_BELOW_AVG,
    VOLUME_SPIKE,
    VOLUME_STRONG_SPIKE
)
from ..utils.formatters import format_volume, format_ratio


def render_volume_indicator(candles: List[Candle]) -> None:
    """
    Render volume analysis indicator.
    
    Args:
        candles: List of recent candles for volume analysis
    
    Displays:
        - Current volume value
        - 20-period moving average
        - Volume ratio (current / average)
        - Spike level indicator
        - Progress bar with color coding
    """
    try:
        if not candles or len(candles) < 20:
            st.info("⏳ Waiting for volume data (need at least 20 candles)...")
            return
        
        # Calculate volume analysis
        volume_analyzer = VolumeAnalyzer(ma_period=20)
        volume_analysis = volume_analyzer.analyze(candles)
        
        if not volume_analysis:
            st.warning("⚠️ Unable to calculate volume analysis")
            return
        
        current_volume = volume_analysis.current_volume
        average_volume = volume_analysis.average_volume
        ratio = volume_analysis.ratio
        spike_level = volume_analysis.spike_level
        
        # Determine spike level and color
        if ratio >= 2.5:
            spike_label = "🚨 STRONG SPIKE"
            spike_color = VOLUME_STRONG_SPIKE
            spike_emoji = "🚨"
        elif ratio >= 2.0:
            spike_label = "⚠️ SPIKE"
            spike_color = VOLUME_SPIKE
            spike_emoji = "⚠️"
        elif ratio >= 1.5:
            spike_label = "🟡 ELEVATED"
            spike_color = VOLUME_SPIKE
            spike_emoji = "🟡"
        else:
            spike_label = "🟢 NORMAL"
            spike_color = VOLUME_ABOVE_AVG if ratio >= 1.0 else VOLUME_BELOW_AVG
            spike_emoji = ""
        
        # Display title
        st.markdown("### Volume Analysis")
        
        # Display metrics
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(
                label="Current Volume",
                value=format_volume(current_volume)
            )
        
        with col2:
            st.metric(
                label="Average (MA20)",
                value=format_volume(average_volume)
            )
        
        # Display ratio and spike level
        ratio_html = f"""
        <div style="margin: 16px 0;">
            <div style="font-size: 16px; color: #757575; margin-bottom: 4px;">
                Volume Ratio
            </div>
            <div style="font-size: 28px; font-weight: 700; color: {spike_color};">
                {format_ratio(ratio)} {spike_emoji}
            </div>
            <div style="font-size: 18px; font-weight: 600; color: {spike_color}; margin-top: 4px;">
                {spike_label}
            </div>
        </div>
        """
        st.markdown(ratio_html, unsafe_allow_html=True)
        
        # Progress bar (normalize to 0-1, cap at 3x for display)
        progress_value = min(ratio / 3.0, 1.0)
        st.progress(progress_value)
        
        # Show alert for spikes
        if ratio >= 2.0:
            if ratio >= 2.5:
                st.error(f"🚨 Strong volume spike detected! ({format_ratio(ratio)})")
            else:
                st.warning(f"⚠️ Volume spike detected! ({format_ratio(ratio)})")
        
    except Exception as e:
        st.error(f"❌ Error loading volume indicator: {e}")


def render_volume_simple(candles: List[Candle]) -> None:
    """
    Render simple volume display (for compact spaces).
    
    Args:
        candles: List of recent candles for volume analysis
    """
    try:
        if not candles or len(candles) < 20:
            st.caption("⏳ Volume: Calculating...")
            return
        
        # Calculate volume analysis
        volume_analyzer = VolumeAnalyzer(ma_period=20)
        volume_analysis = volume_analyzer.analyze(candles)
        
        if not volume_analysis:
            st.caption("⚠️ Volume: N/A")
            return
        
        current_volume = volume_analysis.current_volume
        ratio = volume_analysis.ratio
        
        # Determine spike level
        if ratio >= 2.5:
            spike_label = "Strong Spike"
        elif ratio >= 2.0:
            spike_label = "Spike"
        elif ratio >= 1.5:
            spike_label = "Elevated"
        else:
            spike_label = "Normal"
        
        # Display as metric
        st.metric(
            label="Volume",
            value=format_volume(current_volume),
            delta=f"{format_ratio(ratio)} - {spike_label}"
        )
        
    except Exception as e:
        st.caption(f"❌ Volume error: {e}")


def render_volume_bar_chart(candles: List[Candle]) -> None:
    """
    Render volume as bar chart with color coding.
    
    Args:
        candles: List of recent candles for volume display
    """
    try:
        if not candles:
            st.info("⏳ No volume data available")
            return
        
        import plotly.graph_objects as go
        
        # Prepare data
        timestamps = [c.timestamp for c in candles]
        volumes = [c.volume for c in candles]
        
        # Calculate MA20 if enough data
        if len(candles) >= 20:
            volume_analyzer = VolumeAnalyzer(ma_period=20)
            volume_analysis = volume_analyzer.analyze(candles)
            avg_volume = volume_analysis.average_volume if volume_analysis else None
        else:
            avg_volume = None
        
        # Color bars based on price direction
        colors = []
        for i, candle in enumerate(candles):
            if candle.close > candle.open:
                colors.append(VOLUME_ABOVE_AVG)  # Green for up
            else:
                colors.append(VOLUME_BELOW_AVG)  # Red for down
        
        # Create bar chart
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=timestamps,
            y=volumes,
            marker_color=colors,
            name='Volume'
        ))
        
        # Add MA20 line if available
        if avg_volume:
            fig.add_hline(
                y=avg_volume,
                line_dash="dash",
                line_color="gray",
                annotation_text=f"MA20: {format_volume(avg_volume)}",
                annotation_position="right"
            )
        
        fig.update_layout(
            title="Volume",
            xaxis_title="Time",
            yaxis_title="Volume (BTC)",
            height=300,
            margin=dict(l=20, r=20, t=40, b=20),
            paper_bgcolor="white",
            plot_bgcolor="white",
            font={'color': "black"}
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"❌ Error rendering volume chart: {e}")
