import sqlite3

DB_PATH = "foodie_memory.db"

new_sources = [
    # VIDEO
    ("youtube.com", "Vlog titles and descriptions (Good for 'Top 10' lists)"),
    
    # HIGH-QUALITY EDITORIAL (Global/US with Toronto presence)
    ("theinfatuation.com", "Highly trusted, specific reviews"),
    ("guide.michelin.com", "High-end/Bib Gourmand findings"),
    ("bonappetit.com", "Culinary journalism"),
    ("cntraveler.com", "Travel food guides"),
    
    # LOCAL GTA & CANADA MEDIA
    ("narcity.com", "Trendy, viral spots in Toronto"),
    ("curiocity.com", "Local happenings and food news"),
    ("streetsoftoronto.com", "Dedicated local coverage"),
    ("tastetoronto.com", "Visual-heavy local features"),
    ("cbc.ca/news/canada/toronto", "Occasional high-quality food reporting")
]

def update_sources():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("🛠️  Upgrading Source List...")
    for domain, note in new_sources:
        try:
            cursor.execute("INSERT INTO sources (domain, notes) VALUES (?, ?)", (domain, note))
            print(f"   + Added: {domain}")
        except sqlite3.IntegrityError:
            print(f"   . Already exists: {domain}")
            
    conn.commit()
    conn.close()
    print("✅ Database updated.")

if __name__ == "__main__":
    update_sources()