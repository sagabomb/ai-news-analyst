import streamlit as st
import backend
import pandas as pd

# 1. PAGE SETUP
st.set_page_config(page_title="The Foodie Sentinel", page_icon="🍜", layout="wide")
st.title("🍜 The Foodie Sentinel")
st.markdown("Automated Research & Discovery Engine")

# --- SIDEBAR: CONTROLS ---
with st.sidebar:
    st.header("Add to Watchlist")
    st.markdown("What food should the Sentinel hunt for?")
    
    # Input fields
    new_food = st.text_input("Food Item", placeholder="e.g. Omakase")
    new_loc = st.text_input("Location", value="Markham")
    
    # The Action Button
    if st.button("Start Watching", type="primary"):
        if new_food:
            # CALL THE BACKEND
            msg = backend.add_to_watchlist(new_food, new_loc)
            if "✅" in msg:
                st.success(msg)
            else:
                st.error(msg)
        else:
            st.warning("Please enter a food name.")

    st.divider()
    st.caption(f"Database: `{backend.DB_PATH}`")

# --- MAIN PAGE: TABS ---
tab1, tab2 = st.tabs(["📋 Watchlist Configuration", "🍽️ The Black Book"])

# TAB 1: What are we looking for?
with tab1:
    st.subheader("Active Search Targets")
    watchlist_data = backend.get_watchlist()
    
    if watchlist_data:
        df = pd.DataFrame(watchlist_data)
        # Display as a clean interactive table
        st.dataframe(
            df, 
            use_container_width=True,
            column_config={
                "last_checked": st.column_config.TextColumn("Last Scan"),
                "food_item": "Cuisine / Dish",
                "location": "Target Area"
            }
        )
    else:
        st.info("Your watchlist is empty. Add your first target in the sidebar! 👈")

# TAB 2: What have we found?
with tab2:
    st.subheader("Discovered Restaurants")
    restaurant_data = backend.get_all_restaurants()
    
    if restaurant_data:
        df_rest = pd.DataFrame(restaurant_data)
        st.dataframe(
            df_rest[["name", "neighborhood", "taste_rating", "notes"]], 
            use_container_width=True
        )
    else:
        st.info("No discoveries yet. The Sentinel hasn't run.")