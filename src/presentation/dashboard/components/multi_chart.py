"""
Multi-timeframe Chart Component

Displays side-by-side charts for 15m and 1h timeframes.
"""

import streamlit as st
from typing import List
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from ....domain.entities.candle import Candle
from ....application.services.realtime_service import RealtimeService
from ..config.theme_config import (
    CHART_CANDLESTICK_UP,
    CHART_CANDLESTICK_DOWN,
    CHART_BACKGROUND,
    CHART_GRID,
    CHART_TEXT,
    VOLUME_ABOVE_AVG,
    VOLUME_BELOW_AVG
)


def create_candlestick_chart(
    candles: List[Candle],
    title: str = "Price Chart"
) -> go.Figure:
    """
    Create a candlestick chart with EMA, RSI, and Volume subplots.
    
    Args:
        candles: List of Candle objects
        title: Chart title
    
    Returns:
        Plotly Figure object
    """
    if not candles:
        # Return empty figure
        fig = go.Figure()
        fig.add_annotation(
            text="No data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=20, color="gray")
        )
        return fig
    
    # Prepare data
    timestamps = [c.timestamp for c in candles]
    opens = [c.open for c in candles]
    highs = [c.high for c in candles]
    lows = [c.low for c in candles]
    closes = [c.close for c in candles]
    volumes = [c.volume for c in candles]
    
    # EMA and RSI data - use getattr to safely access attributes
    ema7_values = [getattr(c, 'ema_7', None) for c in candles]
    ema25_values = [getattr(c, 'ema_25', None) for c in candles]
    rsi_values = [getattr(c, 'rsi_6', None) for c in candles]
    
    # Create subplots: Price, RSI, Volume
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.6, 0.2, 0.2],
        subplot_titles=(title, "RSI(6)", "Volume")
    )
    
    # 1. Candlestick chart
    fig.add_trace(
        go.Candlestick(
            x=timestamps,
            open=opens,
            high=highs,
            low=lows,
            close=closes,
            name="Price",
            increasing_line_color=CHART_CANDLESTICK_UP,
            decreasing_line_color=CHART_CANDLESTICK_DOWN
        ),
        row=1, col=1
    )
    
    # 2. EMA(7) overlay
    if any(ema7_values):
        fig.add_trace(
            go.Scatter(
                x=timestamps,
                y=ema7_values,
                name="EMA(7)",
                line=dict(color="#1f77b4", width=2),  # Blue
                mode='lines'
            ),
            row=1, col=1
        )
    
    # 3. EMA(25) overlay
    if any(ema25_values):
        fig.add_trace(
            go.Scatter(
                x=timestamps,
                y=ema25_values,
                name="EMA(25)",
                line=dict(color="#ff7f0e", width=2),  # Orange
                mode='lines'
            ),
            row=1, col=1
        )
    
    # 4. RSI subplot
    if any(rsi_values):
        fig.add_trace(
            go.Scatter(
                x=timestamps,
                y=rsi_values,
                name="RSI",
                line=dict(color="purple", width=2),
                fill='tozeroy',
                fillcolor='rgba(128, 0, 128, 0.1)'
            ),
            row=2, col=1
        )
        
        # Add RSI levels (30 and 70)
        fig.add_hline(
            y=70, line_dash="dash", line_color="red",
            annotation_text="Overbought (70)",
            annotation_position="right",
            row=2, col=1
        )
        fig.add_hline(
            y=30, line_dash="dash", line_color="green",
            annotation_text="Oversold (30)",
            annotation_position="right",
            row=2, col=1
        )
    
    # 5. Volume bars with spike detection
    # Calculate volume MA(20) for spike detection
    volume_ma = []
    for i in range(len(volumes)):
        if i < 20:
            volume_ma.append(None)
        else:
            ma = sum(volumes[i-20:i]) / 20
            volume_ma.append(ma)
    
    # Detect spikes and color accordingly
    colors = []
    for i, (vol, c, o) in enumerate(zip(volumes, closes, opens)):
        ma = volume_ma[i]
        if ma and vol >= ma * 2.0:  # Spike threshold: 2x average
            # Volume spike - use bright yellow/orange
            colors.append('#FFA726')  # Bright orange for spikes
        elif c > o:
            colors.append(VOLUME_ABOVE_AVG)  # Green for up
        else:
            colors.append(VOLUME_BELOW_AVG)  # Red for down
    
    fig.add_trace(
        go.Bar(
            x=timestamps,
            y=volumes,
            name="Volume",
            marker_color=colors,
            showlegend=False,
            hovertemplate='Volume: %{y:.2f} BTC<extra></extra>'
        ),
        row=3, col=1
    )
    
    # Add Volume MA(20) line
    if any(v is not None for v in volume_ma):
        fig.add_trace(
            go.Scatter(
                x=timestamps,
                y=volume_ma,
                name="Vol MA(20)",
                line=dict(color="#2196F3", width=1, dash='dot'),
                mode='lines',
                hovertemplate='MA(20): %{y:.2f} BTC<extra></extra>'
            ),
            row=3, col=1
        )
        
        # Add spike threshold line (2x MA)
        spike_threshold = [ma * 2.0 if ma else None for ma in volume_ma]
        if any(v is not None for v in spike_threshold):
            fig.add_trace(
                go.Scatter(
                    x=timestamps,
                    y=spike_threshold,
                    name="Spike Threshold (2x)",
                    line=dict(color="#FF5722", width=1, dash='dash'),
                    mode='lines',
                    hovertemplate='Spike Threshold: %{y:.2f} BTC<extra></extra>'
                ),
                row=3, col=1
            )
    
    # Update layout
    fig.update_layout(
        height=800,
        paper_bgcolor=CHART_BACKGROUND,
        plot_bgcolor=CHART_BACKGROUND,
        font=dict(color=CHART_TEXT),
        xaxis_rangeslider_visible=False,
        hovermode='x unified',
        margin=dict(l=50, r=50, t=50, b=50)
    )
    
    # Update axes
    fig.update_xaxes(
        gridcolor=CHART_GRID,
        showgrid=True,
        title_text="Time",
        row=3, col=1
    )
    
    fig.update_yaxes(
        gridcolor=CHART_GRID,
        showgrid=True,
        title_text="Price (USD)",
        row=1, col=1
    )
    
    fig.update_yaxes(
        gridcolor=CHART_GRID,
        showgrid=True,
        title_text="RSI",
        range=[0, 100],
        row=2, col=1
    )
    
    fig.update_yaxes(
        gridcolor=CHART_GRID,
        showgrid=True,
        title_text="Volume (BTC)",
        row=3, col=1
    )
    
    return fig


