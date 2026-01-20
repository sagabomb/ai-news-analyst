import os
import csv
from typing import Literal
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from tavily import TavilyClient
from pydantic import BaseModel, Field

# 1. SETUP
current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(current_dir, '.env')
load_dotenv(env_path)
API_KEY = os.getenv("TAVILY_API_KEY")

mcp = FastMCP("Markham Foodie Agent")

# 2. THE NEW "STRICT" DATA STRUCTURE
# This solves the "Priorities" and "Distance" issues by capturing granular data.
class RestaurantReview(BaseModel):
    name: str = Field(description="Name of the restaurant")
    neighborhood: str = Field(description="The specific area (e.g., 'Unionville', 'First Markham Place', 'Steeles/Woodbine')")
    address: str = Field(description="The street address (for proximity checks)")
    
    # We split the scores so you can filter by what matters
    taste_rating: int = Field(description="1-10 rating purely on flavor quality")
    authenticity_rating: int = Field(description="1-10 rating on traditional preparation (non-westernized)")
    value_rating: int = Field(description="1-10 rating on price-to-portion ratio")
    
    price_estimate: float = Field(description="Estimated price per person in CAD (number only)")
    best_dish: str = Field(description="The specific dish to order here")

# --- TOOL 1: THE SMART SCOUT ---
@mcp.tool()
def search_food_reviews(dish: str, location: str, source_type: Literal["social", "general"] = "social") -> str:
    """
    Searches for restaurant reviews.
    - Adds 'negative keywords' to ban generic SEO sites.
    - Looks for 'neighbors' of the location automatically.
    """
    if not API_KEY: return "Error: API Key missing."
    client = TavilyClient(api_key=API_KEY)

    # 1. Negative Prompting (The "Quality" Fix)
    # We explicitly tell the search engine to ignore generic aggregators
    exclusions = "-site:yelp.ca -site:tripadvisor.ca -site:narcity.com -site:blogto.com"
    
    if source_type == "social":
        # Look for passionate arguments on Reddit/Chowhound
        query = f"best authentic {dish} near {location} reddit forum discussion {exclusions}"
    else:
        # Look for deep-dive food blogs or articles
        query = f"best {dish} in {location} review hidden gem {exclusions}"

    response = client.search(query, topic="general", max_results=7)
    
    results = []
    for result in response['results']:
        results.append(f"Source: {result['title']}\nLink: {result['url']}\nSnippet: {result['content']}\n---")
    return "\n".join(results)

# --- TOOL 2: THE ANALYST (Saver) ---
@mcp.tool()
def save_structured_review(review: RestaurantReview) -> str:
    """
    Saves the restaurant data to CSV.
    Only call this if the restaurant is in the target city OR immediate neighboring areas.
    """
    desktop = os.path.expanduser("~/Desktop")
    file_path = os.path.join(desktop, "restaurant_data.csv")
    file_exists = os.path.exists(file_path)
    
    try:
        with open(file_path, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # Write Header with new columns
            if not file_exists:
                writer.writerow([
                    "Name", "Neighborhood", "Address", 
                    "Taste (/10)", "Authenticity (/10)", "Value (/10)", 
                    "Price ($)", "Must Order"
                ])
            
            # Write Data
            writer.writerow([
                review.name, 
                review.neighborhood,
                review.address,
                review.taste_rating,
                review.authenticity_rating,
                review.value_rating,
                review.price_estimate, 
                review.best_dish
            ])
        return f"Saved {review.name} ({review.neighborhood}) to CSV."
    except Exception as e:
        return f"Error saving CSV: {e}"

if __name__ == "__main__":
    mcp.run()