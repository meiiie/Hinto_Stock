"""
State Management Utilities

Helper functions for managing Streamlit session state.
"""

import streamlit as st
from typing import Any, Optional
from datetime import datetime

from ....application.services.realtime_service import RealtimeService


def initialize_session_state() -> None:
    """
    Initialize all session state variables with default values.
    
    This should be called once at the start of the app.
    """
    # Service instance
    if 'service' not in st.session_state:
        st.session_state.service = None
    
    # Auto-refresh settings
    if 'auto_refresh' not in st.session_state:
        st.session_state.auto_refresh = True
    
    if 'refresh_interval' not in st.session_state:
        st.session_state.refresh_interval = 1  # seconds
    
    # Cache timestamps
    if 'last_refresh' not in st.session_state:
        st.session_state.last_refresh = datetime.now()
    
    if 'cache_ttl' not in st.session_state:
        st.session_state.cache_ttl = 1  # seconds
    
    # User preferences
    if 'show_signals' not in st.session_state:
        st.session_state.show_signals = True
    
    if 'chart_limit' not in st.session_state:
        st.session_state.chart_limit = 100
    
    if 'selected_timeframe' not in st.session_state:
        st.session_state.selected_timeframe = '15m'


def get_service() -> Optional[RealtimeService]:
    """
    Get the RealtimeService instance from session state.
    
    Returns:
        RealtimeService instance or None if not initialized
    """
    return st.session_state.get('service', None)


def set_service(service: RealtimeService) -> None:
    """
    Set the RealtimeService instance in session state.
    
    Args:
        service: RealtimeService instance
    """
    st.session_state.service = service


def is_auto_refresh_enabled() -> bool:
    """
    Check if auto-refresh is enabled.
    
    Returns:
        True if auto-refresh is enabled, False otherwise
    """
    return st.session_state.get('auto_refresh', True)


def set_auto_refresh(enabled: bool) -> None:
    """
    Enable or disable auto-refresh.
    
    Args:
        enabled: True to enable, False to disable
    """
    st.session_state.auto_refresh = enabled


def get_refresh_interval() -> int:
    """
    Get the auto-refresh interval in seconds.
    
    Returns:
        Refresh interval in seconds
    """
    return st.session_state.get('refresh_interval', 1)


def set_refresh_interval(interval: int) -> None:
    """
    Set the auto-refresh interval.
    
    Args:
        interval: Refresh interval in seconds (minimum 1)
    """
    if interval < 1:
        interval = 1
    st.session_state.refresh_interval = interval


def update_last_refresh() -> None:
    """
    Update the last refresh timestamp to current time.
    """
    st.session_state.last_refresh = datetime.now()


def get_last_refresh() -> datetime:
    """
    Get the last refresh timestamp.
    
    Returns:
        Last refresh datetime
    """
    return st.session_state.get('last_refresh', datetime.now())


def should_refresh() -> bool:
    """
    Check if enough time has passed since last refresh.
    
    Returns:
        True if should refresh, False otherwise
    """
    if not is_auto_refresh_enabled():
        return False
    
    last_refresh = get_last_refresh()
    interval = get_refresh_interval()
    elapsed = (datetime.now() - last_refresh).total_seconds()
    
    return elapsed >= interval


def get_state_value(key: str, default: Any = None) -> Any:
    """
    Get a value from session state with a default.
    
    Args:
        key: State key
        default: Default value if key doesn't exist
    
    Returns:
        State value or default
    """
    return st.session_state.get(key, default)


def set_state_value(key: str, value: Any) -> None:
    """
    Set a value in session state.
    
    Args:
        key: State key
        value: Value to set
    """
    st.session_state[key] = value


def clear_state() -> None:
    """
    Clear all session state.
    
    Warning: This will reset the entire application state.
    """
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    
    # Reinitialize with defaults
    initialize_session_state()


def get_user_preferences() -> dict:
    """
    Get all user preferences as a dictionary.
    
    Returns:
        Dictionary of user preferences
    """
    return {
        'auto_refresh': is_auto_refresh_enabled(),
        'refresh_interval': get_refresh_interval(),
        'show_signals': st.session_state.get('show_signals', True),
        'chart_limit': st.session_state.get('chart_limit', 100),
        'selected_timeframe': st.session_state.get('selected_timeframe', '15m')
    }


def set_user_preferences(preferences: dict) -> None:
    """
    Set user preferences from a dictionary.
    
    Args:
        preferences: Dictionary of preferences to set
    """
    if 'auto_refresh' in preferences:
        set_auto_refresh(preferences['auto_refresh'])
    
    if 'refresh_interval' in preferences:
        set_refresh_interval(preferences['refresh_interval'])
    
    if 'show_signals' in preferences:
        st.session_state.show_signals = preferences['show_signals']
    
    if 'chart_limit' in preferences:
        st.session_state.chart_limit = preferences['chart_limit']
    
    if 'selected_timeframe' in preferences:
        st.session_state.selected_timeframe = preferences['selected_timeframe']
