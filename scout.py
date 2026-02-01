import sqlite3
import requests
from bs4 import BeautifulSoup
import time
import random
import re  # <--- NEW: Regex library to find patterns like $100

DB_PATH = "foodie_memory.db"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def get_user_brands():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT brands FROM preferences LIMIT 1")
    row = c.fetchone()
    conn.close()
    if row and row[0]:
        return [b.strip().lower() for b in row[0].split(',')]
    return ['nike', 'hoka', 'saucony']

def extract_price(text):
    """
    Scans text for price patterns like $129.99 or $99.
    Returns the first valid float found, or 0.0 if nothing.
    """
    # Look for $ followed by digits and optional decimals
    # Matches: $100, $99.99, $1,200.50
    match = re.search(r'\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)', text)
    if match:
        price_str = match.group(1).replace(',', '') # Remove commas
        try:
            return float(price_str)
        except:
            return 0.0
    return 0.0

def run_scout():
    print("🔭 Scout v1.1: Hunting for prices...")
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Get active URLs
    c.execute("SELECT url_id, url, site_name FROM watched_urls WHERE status='active'")
    targets = c.fetchall()
    target_brands = get_user_brands()
    
    if not targets:
        print("   ⚠️ No URLs to scout.")
        return

    for url_id, url, site_name in targets:
        print(f"\n   Visiting: {site_name}...")
        
        try:
            time.sleep(random.uniform(1, 3))
            response = requests.get(url, headers=HEADERS, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                page_text = soup.get_text().lower()
                
                # Check for brands
                found_brands = [b for b in target_brands if b in page_text]
                
                if found_brands:
                    # NEW: Try to find a real price
                    # We look at the raw text of the whole page (simple method)
                    price_guess = extract_price(soup.get_text())
                    
                    print(f"      ✅ Brands: {', '.join(found_brands)}")
                    print(f"      💰 Best Price Guess: ${price_guess}")
                    
                    # Only save if we found a price > 0 OR explicit sale keywords
                    if price_guess > 0 or "sale" in page_text:
                        c.execute('''
                            INSERT INTO price_history (shoe_name, price, url, currency)
                            VALUES (?, ?, ?, ?)
                        ''', (f"Found {found_brands[0]}", price_guess, url, "CAD"))
                        conn.commit()
                else:
                    print("      ❌ No target brands.")
            else:
                print(f"      ⚠️ Status: {response.status_code}")
                
        except Exception as e:
            print(f"      ⚠️ Error: {e}")

    conn.close()
    print("\n🔭 Mission Complete.")

if __name__ == "__main__":
    run_scout()