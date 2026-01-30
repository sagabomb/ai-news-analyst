import os
import sqlite3
import json
from typing import List, Dict, Optional
from dotenv import load_dotenv
from tavily import TavilyClient
import google.generativeai as genai
from pydantic import BaseModel, Field

# 1. SETUP
load_dotenv()
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

current_dir = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(current_dir, "foodie_memory.db")

# Configure Gemini
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

# --- DATA MODELS ---
class RestaurantCandidate(BaseModel):
    name: str
    neighborhood: str
    taste_rating: int
    notes: str
    confidence_score: int

# --- DATABASE FUNCTIONS (Standard) ---
def get_watchlist() -> List[Dict]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM watchlist")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_trusted_sources() -> List[str]:
    """Fetch all active domains from the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT domain FROM sources")
    rows = cursor.fetchall()
    conn.close()
    # Return a clean list: ['reddit.com', 'blogto.com', ...]
    return [row[0] for row in rows]

def add_to_watchlist(food_item: str, location: str = "Markham") -> str:
    clean_food = food_item.strip().title()
    clean_loc = location.strip().title()
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO watchlist (food_item, location, last_checked) VALUES (?, ?, ?)", 
                       (clean_food, clean_loc, "Never"))
        if cursor.rowcount == 0:
            return f"⚠️ '{clean_food}' is already in your watchlist!"
        conn.commit()
        return f"✅ Added '{clean_food}'."
    except Exception as e:
        return f"❌ Error: {e}"

def get_all_restaurants() -> List[Dict]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM restaurants ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def save_restaurant(candidate: RestaurantCandidate) -> str:
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR IGNORE INTO restaurants (name, neighborhood, taste_rating, notes) VALUES (?, ?, ?, ?)",
            (candidate.name, candidate.neighborhood, candidate.taste_rating, candidate.notes)
        )
        conn.commit()
        if cursor.rowcount == 0:
            return "Duplicate"
        return "Saved"
    except Exception as e:
        return f"Error: {e}"

# --- INTELLIGENCE FUNCTIONS (Gemini Powered) ---

# ... (Imports and Setup remain the same) ...

# --- INTELLIGENCE FUNCTIONS (Gemini Pro Fixed) ---

# ... (Keep your imports and DB setup at the top) ...

# --- NEW VERIFICATION FUNCTION ---
def verify_is_open(name: str, location: str, model_name: str) -> bool:
    """
    Performs a specific 'sanity check' search to see if a place is closed.
    Returns TRUE if open, FALSE if closed.
    """
    print(f"   🕵️‍♀️ Verifying status for: {name}...")
    t_client = TavilyClient(api_key=TAVILY_API_KEY)
    
    # Specific query to catch closures
    query = f"is {name} in {location} permanently closed? restaurant hours"
    
    try:
        # We only need 2 results to check status
        search_result = t_client.search(query, max_results=2)
        content = "\n".join([r['content'] for r in search_result['results']])
        
        # Ask Gemini to be the judge
        model = genai.GenerativeModel(model_name)
        prompt = f"""
        Based on these search results, is the restaurant '{name}' PERMANENTLY CLOSED?
        
        SEARCH DATA:
        {content}
        
        RULES:
        - If it says "Permanently closed", return "CLOSED".
        - If it mentions current hours or recent reviews, return "OPEN".
        - If uncertain, assume "OPEN".
        - Respond with ONE word: OPEN or CLOSED.
        """
        
        response = model.generate_content(prompt)
        status = response.text.strip().upper()
        
        if "CLOSED" in status:
            print(f"   ❌ DETECTED CLOSURE: {name} is closed. Skipping.")
            return False
        else:
            print(f"   ✅ Verified Open: {name}")
            return True
            
    except Exception as e:
        print(f"   ⚠️ Verification failed ({e}). Assuming open.")
        return True

# --- MAIN INTELLIGENCE FUNCTION ---
# --- MAIN INTELLIGENCE FUNCTION ---
def search_and_analyze(food_item: str, location: str) -> List[RestaurantCandidate]:
    MODEL_NAME = 'gemini-flash-latest'
    
    if not TAVILY_API_KEY or not GOOGLE_API_KEY:
        print("❌ Missing API Keys.")
        return []

    t_client = TavilyClient(api_key=TAVILY_API_KEY)
    
    # 1. SETUP SOURCES
    sources = get_trusted_sources()
    if not sources:
        sources = ["reddit.com", "blogto.com", "yelp.ca"]
    
    # 2. SEARCH (Fixed: Moved domains to 'include_domains' parameter)
    query = f"best {food_item} in {location} area and nearby"
    print(f"🔎 Searching: {query} (checking {len(sources)} specific sites)...")
    
    try:
        # We pass the list of sites strictly to 'include_domains' to avoid the 400 char limit
        search_result = t_client.search(
            query, 
            max_results=5, 
            include_domains=sources
        )
        hits = search_result['results']
        
        # DEBUG: Print titles
        print(f"   --> Tavily Titles Found:")
        for h in hits:
            print(f"       - {h['title'][:60]}...") 
            
        if not hits:
            return []
            
        raw_context = "\n".join([f"Source: {r['title']}\nContent: {r['content']}" for r in hits])
        
    except Exception as e:
        print(f"❌ Search failed: {e}")
        return []

    # 3. ANALYZE (Gemini)
    print(f"🧠 Analyzing with {MODEL_NAME}...")
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        
        prompt = f"""
        Analyze these search results and extract ANY restaurant names that serve {food_item}.
        
        RULES:
        1. Extract specific restaurant names.
        2. Guess the neighborhood.
        3. Return a VALID JSON list.
        
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

        response = model.generate_content(prompt)
        text = response.text.strip()
        
        # Clean JSON
        if text.startswith("```json"): text = text[7:]
        if text.startswith("```"): text = text[3:]
        if text.endswith("```"): text = text[:-3]
        
        data = json.loads(text)
        print(f"   --> Gemini extracted {len(data)} raw items.")
        
        found_places = []
        for item in data:
            score = item.get('confidence_score', 0)
            name = item.get('name', 'Unknown')
            
            # 4. VERIFY STATUS
            if score >= 5:
                # Use the helper function to check if it's open
                if verify_is_open(name, location, MODEL_NAME):
                    found_places.append(RestaurantCandidate(**item))
            else:
                print(f"   ⚠️ REJECTED: {name} (Score {score} too low)")

        return found_places

    except Exception as e:
        print(f"❌ Analysis Logic Failed: {e}")
        return []