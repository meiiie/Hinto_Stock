"""
Cache Management Utilities

Helper functions for managing Streamlit caching.
"""

import streamlit as st
from typing import List, Optional
from datetime import datetime

from ....domain.entities.candle import Candle
from ....application.services.realtime_service import RealtimeService


@st.cache_data(ttl=1)
def get_cached_candles(
    service_id: int,
    timeframe: str,
    limit: int = 100
) -> List[Candle]:
    """
    Get candles with 1-second cache.
    
    Args:
        service_id: Service instance ID (for cache key)
        timeframe: Timeframe ('1m', '15m', '1h')
        limit: Maximum number of candles
    
    Returns:
        List of Candle objects
    
    Note:
        Uses service_id instead of service object to make it hashable for caching.
        The actual service instance should be retrieved from session state.
    """
    if 'service' not in st.session_state:
        return []
    
    service: RealtimeService = st.session_state.service
    return service.get_candles(timeframe, limit)


@st.cache_data(ttl=1)
def get_cached_latest_data(
    service_id: int,
    timeframe: str
) -> Optional[Candle]:
    """
    Get latest candle with 1-second cache.
    
    Args:
        service_id: Service instance ID (for cache key)
        timeframe: Timeframe ('1m', '15m', '1h')
    
    Returns:
        Latest Candle or None
    """
    if 'service' not in st.session_state:
        return None
    
    service: RealtimeService = st.session_state.service
    return service.get_latest_data(timeframe)


@st.cache_data(ttl=1)
def get_cached_status(service_id: int) -> dict:
    """
    Get service status with 1-second cache.
    
    Args:
        service_id: Service instance ID (for cache key)
    
    Returns:
        Status dictionary
    """
    if 'service' not in st.session_state:
        return {
            'is_running': False,
            'connection': {
                'is_connected': False,
                'state': 'disconnected',
                'latency_ms': 0,
                'reconnect_count': 0
            },
            'data': {
                '1m_candles': 0,
                '15m_candles': 0,
                '1h_candles': 0,
                'latest_1m': None,
                'latest_15m': None,
                'latest_1h': None
            },
            'signals': {
                'latest': None
            }
        }
    
    service: RealtimeService = st.session_state.service
    return service.get_status()


@st.cache_resource
def get_service_instance() -> RealtimeService:
    """
    Get singleton RealtimeService instance.
    
    Returns:
        RealtimeService instance
    
    Note:
        This creates a singleton instance that persists across reruns.
        Use with caution as it maintains state.
    """
    return RealtimeService()


def clear_all_caches() -> None:
    """
    Clear all Streamlit caches.
    
    This is useful when you want to force a refresh of all cached data.
    """
    st.cache_data.clear()
    st.cache_resource.clear()


def get_cache_key() -> int:
    """
    Get a cache key based on current timestamp.
    
    Returns:
        Integer cache key (seconds since epoch)
    
    Note:
        This can be used to force cache invalidation by changing the key.
    """
    return int(datetime.now().timestamp())
