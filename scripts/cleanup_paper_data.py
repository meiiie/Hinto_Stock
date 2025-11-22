import sqlite3
import os

DB_PATH = os.path.join('data', 'trading_system.db')

def cleanup_data():
    print(f"Connecting to database: {DB_PATH}")
    
    if not os.path.exists(DB_PATH):
        print("❌ Database not found!")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check for orders with entry price < 60000 (Old test data)
        cursor.execute("SELECT count(*) FROM paper_orders WHERE entry_price < 60000")
        count = cursor.fetchone()[0]
        
        if count > 0:
            print(f"Found {count} invalid orders (Entry < $60k). Deleting...")
            cursor.execute("DELETE FROM paper_orders WHERE entry_price < 60000")
            conn.commit()
            print("✅ Cleanup complete!")
        else:
            print("✅ No invalid orders found.")
            
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    cleanup_data()
