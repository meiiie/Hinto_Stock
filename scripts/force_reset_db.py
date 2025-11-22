import sqlite3
import os

DB_PATH = 'data/trading_system.db'

def force_reset_db():
    print(f"Targeting DB at: {os.path.abspath(DB_PATH)}")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 1. Drop existing tables
        print("Dropping tables...")
        cursor.execute("DROP TABLE IF EXISTS paper_orders")
        cursor.execute("DROP TABLE IF EXISTS paper_account")
        cursor.execute("DROP TABLE IF EXISTS paper_positions")
        
        # 2. Recreate paper_account table
        print("Creating paper_account table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS paper_account (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                balance REAL NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 3. Recreate paper_positions table (Futures Model)
        print("Creating paper_positions table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS paper_positions (
                id TEXT PRIMARY KEY,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,
                status TEXT NOT NULL,
                entry_price REAL NOT NULL,
                quantity REAL NOT NULL,
                leverage INTEGER DEFAULT 1,
                margin REAL NOT NULL,
                liquidation_price REAL,
                stop_loss REAL,
                take_profit REAL,
                open_time TEXT NOT NULL,
                close_time TEXT,
                realized_pnl REAL DEFAULT 0.0,
                exit_reason TEXT,
                highest_price REAL DEFAULT 0.0,
                lowest_price REAL DEFAULT 0.0
            )
        ''')
        
        # 4. Initialize Account Balance
        print("Initializing account balance to $10,000...")
        cursor.execute("INSERT INTO paper_account (id, balance) VALUES (1, 10000.0)")
        
        conn.commit()
        conn.close()
        print("✅ Database Force Reset Complete!")
        
    except Exception as e:
        print(f"❌ Error resetting database: {e}")

if __name__ == "__main__":
    force_reset_db()
