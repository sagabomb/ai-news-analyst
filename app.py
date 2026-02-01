import streamlit as st
import pandas as pd
import sqlite3
import backend  # Import your actual backend logic

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Foodie Sentinel V2", 
    page_icon="🕵️‍♂️", 
    layout="wide"
)

st.title("🕵️‍♂️ Foodie Sentinel Command Center")
st.caption(f"Connected to Memory Bank: `{backend.DB_NAME}`")

# --- TABS FOR ORGANIZATION ---
tab1, tab2 = st.tabs(["🍽️ The Black Book (Results)", "⚙️ Mission Config (Watchlist)"])

# --- TAB 1: THE RESULTS ---
with tab1:
    st.header("Recent Intelligence")
    
    # 1. Load Data
    try:
        conn = sqlite3.connect(backend.DB_NAME)
        # We query specifically for the columns we created
        query = """
            SELECT 
                name as 'Restaurant', 
                neighborhood as 'Location', 
                taste_rating as 'Rating', 
                confidence_score as 'AI Confidence',
                notes as 'Intel',
                created_at as 'Found'
            FROM restaurants 
            ORDER BY created_at DESC
        """
        df = pd.read_sql_query(query, conn)
        conn.close()

        # 2. Metrics Row
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Spots Tracked", len(df))
            
            avg_rating = df['Rating'].mean()
            c2.metric("Average Rating", f"{avg_rating:.1f} / 10")
            
            high_conf = len(df[df['AI Confidence'] >= 8])
            c3.metric("High Confidence Leads", high_conf)
        else:
            st.info("Database is empty. Run 'sentinel.py' to gather intelligence.")

        # 3. Interactive Data Table
        st.dataframe(
            df, 
            use_container_width=True,
            hide_index=True,
            column_config={
                "Rating": st.column_config.NumberColumn(format="%d ⭐"),
                "AI Confidence": st.column_config.ProgressColumn(min_value=0, max_value=10, format="%d/10"),
                "Found": st.column_config.DatetimeColumn(format="D MMM YYYY, h:mm a")
            }
        )
        
    except Exception as e:
        st.error(f"Could not load database. Has sentinel.py run yet? \nError: {e}")

# --- TAB 2: THE CONFIG ---
with tab2:
    st.header("Active Surveillance Targets")
    st.markdown("The Sentinel is currently hunting for these targets:")
    
    # Get watchlist from the backend function we fixed earlier
    watchlist = backend.get_watchlist()
    
    # Convert to DataFrame for nice display
    st.table(pd.DataFrame(watchlist))
    
    st.caption("To edit these targets, modify the `get_watchlist()` function in `backend.py`.")