
import sqlite3
import os

def check_db():
    db_path = "data/paper_trading.db"
    print(f"Checking {db_path}...")
    
    if not os.path.exists(db_path):
        print("❌ DB file does not exist!")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='signals';")
        if not cursor.fetchone():
            print("❌ Table 'signals' does not exist!")
            return
            
        cursor.execute("SELECT COUNT(*) FROM signals")
        count = cursor.fetchone()[0]
        print(f"📊 Total Signals: {count}")
        
        cursor.execute("SELECT id, symbol, status, generated_at FROM signals ORDER BY generated_at DESC LIMIT 5")
        rows = cursor.fetchall()
        for row in rows:
            print(f"   - {row}")
            
        conn.close()
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_db()
