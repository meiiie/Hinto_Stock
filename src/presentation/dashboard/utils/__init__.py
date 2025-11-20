"""
Dashboard Utilities

Helper utilities for the trading dashboard.
"""

from .formatters import (
    format_price,
    format_volume,
    format_percentage,
    format_timestamp,
    format_datetime,
    format_number,
    format_latency,
    format_ratio
)

from .cache_manager import (
    get_cached_candles,
    get_cached_latest_data,
    get_cached_status,
    get_service_instance,
    clear_all_caches,
    get_cache_key
)

from .state_manager import (
    initialize_session_state,
    get_service,
    set_service,
    is_auto_refresh_enabled,
    set_auto_refresh,
    get_refresh_interval,
    set_refresh_interval,
    update_last_refresh,
    get_last_refresh,
    should_refresh,
    get_state_value,
    set_state_value,
    clear_state,
    get_user_preferences,
    set_user_preferences
)

__all__ = [
    # Formatters
    'format_price',
    'format_volume',
    'format_percentage',
    'format_timestamp',
    'format_datetime',
    'format_number',
    'format_latency',
    'format_ratio',
    # Cache Manager
    'get_cached_candles',
    'get_cached_latest_data',
    'get_cached_status',
    'get_service_instance',
    'clear_all_caches',
    'get_cache_key',
    # State Manager
    'initialize_session_state',
    'get_service',
    'set_service',
    'is_auto_refresh_enabled',
    'set_auto_refresh',
    'get_refresh_interval',
    'set_refresh_interval',
    'update_last_refresh',
    'get_last_refresh',
    'should_refresh',
    'get_state_value',
    'set_state_value',
    'clear_state',
    'get_user_preferences',
    'set_user_preferences'
]
