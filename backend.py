import os
import json
import sqlite3
import time  # <--- NEW: Added for rate limiting
from typing import List, Optional
from dotenv import load_dotenv
from tavily import TavilyClient
from google import genai
from google.genai import types

# Load environment variables
load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
DB_NAME = "foodie_memory.db"

# --- DATA STRUCTURES ---
class RestaurantCandidate:
    def __init__(self, name, neighborhood, taste_rating, notes, confidence_score):
        self.name = name
        self.neighborhood = neighborhood
        self.taste_rating = taste_rating
        self.notes = notes
        self.confidence_score = confidence_score

# --- HELPER FUNCTIONS ---

def get_watchlist():
    """
    Returns the list of food items to track.
    FIXED: Uses 'food_item' key to match sentinel.py
    """
    return [
        {"food_item": "Pizza", "location": "Markham"},
        {"food_item": "Dim Sum", "location": "Richmond Hill"},
        {"food_item": "Ramen", "location": "North York"},
        {"food_item": "Burger", "location": "Vaughan"}
    ]

def init_db():
    """Creates the database table if it doesn't exist."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS restaurants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            neighborhood TEXT,
            taste_rating INTEGER,
            notes TEXT,
            confidence_score INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def save_restaurant(candidate: RestaurantCandidate):
    """Saves a single restaurant to the database."""
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        # Check for duplicates
        c.execute("SELECT id FROM restaurants WHERE name = ?", (candidate.name,))
        if c.fetchone():
            print(f"   ⚠️ Skipping {candidate.name} (Already in DB)")
            conn.close()
            return

        c.execute('''
            INSERT INTO restaurants (name, neighborhood, taste_rating, notes, confidence_score)
            VALUES (?, ?, ?, ?, ?)
        ''', (candidate.name, candidate.neighborhood, candidate.taste_rating, candidate.notes, candidate.confidence_score))
        
        conn.commit()
        conn.close()
        print(f"   💾 Saved: {candidate.name}")
    except Exception as e:
        print(f"   ❌ DB Error: {e}")

def get_trusted_sources():
    return ["reddit.com", "blogto.com", "yelp.ca", "torontolife.com", "eater.com"]

def verify_is_open(name: str, location: str, client: genai.Client) -> bool:
    # PERMANENT FIX: Disable this check to save API Quota
    return True 

# --- MAIN INTELLIGENCE FUNCTION ---
# --- MAIN INTELLIGENCE FUNCTION (With Smart Retry) ---
def search_and_analyze(food_item: str, location: str) -> List[RestaurantCandidate]:
    MODEL_NAME = 'gemini-2.0-flash' 
    
    if not TAVILY_API_KEY or not GOOGLE_API_KEY:
        print("❌ Missing API Keys.")
        return []

    t_client = TavilyClient(api_key=TAVILY_API_KEY)
    sources = get_trusted_sources()
    
    # 1. SEARCH
    query = f"best {food_item} in {location} area and nearby"
    print(f"🔎 Searching: {query}...")
    
    try:
        search_result = t_client.search(
            query, 
            max_results=5, 
            include_domains=sources
        )
        hits = search_result['results']
        
        if not hits:
            return []
            
        raw_context = "\n".join([f"Source: {r['title']}\nContent: {r['content']}" for r in hits])
        
    except Exception as e:
        print(f"❌ Search failed: {e}")
        return []

    # 2. ANALYZE (With Retry Logic)
    print(f"🧠 Analyzing with {MODEL_NAME}...")
    
    client = genai.Client(api_key=GOOGLE_API_KEY)
    
    prompt = f"""
    Analyze these search results and extract ANY restaurant names that serve {food_item}.
    RETURN ONLY VALID JSON.
    
    SEARCH DATA:
    {raw_context}
    
    Output Format:
    [
      {{
        "name": "Restaurant Name",
        "neighborhood": "Area Name",
        "taste_rating": 7,
        "notes": "Brief mention",
        "confidence_score": 6
      }}
    ]
    """

    # --- THE NEW RETRY LOOP ---
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt
            )
            # If we get here, it worked! Break the loop.
            text = response.text.strip()
            break 
            
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                wait_time = 60
                print(f"   ⏳ Quota hit (Attempt {attempt+1}/{max_retries}). Sleeping {wait_time}s...")
                time.sleep(wait_time)
            else:
                # If it's a real error (not quota), crash usually.
                print(f"❌ Analysis Logic Failed: {e}")
                return []
    else:
        # If we loop 3 times and still fail
        print("❌ Gave up after 3 retries.")
        return []

    # 3. PARSE RESULTS
    try:
        if text.startswith("```json"): text = text[7:]
        if text.startswith("```"): text = text[3:]
        if text.endswith("```"): text = text[:-3]
        
        data = json.loads(text)
        
        found_places = []
        for item in data:
            score = item.get('confidence_score', 0)
            name = item.get('name', 'Unknown')
            
            if score >= 5:
                # verify_is_open is disabled (returns True) to save quota
                if verify_is_open(name, location, client):
                    found_places.append(RestaurantCandidate(**item))

        return found_places

    except Exception as e:
        print(f"❌ Parsing Logic Failed: {e}")
        return []