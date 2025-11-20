"""
Data Formatting Utilities

Helper functions for formatting data for display in the dashboard.
"""

from datetime import datetime
from typing import Union


def format_price(price: float) -> str:
    """
    Format price with commas and 2 decimals.
    
    Args:
        price: Price value
    
    Returns:
        Formatted price string (e.g., "$91,558.84")
    
    Examples:
        >>> format_price(91558.84)
        '$91,558.84'
        >>> format_price(1234.5)
        '$1,234.50'
    """
    return f"${price:,.2f}"


def format_volume(volume: float) -> str:
    """
    Format volume with commas and 2 decimals.
    
    Args:
        volume: Volume value in BTC
    
    Returns:
        Formatted volume string (e.g., "25.50 BTC")
    
    Examples:
        >>> format_volume(25.5)
        '25.50 BTC'
        >>> format_volume(1234.567)
        '1,234.57 BTC'
    """
    return f"{volume:,.2f} BTC"


def format_percentage(value: float) -> str:
    """
    Format percentage with sign and 2 decimals.
    
    Args:
        value: Percentage value (e.g., 2.5 for 2.5%)
    
    Returns:
        Formatted percentage string (e.g., "+2.50%")
    
    Examples:
        >>> format_percentage(2.5)
        '+2.50%'
        >>> format_percentage(-1.3)
        '-1.30%'
    """
    return f"{value:+.2f}%"


def format_timestamp(dt: datetime) -> str:
    """
    Format datetime as HH:MM:SS.
    
    Args:
        dt: Datetime object
    
    Returns:
        Formatted time string (e.g., "18:00:15")
    
    Examples:
        >>> from datetime import datetime
        >>> dt = datetime(2025, 11, 18, 18, 0, 15)
        >>> format_timestamp(dt)
        '18:00:15'
    """
    return dt.strftime("%H:%M:%S")


def format_datetime(dt: datetime) -> str:
    """
    Format datetime as YYYY-MM-DD HH:MM:SS.
    
    Args:
        dt: Datetime object
    
    Returns:
        Formatted datetime string (e.g., "2025-11-18 18:00:15")
    
    Examples:
        >>> from datetime import datetime
        >>> dt = datetime(2025, 11, 18, 18, 0, 15)
        >>> format_datetime(dt)
        '2025-11-18 18:00:15'
    """
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def format_number(value: Union[int, float], decimals: int = 2) -> str:
    """
    Format number with commas and specified decimals.
    
    Args:
        value: Numeric value
        decimals: Number of decimal places (default: 2)
    
    Returns:
        Formatted number string
    
    Examples:
        >>> format_number(1234567.89)
        '1,234,567.89'
        >>> format_number(1234.5, decimals=0)
        '1,235'
    """
    return f"{value:,.{decimals}f}"


def format_latency(latency_ms: int) -> str:
    """
    Format latency in milliseconds.
    
    Args:
        latency_ms: Latency in milliseconds
    
    Returns:
        Formatted latency string (e.g., "430ms")
    
    Examples:
        >>> format_latency(430)
        '430ms'
        >>> format_latency(1500)
        '1,500ms'
    """
    return f"{latency_ms:,}ms"


def format_ratio(ratio: float, decimals: int = 1) -> str:
    """
    Format ratio with 'x' suffix.
    
    Args:
        ratio: Ratio value
        decimals: Number of decimal places (default: 1)
    
    Returns:
        Formatted ratio string (e.g., "1.7x")
    
    Examples:
        >>> format_ratio(1.7)
        '1.7x'
        >>> format_ratio(2.345, decimals=2)
        '2.35x'
    """
    return f"{ratio:.{decimals}f}x"
