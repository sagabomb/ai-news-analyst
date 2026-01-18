import os
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from tavily import TavilyClient

# 1. LOAD SECRETS (Bulletproof Method)
# We tell Python: "Look for the .env file exactly where this script lives"
# This prevents path errors when Claude launches the app.
current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(current_dir, '.env')
load_dotenv(env_path)

# 2. GET THE KEY
API_KEY = os.getenv("TAVILY_API_KEY")

# 3. INITIALIZE SERVER
mcp = FastMCP("News Analyst Agent")

# --- TOOL 1: Hype Analyzer ---
@mcp.tool()
def analyze_hype_level(text: str) -> int:
    """
    Analyzes text and returns a hype score from 0 to 100.
    Higher score means more sensationalist language.
    """
    hype_words = ["revolutionary", "breakthrough", "agentic", "transform", "incredible", "boom", "future"]
    score = 0
    text_lower = text.lower()
    for word in hype_words:
        if word in text_lower:
            score += 10
    return min(score, 100)

# --- TOOL 2: Tavily Search (Secure) ---
@mcp.tool()
def web_search(query: str) -> str:
    """
    Search the real internet for current events, news, or facts using Tavily.
    Use this when the user asks about recent topics or live data.
    """
    # Safety Check: Did the user forget the .env file?
    if not API_KEY:
        return "Error: TAVILY_API_KEY not found. Please check your .env file."

    try:
        # Initialize Client
        client = TavilyClient(api_key=API_KEY)
        
        # Perform Search
        response = client.search(query, topic="news", max_results=3)
        
        # Format results
        formatted_results = []
        for result in response['results']:
            title = result.get('title', 'No Title')
            url = result.get('url', '#')
            content = result.get('content', 'No Content')
            formatted_results.append(f"Title: {title}\nSource: {url}\nContent: {content}\n---")
        
        return "\n".join(formatted_results)

    except Exception as e:
        return f"Search Error: {str(e)}"

# 4. RUN IT
if __name__ == "__main__":
    mcp.run()