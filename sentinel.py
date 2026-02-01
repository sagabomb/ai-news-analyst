import backend
import datetime
import time

def run_sentinel():
    print(f"🤖 SENTINEL V2 STARTING: {datetime.datetime.now()}")
    
    # 1. Initialize the Database (Critical Step)
    backend.init_db()
    
    # 2. Get the Target List
    watchlist = backend.get_watchlist()
    print(f"📋 Found {len(watchlist)} active targets.")

    # 3. Run the Loop
    for target in watchlist:
        # Note: These keys match backend.get_watchlist()
        food = target['food_item']
        loc = target['location']
        
        print(f"\n--- 🎯 TARGET: {food} in {loc} ---")
        
        # Run the Intelligence Agent
        candidates = backend.search_and_analyze(food, loc)
        
        # Run the Memory Agent
        if candidates:
            print(f"   ✅ Found {len(candidates)} candidates.")
            for place in candidates:
                backend.save_restaurant(place)
        else:
            print("   💤 No new results found.")

    print("\n🏁 SENTINEL RUN COMPLETE.")

if __name__ == "__main__":
    run_sentinel()