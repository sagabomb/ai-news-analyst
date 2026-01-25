import backend
import time
from datetime import datetime

def run_sentinel():
    print(f"🤖 SENTINEL V2 STARTING: {datetime.now()}")
    
    watchlist = backend.get_watchlist()
    if not watchlist:
        print("💤 Watchlist is empty.")
        return

    print(f"📋 Found {len(watchlist)} active targets.")

    for target in watchlist:
        food = target['food_item']
        loc = target['location']
        print(f"\n🔎 Hunting for: {food} in {loc}...")

        # CALL THE SMART FUNCTION
        candidates = backend.search_and_analyze(food, loc)
        
        new_count = 0
        for spot in candidates:
            # logic is already inside 'save_restaurant' to handle duplicates
            status = backend.save_restaurant(spot)
            
            if status == "Saved":
                print(f"   ✅ DISCOVERED: {spot.name} ({spot.taste_rating}/10)")
                new_count += 1
            else:
                print(f"   (duplicate): {spot.name}")

        print(f"   -> Finished {food}. Added {new_count} validated spots.")
        time.sleep(2) # Be polite

    print(f"\n🏁 SENTINEL FINISHED")

if __name__ == "__main__":
    run_sentinel()