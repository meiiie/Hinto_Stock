"""
Trading Signals Panel Component

Displays trading signals with confidence and reasons.
"""

import streamlit as st
from typing import Optional

from ....application.services.realtime_service import RealtimeService
from ....application.signals.signal_generator import TradingSignal
from ..config.theme_config import COLOR_BULLISH, COLOR_BEARISH, COLOR_NEUTRAL
from ..utils.formatters import format_price, format_timestamp, format_percentage


def render_signals_panel(service: RealtimeService) -> None:
    """
    Render trading signals panel.
    
    Args:
        service: RealtimeService instance
    
    Displays:
        - Signal type (BUY/SELL/NEUTRAL)
        - Confidence percentage and level
        - Price at signal generation
        - Timestamp
        - Contributing indicators (reasons)
    """
    try:
        # Get current signal
        signal = service.get_current_signals()
        
        if not signal:
            st.info("📊 No active trading signals")
            st.caption("Signals will appear when conditions are met")
            return
        
        # Check if signal is neutral
        if signal.signal_type.value == 'neutral':
            st.info("📊 No active trading signals")
            st.caption("Market conditions are neutral")
            return
        
        # Determine signal color and emoji
        if signal.signal_type.value == 'buy':
            signal_color = COLOR_BULLISH
            signal_emoji = "🟢"
            signal_label = "BUY SIGNAL"
            bg_color = "#E8F5E9"  # Light green
        else:  # sell
            signal_color = COLOR_BEARISH
            signal_emoji = "🔴"
            signal_label = "SELL SIGNAL"
            bg_color = "#FFEBEE"  # Light red
        
        # Display signal card
        st.markdown("### 🚨 Trading Signals")
        
        # Create colored card
        card_html = f"""
        <div style="
            background-color: {bg_color};
            border-left: 5px solid {signal_color};
            padding: 20px;
            border-radius: 8px;
            margin: 10px 0;
        ">
            <div style="font-size: 24px; font-weight: 700; color: {signal_color}; margin-bottom: 12px;">
                {signal_emoji} {signal_label}
            </div>
        </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)
        
        # Display confidence
        col1, col2 = st.columns(2)
        
        with col1:
            confidence_pct = signal.confidence * 100
            st.metric(
                label="Confidence",
                value=f"{confidence_pct:.0f}%"
            )
            
            # Confidence progress bar
            st.progress(signal.confidence)
        
        with col2:
            # Confidence level
            level = signal.confidence_level.value.upper()
            if level == "HIGH":
                level_color = COLOR_BULLISH
                level_emoji = "🔥"
            elif level == "MEDIUM":
                level_color = COLOR_NEUTRAL
                level_emoji = "⚡"
            else:
                level_color = "#757575"
                level_emoji = "💡"
            
            level_html = f"""
            <div style="margin-top: 8px;">
                <div style="font-size: 14px; color: #757575;">Level</div>
                <div style="font-size: 24px; font-weight: 700; color: {level_color};">
                    {level_emoji} {level}
                </div>
            </div>
            """
            st.markdown(level_html, unsafe_allow_html=True)
        
        # Display signal details
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(
                label="Current Price",
                value=format_price(signal.price)
            )
        
        with col2:
            timestamp_str = format_timestamp(signal.timestamp)
            st.metric(
                label="Time",
                value=timestamp_str
            )
        
        # Display Entry/TP/SL if available (Enhanced Signal)
        if signal.entry_price or signal.tp_levels or signal.stop_loss:
            st.markdown("---")
            st.markdown("### 📊 Trading Plan")
            
            # Entry Price
            if signal.entry_price:
                entry_col1, entry_col2 = st.columns([2, 1])
                with entry_col1:
                    st.metric(
                        label="📍 Entry Price",
                        value=format_price(signal.entry_price),
                        delta=format_percentage((signal.entry_price - signal.price) / signal.price)
                    )
                with entry_col2:
                    distance_pct = abs((signal.entry_price - signal.price) / signal.price * 100)
                    st.caption(f"Distance: {distance_pct:.2f}%")
            
            # Take Profit Levels
            if signal.tp_levels:
                st.markdown("**🎯 Take Profit Levels:**")
                
                tp_sizes = [0.6, 0.3, 0.1]  # 60%, 30%, 10%
                tp_labels = ['TP1', 'TP2', 'TP3']
                
                for i, (tp_key, tp_label) in enumerate(zip(['tp1', 'tp2', 'tp3'], tp_labels)):
                    if tp_key in signal.tp_levels:
                        tp_price = signal.tp_levels[tp_key]
                        tp_size = tp_sizes[i]
                        
                        # Calculate gain percentage
                        if signal.entry_price:
                            gain_pct = ((tp_price - signal.entry_price) / signal.entry_price) * 100
                        else:
                            gain_pct = ((tp_price - signal.price) / signal.price) * 100
                        
                        # Display TP level
                        tp_col1, tp_col2, tp_col3 = st.columns([2, 1, 1])
                        with tp_col1:
                            st.caption(f"**{tp_label}:** {format_price(tp_price)}")
                        with tp_col2:
                            st.caption(f"**{tp_size:.0%}** position")
                        with tp_col3:
                            gain_color = COLOR_BULLISH if gain_pct > 0 else COLOR_BEARISH
                            st.caption(f"<span style='color: {gain_color};'>**{gain_pct:+.2f}%**</span>", unsafe_allow_html=True)
            
            # Stop Loss
            if signal.stop_loss:
                st.markdown("**🛑 Stop Loss:**")
                
                sl_col1, sl_col2 = st.columns([2, 1])
                with sl_col1:
                    st.metric(
                        label="Stop Loss Price",
                        value=format_price(signal.stop_loss)
                    )
                with sl_col2:
                    # Calculate risk percentage
                    if signal.entry_price:
                        risk_pct = abs((signal.stop_loss - signal.entry_price) / signal.entry_price) * 100
                    else:
                        risk_pct = abs((signal.stop_loss - signal.price) / signal.price) * 100
                    
                    st.caption(f"<span style='color: {COLOR_BEARISH};'>**-{risk_pct:.2f}%** risk</span>", unsafe_allow_html=True)
            
            # Risk/Reward Ratio
            if signal.risk_reward_ratio:
                st.markdown("**📊 Risk/Reward Ratio:**")
                
                rr_ratio = signal.risk_reward_ratio
                rr_color = COLOR_BULLISH if rr_ratio >= 1.5 else COLOR_NEUTRAL
                
                rr_html = f"""
                <div style="
                    background-color: #F5F5F5;
                    padding: 12px;
                    border-radius: 6px;
                    text-align: center;
                    border-left: 4px solid {rr_color};
                ">
                    <div style="font-size: 24px; font-weight: 700; color: {rr_color};">
                        1:{rr_ratio:.2f}
                    </div>
                    <div style="font-size: 12px; color: #757575; margin-top: 4px;">
                        {'✅ Excellent' if rr_ratio >= 2.0 else '✓ Good' if rr_ratio >= 1.5 else '⚠️ Fair'}
                    </div>
                </div>
                """
                st.markdown(rr_html, unsafe_allow_html=True)
            
            # Position Size
            if signal.position_size:
                st.caption(f"💰 Suggested Position Size: **{signal.position_size:.4f} BTC** (1% max risk)")
        
        
        # Display reasons
        if signal.reasons:
            st.markdown("---")
            st.markdown("**Contributing Indicators:**")
            
            for reason in signal.reasons:
                st.markdown(f"✓ {reason}")
        
        # Display indicator values
        if signal.indicators:
            st.markdown("---")
            st.markdown("**Indicator Values:**")
            
            for key, value in signal.indicators.items():
                if isinstance(value, float):
                    st.caption(f"• {key}: {value:.2f}")
                else:
                    st.caption(f"• {key}: {value}")
        
    except Exception as e:
        st.error(f"❌ Error loading signals panel: {e}")


def render_signals_compact(service: RealtimeService) -> None:
    """
    Render compact signals display (for sidebar or small spaces).
    
    Args:
        service: RealtimeService instance
    """
    try:
        signal = service.get_current_signals()
        
        if not signal or signal.signal_type.value == 'neutral':
            st.caption("📊 No active signals")
            return
        
        # Determine signal info
        if signal.signal_type.value == 'buy':
            signal_emoji = "🟢"
            signal_label = "BUY"
            signal_color = COLOR_BULLISH
        else:
            signal_emoji = "🔴"
            signal_label = "SELL"
            signal_color = COLOR_BEARISH
        
        confidence_pct = signal.confidence * 100
        
        # Compact display
        signal_html = f"""
        <div style="
            background-color: #F5F5F5;
            padding: 12px;
            border-radius: 6px;
            border-left: 4px solid {signal_color};
        ">
            <div style="font-size: 18px; font-weight: 700; color: {signal_color};">
                {signal_emoji} {signal_label}
            </div>
            <div style="font-size: 14px; color: #757575; margin-top: 4px;">
                Confidence: {confidence_pct:.0f}%
            </div>
        </div>
        """
        st.markdown(signal_html, unsafe_allow_html=True)
        
    except Exception as e:
        st.caption(f"❌ Signal error: {e}")


def render_signals_list(service: RealtimeService, limit: int = 5) -> None:
    """
    Render list of recent signals (if service tracks history).
    
    Args:
        service: RealtimeService instance
        limit: Maximum number of signals to display
    
    Note:
        Currently only shows the latest signal. 
        Future enhancement: track signal history.
    """
    try:
        st.markdown("### Recent Signals")
        
        signal = service.get_current_signals()
        
        if not signal or signal.signal_type.value == 'neutral':
            st.info("No recent signals")
            return
        
        # Display latest signal in list format
        signal_type = signal.signal_type.value.upper()
        confidence_pct = signal.confidence * 100
        timestamp_str = format_timestamp(signal.timestamp)
        
        if signal.signal_type.value == 'buy':
            signal_color = COLOR_BULLISH
            signal_emoji = "🟢"
        else:
            signal_color = COLOR_BEARISH
            signal_emoji = "🔴"
        
        signal_html = f"""
        <div style="
            background-color: #FAFAFA;
            padding: 16px;
            border-radius: 6px;
            margin: 8px 0;
            border-left: 4px solid {signal_color};
        ">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <span style="font-size: 20px; font-weight: 700; color: {signal_color};">
                        {signal_emoji} {signal_type}
                    </span>
                    <span style="font-size: 14px; color: #757575; margin-left: 12px;">
                        {timestamp_str}
                    </span>
                </div>
                <div style="font-size: 16px; font-weight: 600; color: {signal_color};">
                    {confidence_pct:.0f}%
                </div>
            </div>
            <div style="font-size: 14px; color: #757575; margin-top: 8px;">
                Price: {format_price(signal.price)}
            </div>
        </div>
        """
        st.markdown(signal_html, unsafe_allow_html=True)
        
        st.caption("💡 Tip: Signal history tracking coming soon!")
        
    except Exception as e:
        st.error(f"❌ Error loading signals list: {e}")
