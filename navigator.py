import os
import sqlite3
from tavily import TavilyClient
from dotenv import load_dotenv

# --- CONFIG ---
load_dotenv()
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
DB_PATH = "foodie_memory.db"

# --- THE NAVIGATOR AGENT ---
def find_new_stores():
    """
    Uses Tavily Search to discover running shoe retailers.
    Saves new discoveries to the 'watched_urls' table.
    """
    print("🧭 Navigator: Scanning the horizon for shoe stores...")
    
    if not TAVILY_API_KEY:
        print("❌ Error: TAVILY_API_KEY not found in .env")
        return

    # 1. SEARCH PHASE
    # We ask for sites that specifically sell running shoes in Canada
    client = TavilyClient(api_key=TAVILY_API_KEY)
    
    queries = [
        "best online running shoe stores Canada",
        "independent running shops Ontario online sales",
        "running room canada deals",
        "black toe running toronto shop"
    ]
    
    discovered_urls = []
    
    for q in queries:
        print(f"   Searching: '{q}'...")
        try:
            # depth="advanced" gets better results than basic
            response = client.search(query=q, search_depth="basic", max_results=5)
            
            for result in response.get('results', []):
                url = result['url']
                title = result['title']
                
                # Basic filter: Skip giant generic sites if we want niche ones
                if "amazon" in url or "pinterest" in url or "instagram" in url:
                    continue
                    
                discovered_urls.append((url, title))
        except Exception as e:
            print(f"   ⚠️ Search error: {e}")

    # 2. MEMORY PHASE (Save to DB)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    new_count = 0
    
    print(f"🧭 Navigator: Found {len(discovered_urls)} potential sites. Filtering duplicates...")
    
    for url, title in discovered_urls:
        try:
            # We treat 'title' as the site_name for now
            c.execute('''
                INSERT INTO watched_urls (url, site_name, source) 
                VALUES (?, ?, 'navigator_agent')
            ''', (url, title))
            new_count += 1
            print(f"   ✅ Added: {title}")
        except sqlite3.IntegrityError:
            # This means the URL is already in our DB (Duplicate)
            pass
            
    conn.commit()
    conn.close()
    
    if new_count == 0:
        print("🧭 Navigator: No NEW sites found (all duplicates).")
    else:
        print(f"🧭 Navigator: Successfully added {new_count} new stores to the Watch List.")

if __name__ == "__main__":
    find_new_stores()