import streamlit as st
from src.presentation.dashboard.components.paper_portfolio import PaperPortfolioComponent

def render():
    st.title("Paper Trading Engine")
    
    # Initialize component
    portfolio = PaperPortfolioComponent()
    
    # Get current price from service
    current_price = 0.0
    if 'service' in st.session_state and st.session_state.service:
        service = st.session_state.service
        if service.is_running():
            latest_candle = service.get_latest_data('1m')
            if latest_candle:
                current_price = latest_candle.close
    
    # Render with real-time price
    # (Reset Button moved to bottom)

    portfolio.render(current_price=current_price)
    
    # Auto-refresh controls
    col1, col2 = st.columns([3, 1])
    with col2:
        auto_refresh = st.checkbox("🔄 Auto-refresh (2s)", value=True)
    
    if auto_refresh:
        import time
        time.sleep(2)
        st.rerun()
    
    # Add manual refresh button (only if auto-refresh is off)
    if not auto_refresh:
        if st.button("🔄 Refresh Data"):
            st.rerun()

    st.markdown("---")
    with st.expander("⚠️ Danger Zone"):
        st.warning("This action will delete all trade history and reset your balance to $10,000.")
        if st.button("🗑️ Reset Paper Trading Data", type="primary"):
            if 'service' in st.session_state and st.session_state.service:
                service = st.session_state.service
                if hasattr(service, 'paper_service'):
                    service.paper_service.reset_account()
                    st.toast("✅ Paper Trading Data Reset!", icon="🗑️")
                    st.rerun()
