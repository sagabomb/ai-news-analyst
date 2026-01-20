import os
import sqlite3
from typing import Literal, List, Dict
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from tavily import TavilyClient
from pydantic import BaseModel, Field

# 1. SETUP
current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(current_dir, '.env')
load_dotenv(env_path)
API_KEY = os.getenv("TAVILY_API_KEY")

# DATABASE SETUP
# This creates a file 'foodie_memory.db' in your folder.
DB_PATH = os.path.join(current_dir, "foodie_memory.db")

def init_db():
    """Creates the table if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS restaurants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            neighborhood TEXT,
            taste_rating INTEGER,
            notes TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Initialize DB on startup
init_db()

mcp = FastMCP("Markham Foodie Agent")

# 2. DATA STRUCTURE
class RestaurantReview(BaseModel):
    name: str = Field(description="Name of the restaurant")
    neighborhood: str = Field(description="The specific area")
    taste_rating: int = Field(description="1-10 rating on flavor")
    notes: str = Field(description="Short summary of why it's good or bad")

# --- TOOL 1: THE MEMORY CHECK ---
@mcp.tool()
def check_my_food_history() -> str:
    """
    Checks the local database to see what restaurants the user has already tracked.
    Use this BEFORE searching to avoid repeating suggestions.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT name, taste_rating, notes FROM restaurants')
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        return "Memory is empty. No past restaurants found."
    
    history = "Here are the places we already know about:\n"
    for row in rows:
        history += f"- {row[0]}: Rated {row[1]}/10. Notes: {row[2]}\n"
    return history

# --- TOOL 2: THE SCOUT (Web Search) ---
@mcp.tool()
def search_new_spots(dish: str, location: str) -> str:
    """
    Searches for NEW spots. 
    Use 'check_my_food_history' first to know what to ignore.
    """
    if not API_KEY: return "Error: API Key missing."
    client = TavilyClient(api_key=API_KEY)

    # Negative prompting to avoid generic lists
    query = f"best authentic {dish} in {location} reddit forum discussion -site:yelp.ca -site:tripadvisor.ca"
    response = client.search(query, max_results=5)
    
    results = []
    for r in response['results']:
        results.append(f"Found: {r['title']}\nSnippet: {r['content']}\n---")
    return "\n".join(results)

# --- TOOL 3: THE MEMORY WRITER ---
@mcp.tool()
def remember_restaurant(review: RestaurantReview) -> str:
    """
    Saves a restaurant to the permanent database.
    Use this when you find a high-quality candidate worth remembering.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR IGNORE INTO restaurants (name, neighborhood, taste_rating, notes)
            VALUES (?, ?, ?, ?)
        ''', (review.name, review.neighborhood, review.taste_rating, review.notes))
        conn.commit()
        conn.close()
        return f"SUCCESS: I have memorized {review.name}."
    except Exception as e:
        return f"Error saving to DB: {e}"

if __name__ == "__main__":
    mcp.run()