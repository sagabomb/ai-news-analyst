import sqlite3
import os

# 1. Setup Paths
current_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(current_dir, "foodie_memory.db")

print(f"📂 Updating Database at: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 2. Create 'restaurants' table (The Memory) - Existing
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS restaurants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            neighborhood TEXT,
            taste_rating INTEGER,
            notes TEXT
        )
    ''')

    # 3. Create 'watchlist' table (The Preferences) - NEW
    # This stores WHAT you want to track
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS watchlist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            food_item TEXT UNIQUE,
            location TEXT,
            last_checked TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ SUCCESS: Database schema updated.")

except Exception as e:
    print(f"❌ ERROR: {e}")