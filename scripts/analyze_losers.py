import sqlite3
import pandas as pd
from datetime import datetime

# Connect to database
conn = sqlite3.connect('data/trading_system.db')

# Query last 20 closed positions to find 5 losers
query = """
SELECT 
    id, symbol, side, entry_price, quantity,
    highest_price, lowest_price, 
    realized_pnl as pnl, exit_reason, open_time, close_time
FROM paper_positions 
WHERE status = 'CLOSED'
ORDER BY close_time DESC
LIMIT 20
"""

df = pd.read_sql_query(query, conn)
conn.close()

# Filter for losing trades (PnL < 0)
losing_trades = df[df['pnl'] < 0].head(5)

print("--- LAST 5 LOSING TRADES ---")
if losing_trades.empty:
    print("No losing trades found.")
else:
    for index, row in losing_trades.iterrows():
        entry = row['entry_price']
        pnl = row['pnl']
        qty = row['quantity']
        side = row['side']
        
        # Calculate Exit Price from PnL
        # PnL = (Exit - Entry) * Qty  (LONG)
        # PnL = (Entry - Exit) * Qty  (SHORT)
        if side == 'LONG':
            exit_p = entry + (pnl / qty)
            mfe_price = row['highest_price']
            if mfe_price == 0: mfe_price = entry
            mfe_pct = ((mfe_price - entry) / entry) * 100
        else:
            exit_p = entry - (pnl / qty)
            mfe_price = row['lowest_price']
            if mfe_price == 0: mfe_price = entry
            mfe_pct = ((entry - mfe_price) / entry) * 100
            
        # Calculate Fees (0.05% per side = 0.1% total)
        # Fee = Entry * Qty * 0.0005 + Exit * Qty * 0.0005
        fee_entry = entry * qty * 0.0005
        fee_exit = exit_p * qty * 0.0005
        total_fee = fee_entry + fee_exit
        net_pnl = pnl - total_fee
        
        print(f"ID: {row['id']} | {side} | Entry: {entry:.4f} | Exit: {exit_p:.4f}")
        print(f"   Gross PnL: {pnl:.2f} | Net PnL (w/ Fees): {net_pnl:.2f} | Fees: {total_fee:.2f}")
        print(f"   MFE Price: {mfe_price:.4f} | MFE %: {mfe_pct:.2f}%")
        print(f"   Reason: {row['exit_reason']} | Time: {row['close_time']}")
        print("-" * 30)
