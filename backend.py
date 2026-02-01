import os
import json
import sqlite3
import time
from typing import List, Optional
from dotenv import load_dotenv
from tavily import TavilyClient
from google import genai
from google.genai import types
import datetime

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

# --- HELPER FUNCTIONS (These were missing before) ---

def get_watchlist():
    """Returns the list of food items to track."""
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
    """Saves a single restaurant to the database with LOCAL TIME."""
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        # Check for duplicates by name
        c.execute("SELECT id FROM restaurants WHERE name = ?", (candidate.name,))
        if c.fetchone():
            print(f"   ⚠️ Skipping {candidate.name} (Already in DB)")
            conn.close()
            return

        # NEW: We calculate the local time explicitly
        local_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # UPDATED SQL: We now insert 'created_at' manually
        c.execute('''
            INSERT INTO restaurants (name, neighborhood, taste_rating, notes, confidence_score, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (candidate.name, candidate.neighborhood, candidate.taste_rating, candidate.notes, candidate.confidence_score, local_time))
        
        conn.commit()
        conn.close()
        print(f"   💾 Saved: {candidate.name}")
    except Exception as e:
        print(f"   ❌ DB Error: {e}")

def get_trusted_sources():
    return ["reddit.com", "blogto.com", "yelp.ca", "torontolife.com", "eater.com"]

def verify_is_open(name: str, location: str, client: genai.Client) -> bool:
    """
    Uses Gemini to strictly verify if the place is permanently closed.
    """
    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=f"Is the restaurant '{name}' in '{location}' permanently closed? Answer only YES or NO."
        )
        answer = response.text.strip().upper()
        
        if "YES" in answer:
            print(f"   ❌ Rejected {name} (Permanently Closed)")
            return False
        return True
    except:
        return True # Default to keep if AI fails

# --- MAIN INTELLIGENCE FUNCTION ---
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

    # 2. ANALYZE
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

    # Retry Loop for Stability
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt
            )
            text = response.text.strip()
            break 
            
        except Exception as e:
            # If we hit a rate limit (even on paid tier), wait briefly
            if "429" in str(e):
                print(f"   ⏳ Network Busy (Attempt {attempt+1}), waiting 5s...")
                time.sleep(5)
            else:
                print(f"   ⚠️ API Glitch (Attempt {attempt+1}): {e}")
            
            if attempt == max_retries - 1:
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
                if verify_is_open(name, location, client):
                    found_places.append(RestaurantCandidate(**item))

        return found_places

    except Exception as e:
        print(f"❌ Parsing Logic Failed: {e}")
        return []