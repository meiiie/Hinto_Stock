import sqlite3
import os

DB_PATH = "data/trading_system.db"

def initialize_db():
    """Initialize the database with required tables"""
    # Ensure data directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create paper_orders table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS paper_orders (
            id TEXT PRIMARY KEY,
            symbol TEXT NOT NULL,
            side TEXT NOT NULL,
            status TEXT NOT NULL,
            entry_price REAL,
            quantity REAL,
            stop_loss REAL,
            take_profit_1 REAL,
            take_profit_2 REAL,
            entry_time TEXT,
            close_time TEXT,
            pnl REAL DEFAULT 0.0,
            exit_reason TEXT
        )
    ''')
    
    # Create paper_account table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS paper_account (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            balance REAL DEFAULT 10000.0,
            locked_balance REAL DEFAULT 0.0
        )
    ''')
    
    # Initialize account if not exists
    cursor.execute('INSERT OR IGNORE INTO paper_account (id, balance) VALUES (1, 10000.0)')
    
    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_PATH}")

if __name__ == "__main__":
    initialize_db()
