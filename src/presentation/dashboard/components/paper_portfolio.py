import streamlit as st
import pandas as pd
from src.infrastructure.persistence.sqlite_order_repository import SQLiteOrderRepository

class PaperPortfolioComponent:
    """
    UI Component to display Paper Trading Portfolio (Futures Model).
    """
    def __init__(self):
        self.repo = SQLiteOrderRepository()

    def render(self, current_price: float = 0.0):
        st.subheader("📝 Futures Portfolio (USDT-M)")
        
        # 1. Account Summary
        wallet_balance = self.repo.get_account_balance()
        active_positions = self.repo.get_active_orders()
        closed_positions = self.repo.get_closed_orders(limit=100)
        
        # Calculate Metrics
        unrealized_pnl = 0.0
        used_margin = 0.0
        
        if current_price > 0:
            for pos in active_positions:
                pnl = pos.calculate_unrealized_pnl(current_price)
                unrealized_pnl += pnl
                used_margin += pos.margin
        
        margin_balance = wallet_balance + unrealized_pnl
        available_balance = max(0.0, margin_balance - used_margin)
        
        # Win Rate Calculation
        win_count = sum(1 for o in closed_positions if o.realized_pnl > 0)
        loss_count = sum(1 for o in closed_positions if o.realized_pnl < 0)
        total_trades = win_count + loss_count
        win_rate = (win_count / total_trades * 100) if total_trades > 0 else 0.0
        
        # Display Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        col1.metric(
            "Margin Balance", 
            f"${margin_balance:,.2f}",
            f"{unrealized_pnl:+.2f} (Unrealized)",
            delta_color="normal" if unrealized_pnl == 0 else "off"
        )
        
        col2.metric("Wallet Balance", f"${wallet_balance:,.2f}")
        col3.metric("Available", f"${available_balance:,.2f}")
        col4.metric("Win Rate", f"{win_rate:.1f}%", f"{win_count}W / {loss_count}L")
        
        st.markdown("---")
        
        # 2. Open Positions (Binance Style)
        st.write("### Open Positions")
        if active_positions:
            data = []
            for pos in active_positions:
                # Calculate PnL
                pnl = 0.0
                roe_pct = 0.0
                
                if current_price > 0:
                    pnl = pos.calculate_unrealized_pnl(current_price)
                    if pos.margin > 0:
                        roe_pct = (pnl / pos.margin) * 100
                
                # Visual Side (Green/Red Bar)
                side_emoji = "🟢" if pos.side == 'LONG' else "🔴"
                symbol_display = f"{side_emoji} {pos.symbol} (1x Isolated)"
                
                # Dual Size Display
                size_usdt = pos.quantity * (current_price if current_price > 0 else pos.entry_price)
                size_display = f"{pos.quantity:.4f} BTC\n(${size_usdt:,.0f})"

                data.append({
                    "id": pos.id, # Hidden ID for actions
                    "Symbol": symbol_display,
                    "Size": size_display,
                    "Entry Price": pos.entry_price,
                    "Break Even": pos.entry_price, # Initially same as Entry
                    "Mark Price": current_price if current_price > 0 else pos.entry_price,
                    "Liq. Price": pos.liquidation_price,
                    "Margin": pos.margin,
                    "PnL (ROE%)": pnl, # Raw value for column_config
                    "TP/SL": f"{pos.take_profit:,.2f} / {pos.stop_loss:,.2f}",
                    "Close": False # Checkbox for action
                })
            
            df_active = pd.DataFrame(data)
            
            # Configure Columns
            edited_df = st.data_editor(
                df_active,
                column_config={
                    "id": None, # Hide ID
                    "Symbol": st.column_config.TextColumn("Symbol", help="Trading Pair & Mode"),
                    "Size": st.column_config.TextColumn("Size", help="Amount (Coin) & Value (USDT)"),
                    "Entry Price": st.column_config.NumberColumn("Entry Price", format="$%.2f"),
                    "Break Even": st.column_config.NumberColumn("Break Even", format="$%.2f", help="Price to cover fees"),
                    "Mark Price": st.column_config.NumberColumn("Mark Price", format="$%.2f"),
                    "Liq. Price": st.column_config.NumberColumn("Liq. Price", format="$%.2f"),
                    "Margin": st.column_config.NumberColumn("Margin", format="$%.2f"),
                    "PnL (ROE%)": st.column_config.NumberColumn(
                        "PnL (USDT)",
                        format="$%.2f",
                        help="Unrealized Profit & Loss"
                    ),
                    "Close": st.column_config.CheckboxColumn("Close Market", help="Close position immediately")
                },
                hide_index=True,
                use_container_width=True,
                key="positions_editor"
            )

            # Handle Close Actions
            if edited_df is not None:
                # Find rows where 'Close' is True
                to_close = edited_df[edited_df['Close'] == True]
                if not to_close.empty:
                    if 'service' in st.session_state and st.session_state.service:
                        service = st.session_state.service
                        if hasattr(service, 'paper_service'):
                            for index, row in to_close.iterrows():
                                position_id = row['id']
                                success = service.paper_service.close_position_by_id(position_id, current_price, "MANUAL_MARKET")
                                if success:
                                    st.toast(f"✅ Closed Position {row['Symbol']}")
                                    st.rerun()
        else:
            st.info("No open positions")
            
        st.markdown("---")
        
        # 3. Open Orders (Pending)
        pending_orders = self.repo.get_pending_orders()
        st.write("### Open Orders (Pending)")
        if pending_orders:
            data = []
            for order in pending_orders:
                side_emoji = "🟢" if order.side == 'LONG' else "🔴"
                data.append({
                    "Symbol": f"{side_emoji} {order.symbol}",
                    "Side": order.side,
                    "Type": "LIMIT",
                    "Price": f"${order.entry_price:,.2f}",
                    "Amount": f"{order.quantity:.4f}",
                    "TP/SL": f"{order.take_profit:,.2f} / {order.stop_loss:,.2f}",
                    "Time": order.open_time.strftime("%H:%M:%S")
                })
            st.dataframe(pd.DataFrame(data), use_container_width=True)
        else:
            st.info("No pending orders")

        st.markdown("---")
        
        # 4. Trade History
        st.write("### Trade History")
        if closed_positions:
            data = []
            for pos in closed_positions:
                data.append({
                    "Time": pos.close_time.strftime("%Y-%m-%d %H:%M") if pos.close_time else "-",
                    "Symbol": pos.symbol,
                    "Side": pos.side,
                    "Entry": pos.entry_price, # Store as float
                    "Realized PnL": pos.realized_pnl, # Store as float
                    "Reason": pos.exit_reason,
                    "Status": pos.status
                })
            
            df_history = pd.DataFrame(data)
            
            def color_pnl(val):
                if isinstance(val, (int, float)):
                    color = 'green' if val > 0 else 'red' if val < 0 else 'gray'
                    return f'color: {color}'
                return ''

            st.dataframe(
                df_history.style.map(color_pnl, subset=['Realized PnL']),
                column_config={
                    "Entry": st.column_config.NumberColumn("Entry", format="$%.2f"),
                    "Realized PnL": st.column_config.NumberColumn("Realized PnL", format="$%.2f")
                },
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No trade history")
