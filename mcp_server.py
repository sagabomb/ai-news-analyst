from mcp.server.fastmcp import FastMCP
import sqlite3
import json
import os

# 1. Define the Server
mcp = FastMCP("Foodie Sentinel")

# 2. Define Paths
# We use absolute paths to ensure OpenClaw finds the DB regardless of where it starts
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "foodie_memory.db")

@mcp.tool()
def get_recent_food_finds(limit: int = 5) -> str:
    """
    Retrieves the most recently found restaurants from the Foodie Sentinel database.
    Use this when the user asks 'What's new?', 'Any new pizza spots?', or 'What did you find?'.
    """
    try:
        # Check if DB exists
        if not os.path.exists(DB_PATH):
            return "Error: Database not found. Please run sentinel.py first."

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # We fetch the exact columns we defined in backend.py
        query = """
        SELECT name, neighborhood, taste_rating, notes, confidence_score, created_at 
        FROM restaurants 
        ORDER BY created_at DESC 
        LIMIT ?
        """
        cursor.execute(query, (limit,))
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return "No restaurants found in database yet."

        results = []
        for r in rows:
            results.append({
                "Restaurant": r[0],
                "Location": r[1],
                "Rating": f"{r[2]}/10",
                " AI_Notes": r[3],
                "Confidence": f"{r[4]}/10",
                "Found_On": r[5]
            })
        
        return json.dumps(results, indent=2)

    except Exception as e:
        return f"Error reading database: {str(e)}"

if __name__ == "__main__":
    mcp.run()