def render_multi_chart(service: RealtimeService, limit: int = 100) -> None:
    """
    Render dual timeframe charts (15m and 1h side-by-side).
    
    Args:
        service: RealtimeService instance
        limit: Maximum number of candles to display
    
    Displays:
        - Two columns (15m and 1h)
        - Candlestick chart with EMA(7) overlay
        - RSI subplot
        - Volume subplot
        - Synchronized time axis
    """
    try:
        st.markdown("### 📊 Multi-timeframe Analysis")
        
        # Get candles for both timeframes
        candles_15m = service.get_candles('15m', limit)
        candles_1h = service.get_candles('1h', limit)
        
        # Check if we have data
        if not candles_15m and not candles_1h:
            st.info("⏳ Waiting for chart data...")
            st.caption("Charts will appear once aggregated candles are available")
            return
        
        # Create two columns
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 15-Minute Chart")
            if candles_15m:
                fig_15m = create_candlestick_chart(candles_15m, "15m Timeframe")
                st.plotly_chart(fig_15m, use_container_width=True)
                st.caption(f"Showing {len(candles_15m)} candles")
            else:
                st.info("⏳ Waiting for 15m candles...")
                st.caption("Need at least 15 minutes of data")
        
        with col2:
            st.markdown("#### 1-Hour Chart")
            if candles_1h:
                fig_1h = create_candlestick_chart(candles_1h, "1h Timeframe")
                st.plotly_chart(fig_1h, use_container_width=True)
                st.caption(f"Showing {len(candles_1h)} candles")
            else:
                st.info("⏳ Waiting for 1h candles...")
                st.caption("Need at least 1 hour of data")
        
    except Exception as e:
        st.error(f"❌ Error loading charts: {e}")


def render_single_chart(
    candles: List[Candle],
    timeframe: str = "15m",
    height: int = 600
) -> None:
    """
    Render a single timeframe chart.
    
    Args:
        candles: List of Candle objects
        timeframe: Timeframe label (e.g., "15m", "1h")
        height: Chart height in pixels
    """
    try:
        if not candles:
            st.info(f"⏳ No {timeframe} data available")
            return
        
        st.markdown(f"### {timeframe.upper()} Chart")
        
        fig = create_candlestick_chart(candles, f"{timeframe} Timeframe")
        fig.update_layout(height=height)
        
        st.plotly_chart(fig, use_container_width=True)
        st.caption(f"Showing {len(candles)} candles")
        
    except Exception as e:
        st.error(f"❌ Error rendering chart: {e}")


def render_chart_controls() -> dict:
    """
    Render chart control widgets.
    
    Returns:
        Dictionary with user selections
    """
    col1, col2, col3 = st.columns(3)
    
    with col1:
        timeframe = st.selectbox(
            "Timeframe",
            options=["1m", "15m", "1h"],
            index=1,
            key="chart_timeframe"
        )
    
    with col2:
        limit = st.slider(
            "Candles",
            min_value=20,
            max_value=200,
            value=100,
            step=20,
            key="chart_limit"
        )
    
    with col3:
        chart_type = st.selectbox(
            "Chart Type",
            options=["Candlestick", "Line"],
            index=0,
            key="chart_type"
        )
    
    return {
        'timeframe': timeframe,
        'limit': limit,
        'chart_type': chart_type
    }
