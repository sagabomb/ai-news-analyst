import sqlite3

DB_PATH = "foodie_memory.db"

def clean_house():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Option A: The Nuclear Option (Delete EVERYTHING)
    # c.execute("DELETE FROM restaurants")
    
    # Option B: The Precision Strike (Delete stuff you don't want)
    # This deletes anything that DOESN'T have your new keywords in the name or notes
    keywords = ['omakase', 'chicken rice', 'sushi']
    query = "DELETE FROM restaurants WHERE " + " AND ".join([f"name NOT LIKE '%{k}%' AND notes NOT LIKE '%{k}%'" for k in keywords])
    
    print(f"Running cleanup...")
    c.execute(query)
    
    deleted_count = c.rowcount
    conn.commit()
    conn.close()
    print(f"🧹 Swept away {deleted_count} irrelevant entries.")

if __name__ == "__main__":
    clean_house()