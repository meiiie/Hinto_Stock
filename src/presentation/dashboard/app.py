"""
Streamlit Dashboard - Main Application

Main entry point for the Crypto Data Dashboard.
Provides navigation and page routing.
"""

import streamlit as st
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from src.infrastructure.di_container import DIContainer
from src.utils.logging_config import configure_logging
from src.presentation.dashboard.utils import initialize_session_state
from src.infrastructure.persistence.sqlite_order_repository import SQLiteOrderRepository
from src.application.services.paper_trading_service import PaperTradingService


# Page configuration
st.set_page_config(
    page_title="Real-time Trading Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "Real-time cryptocurrency trading dashboard with technical analysis"
    }
)


# @st.cache_resource
def get_di_container():
    """
    Initialize and cache DI Container.
    
    This ensures we only create one instance of the container
    and reuse it across the entire app session.
    """
    # Setup logging
    configure_logging(level=20)  # INFO level
    
    config = {
        'DATABASE_PATH': 'crypto_data.db',
        'BINANCE_API_KEY': None,
        'BINANCE_API_SECRET': None
    }
    
    return DIContainer(config)


# @st.cache_resource
def get_dashboard_service():
    """Get DashboardService from DI Container"""
    container = get_di_container()
    return container.get_dashboard_service()


def main():
    """Main application entry point"""
    
    # Initialize session state
    initialize_session_state()
    
    # Initialize Real-time Service if not exists
    if st.session_state.service is None:
        try:
            # Initialize Paper Trading dependencies
            order_repo = SQLiteOrderRepository()
            paper_service = PaperTradingService(order_repo)
            
            from src.application.services.realtime_service_threaded import ThreadedRealtimeService
            st.session_state.service = ThreadedRealtimeService(paper_service=paper_service)
            st.sidebar.success("✅ Service initialized")
        except Exception as e:
            st.sidebar.error(f"❌ Service initialization failed: {e}")
            st.session_state.service = None
    
    # Sidebar navigation
    st.sidebar.title("📈 Real-time Trading Dashboard")
    st.sidebar.markdown("---")
    
    # Page selection
    page = st.sidebar.radio(
        "Navigation",
        ["🏠 Home", "📊 Charts", "🔍 Monitoring", "📝 Paper Trading", "⚙️ Settings"],
        label_visibility="collapsed"
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### About")
    st.sidebar.info(
        "Real-time cryptocurrency data dashboard "
        "with technical indicators and monitoring."
    )
    
    # Route to selected page
    if page == "🏠 Home":
        from src.presentation.dashboard.pages import home
        home.render()
    elif page == "📊 Charts":
        from src.presentation.dashboard.pages import charts
        charts.render()
    elif page == "🔍 Monitoring":
        from src.presentation.dashboard.pages import monitoring
        monitoring.render()
    elif page == "📝 Paper Trading":
        from src.presentation.dashboard.pages import paper_trading
        paper_trading.render()
    elif page == "⚙️ Settings":
        from src.presentation.dashboard.pages import settings
        settings.render()


if __name__ == "__main__":
    main()
