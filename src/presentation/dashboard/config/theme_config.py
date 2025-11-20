"""
Theme Configuration

Dark theme color palette and styling constants for the trading dashboard.
"""

# Background Colors
BACKGROUND_PRIMARY = "#0E1117"      # Dark background
BACKGROUND_SECONDARY = "#1A1D24"    # Slightly lighter dark
BACKGROUND_CARD = "#262730"         # Card background
BORDER_COLOR = "#3A3D47"            # Border gray

# Text Colors
TEXT_PRIMARY = "#FAFAFA"            # Light text
TEXT_SECONDARY = "#B0B3BA"          # Medium gray text
TEXT_DISABLED = "#6B6E76"           # Disabled text

# Indicator Colors
COLOR_BULLISH = "#26A69A"           # Green (price up)
COLOR_BEARISH = "#EF5350"           # Red (price down)
COLOR_NEUTRAL = "#FFA726"           # Orange
COLOR_WARNING = "#FFEB3B"           # Yellow
COLOR_INFO = "#42A5F5"              # Blue

# RSI Zone Colors
RSI_STRONG_OVERBOUGHT = "#EF5350"   # Red (80-100)
RSI_OVERBOUGHT = "#FF9800"          # Orange (70-80)
RSI_NEUTRAL = "#FFC107"             # Yellow (30-70)
RSI_OVERSOLD = "#66BB6A"            # Green (20-30)
RSI_STRONG_OVERSOLD = "#26C6DA"     # Cyan (0-20)

# Volume Colors
VOLUME_ABOVE_AVG = "#26A69A"        # Green
VOLUME_BELOW_AVG = "#EF5350"        # Red
VOLUME_SPIKE = "#FF9800"            # Orange (2x highlight)
VOLUME_STRONG_SPIKE = "#F44336"     # Red (2.5x highlight)

# Connection Status Colors
STATUS_CONNECTED = "#4CAF50"        # Green
STATUS_DISCONNECTED = "#F44336"     # Red
STATUS_RECONNECTING = "#FF9800"     # Orange

# Chart Colors (Plotly compatible)
CHART_BACKGROUND = "#0E1117"
CHART_GRID = "#3A3D47"
CHART_TEXT = "#FAFAFA"
CHART_CANDLESTICK_UP = "#26A69A"
CHART_CANDLESTICK_DOWN = "#EF5350"

# Streamlit Custom CSS for Dark Theme
CUSTOM_CSS = """
<style>
    /* Main background */
    .stApp {
        background-color: #0E1117;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #1A1D24;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        color: #FAFAFA;
        font-size: 28px;
        font-weight: 600;
    }
    
    [data-testid="stMetricLabel"] {
        color: #B0B3BA;
        font-size: 14px;
    }
    
    /* Cards */
    .element-container {
        background-color: #262730;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #FAFAFA;
    }
    
    /* Buttons */
    .stButton > button {
        background-color: #42A5F5;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 0.5rem 1rem;
    }
    
    .stButton > button:hover {
        background-color: #1E88E5;
    }
    
    /* Tables */
    .dataframe {
        background-color: #262730;
        color: #FAFAFA;
    }
    
    /* Success/Error messages */
    .stSuccess {
        background-color: #1B5E20;
        color: #A5D6A7;
    }
    
    .stError {
        background-color: #B71C1C;
        color: #EF9A9A;
    }
    
    .stWarning {
        background-color: #E65100;
        color: #FFCC80;
    }
    
    .stInfo {
        background-color: #0D47A1;
        color: #90CAF9;
    }
</style>
"""


def get_price_color(current: float, previous: float) -> str:
    """
    Get color for price based on direction.
    
    Args:
        current: Current price
        previous: Previous price
    
    Returns:
        Color hex code
    """
    if current > previous:
        return COLOR_BULLISH
    elif current < previous:
        return COLOR_BEARISH
    else:
        return COLOR_NEUTRAL


def get_rsi_color(rsi_value: float) -> str:
    """
    Get color for RSI value based on zone.
    
    Args:
        rsi_value: RSI value (0-100)
    
    Returns:
        Color hex code
    """
    if rsi_value >= 80:
        return RSI_STRONG_OVERBOUGHT
    elif rsi_value >= 70:
        return RSI_OVERBOUGHT
    elif rsi_value >= 30:
        return RSI_NEUTRAL
    elif rsi_value >= 20:
        return RSI_OVERSOLD
    else:
        return RSI_STRONG_OVERSOLD


def get_volume_color(ratio: float) -> str:
    """
    Get color for volume based on ratio to average.
    
    Args:
        ratio: Volume / Average volume
    
    Returns:
        Color hex code
    """
    if ratio >= 2.5:
        return VOLUME_STRONG_SPIKE
    elif ratio >= 2.0:
        return VOLUME_SPIKE
    elif ratio >= 1.0:
        return VOLUME_ABOVE_AVG
    else:
        return VOLUME_BELOW_AVG


def format_price(price: float) -> str:
    """Format price with commas and 2 decimals."""
    return f"${price:,.2f}"


def format_volume(volume: float) -> str:
    """Format volume with commas and 2 decimals."""
    return f"{volume:,.2f} BTC"


def format_percentage(value: float) -> str:
    """Format percentage with sign and 2 decimals."""
    return f"{value:+.2f}%"
