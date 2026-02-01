# Project 2: The AI Shoe Market Intelligence System 👟

## 1. Executive Summary
**Objective:** Build an autonomous system that identifies trending high-end running shoes, aggregates reviews to generate a quality score, and tracks prices for user-selected favorites.
**Core Pivot:** Moving from a simple "Price Tracker" to a "Discovery & Analysis Engine."
**Interface:** A fully AI-driven Telegram bot (LLM-based) that handles natural language queries (e.g., "What are the best super shoes right now?").

---

## 2. System Architecture (The "Pipeline")

The system operates in a linear pipeline: **Discovery → Analysis → Selection → Tracking**.

| Stage | Agent / Component | Role & Capabilities | Status |
| :--- | :--- | :--- | :--- |
| **1. Discovery** | `trend_hunter.py` | **The Cool Hunter.** Scans running blogs (RunRepeat, Runner's World), YouTube transcripts, and Reddit for new releases. | 🆕 **To Build** |
| **2. Analysis** | `review_analyst.py` | **The Critic.** Uses Gemini AI to read scraped reviews and calculate a **"Meta-Score"** (0-100) and summarize pros/cons. | 🆕 **To Build** |
| **3. Selection** | `bot.py` (AI Mode) | **The Concierge.** An LLM-driven interface. Reports trends to the user and asks which ones to add to the "Watch List." | 🔄 **Upgrade** |
| **4. Tracking** | `scout.py` | **The Worker.** Periodically checks prices *only* for the shoes in the Watch List. | ⚠️ **Refactor** |
| **Infrastructure** | `foodie_memory.db` | **Knowledge Base.** Stores Shoe Models, Review Data, and Price History. | 🔄 **Migrate** |

---

## 3. Data Schema (Expanded)

We need new tables to support "Shoe Concepts" separate from "Price Data."

### A. Market Knowledge (New)
* **`shoe_models`**:
    * `model_id`, `name` (e.g., "Nike Vaporfly 3")
    * `release_status` (Released/Upcoming)
    * `meta_score` (Integer 0-100)
    * `summary` (AI-generated text: "Great energy return, but narrow fit.")
    * `last_updated` (Timestamp)
* **`reviews`**:
    * `review_id`, `model_id` (FK)
    * `source` (e.g., "RunRepeat")
    * `url`, `sentiment_score`

### B. User Tracking (Refined)
* **`watch_list`**:
    * `user_id`, `model_id` (FK)
    * `target_price` (Optional)
    * `active` (Boolean)
* **`price_history`**: (Linked to `shoe_models` now, not just raw text)
    * `model_id` (FK), `price`, `store_url`, `timestamp`

---

## 4. The AI Interaction Model (No More Hardcoded Commands)

The Telegram Bot (`bot.py`) will transition from **Rule-Based** (Regex) to **Agent-Based** (LLM Tool Use).

### Example User Journey
1.  **User:** *"What's the latest on marathon super shoes?"*
2.  **Bot (AI):** Queries `shoe_models` table for recent releases with high `meta_score`.
3.  **Bot:** *"The Alphafly 3 is trending (Score: 94) and the Adios Pro 4 just leaked. Reviewers say the Alphafly is lighter this year."*
4.  **User:** *"Track the Alphafly for me."*
5.  **Bot (AI):** Calls tool `add_to_watchlist(user='Allen', shoe='Alphafly 3')`.
6.  **System:** `scout.py` begins daily price checks for Alphafly 3.

---

## 5. Implementation Roadmap

### Phase 1: The Knowledge Graph (Next Session)
* **Goal:** Database migration (Create `shoe_models` table) and building the `trend_hunter.py` agent.
* **Tech:** Tavily API (for searching "new running shoe releases 2026"), Gemini API (to parse the news into JSON).

### Phase 2: The Review Analyst
* **Goal:** Build `review_analyst.py`.
* **Tech:** Scrape review text -> Feed to Gemini -> Output Score (0-100).

### Phase 3: The AI Bot Brain
* **Goal:** Refactor `bot.py` to use **Function Calling** (Tools).
* **Tech:** Google GenAI SDK. The bot will have tools like `get_trending_shoes()`, `read_reviews()`, and `track_shoe()`.

### Phase 4: The Price Scout (Re-Integration)
* **Goal:** Update `scout.py` to search specifically for the *exact models* in the `watch_list`, rather than generic brand scraping.

---

## 6. Technical Risks
* **Data Freshness:** Trends move fast. We need a reliable source for "new releases" (potentially RSS feeds from sneaker blogs).
* **Shoe Matching:** "Nike Vaporfly 3" vs "Vaporfly Next% 3" vs "ZoomX Vaporfly 3". We will need the AI to normalize names so we don't create duplicates.