import sqlite3

DB_PATH = "foodie_memory.db"

def upgrade_database():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    print("👟 Upgrading Database for Project 2...")

    # 1. USERS Table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER UNIQUE,
        username TEXT
    )''')

    # 2. PREFERENCES Table (Your Profile)
    c.execute('''CREATE TABLE IF NOT EXISTS preferences (
        pref_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        shoe_size REAL,
        category TEXT, -- 'road', 'trail'
        brands TEXT,   -- 'nike,saucony'
        FOREIGN KEY(user_id) REFERENCES users(user_id)
    )''')

    # 3. WATCHED_URLS Table (The "Target List")
    c.execute('''CREATE TABLE IF NOT EXISTS watched_urls (
        url_id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT UNIQUE,
        site_name TEXT, 
        source TEXT,    -- 'manual' or 'navigator'
        status TEXT DEFAULT 'active'
    )''')

    conn.commit()
    conn.close()
    print("✅ Database Upgrade Complete.")

if __name__ == "__main__":
    upgrade_database()