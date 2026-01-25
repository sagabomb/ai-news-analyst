import sqlite3
import os

DB_PATH = "foodie_memory.db"

def init_sources():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Create the table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sources (
            domain TEXT PRIMARY KEY,
            notes TEXT
        )
    """)
    
    # 2. Seed with our defaults
    defaults = [
        ("reddit.com", "Community discussions"),
        ("chowhound.com", "Serious foodies"),
        ("blogto.com", "Local Toronto coverage"),
        ("torontolife.com", "Magazine reviews"),
        ("eater.com", "High quality journalism"),
        ("yelp.ca", "User reviews (careful with these)")
    ]
    
    print("🛠️  Initializing Sources Table...")
    for domain, note in defaults:
        try:
            cursor.execute("INSERT INTO sources (domain, notes) VALUES (?, ?)", (domain, note))
            print(f"   + Added: {domain}")
        except sqlite3.IntegrityError:
            print(f"   . Exists: {domain}")
            
    conn.commit()
    conn.close()
    print("✅ Done. Configuration is now in the DB.")

if __name__ == "__main__":
    init_sources()