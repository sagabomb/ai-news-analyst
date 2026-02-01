# Project 2: The Multi-Agent Shoe Tracker 👟

## 1. Executive Summary
**Objective:** Build an autonomous, multi-agent system to track running shoe prices, discover new Canadian retailers, and monitor for specific deals (e.g., "Nike Vaporfly size 10").
**Current State:** Stage 1 (Foundation) completed. The system can discover stores, scrape basic prices, and report via Telegram.
**Primary User:** Allen (Markham, Ontario).

---

## 2. System Architecture (The "Swarm")

The system operates as a hub-and-spoke model where `bot.py` is the interface and specialized scripts act as autonomous agents.

| Agent / Component | File | Role & Capabilities | Status |
| :--- | :--- | :--- | :--- |
| **The Brain** | `foodie_memory.db` | **Central Knowledge Base.** Stores users, preferences, discovered URLs, and price history. | ✅ **Active** |
| **The Navigator** | `navigator.py` | **Discovery Agent.** Uses Tavily API to find *new* online shoe stores in Canada. Filters for duplicates before saving to DB. | ✅ **Active** |
| **The Scout** | `scout.py` | **Acquisition Agent.** Visits active URLs. Uses `requests` + `BeautifulSoup`. Features regex-based price extraction (`$99.99`) and brand keyword matching. | ⚠️ **v1.1 (Basic)** |
| **The Orchestrator** | `bot.py` | **Interface.** Telegram Bot that routes natural language queries ("Find shoes", "Find food") to the correct database backend. | ✅ **Active** |

---

## 3. Data Schema (SQLite)

The database (`foodie_memory.db`) contains the following schema extensions for Project 2:

### A. Identity & Preferences
* **`users`**: `user_id`, `telegram_id` (Auth), `username`.
* **`preferences`**: 
    * `user_id` (FK)
    * `shoe_size` (float, e.g., 10.0)
    * `category` (text, e.g., 'road', 'trail')
    * `brands` (text, comma-separated, e.g., "nike,hoka,saucony")

### B. Intelligence
* **`watched_urls`**: 
    * `url` (Unique), `site_name`
    * `source` (Enum: 'manual', 'navigator_agent')
    * `status` (Default: 'active')
* **`price_history`**:
    * `shoe_name` (Text derived from page title/context)
    * `price` (Real, extracted via Regex)
    * `url`, `currency` ('CAD'), `found_at` (Timestamp)

---

## 4. Current Workflows (Stage 1)

### Discovery Workflow
1.  Run `./.venv/bin/python navigator.py`.
2.  Agent queries Tavily for "Canadian running shoe stores".
3.  Agent filters Amazon/Pinterest results.
4.  Valid URLs are inserted into `watched_urls`.

### Scouting Workflow
1.  Run `./.venv/bin/python scout.py`.
2.  Agent pulls all `active` URLs.
3.  Agent downloads HTML (User-Agent masquerading applied).
4.  Agent checks for user-preferred brands (e.g., "Nike").
5.  Agent attempts to regex-match price.
6.  If Price > 0 OR "Sale" keywords found -> Log to `price_history`.

### User Query Workflow
1.  User types "Find shoes" in Telegram.
2.  `bot.py` detects intent -> Queries `price_history` (Limit 5, sorted by recency).
3.  Returns formatted HTML list with direct links.

---

## 5. Implementation Roadmap

### ✅ Stage 1: The Foundation (COMPLETED)
* [x] Database schema migration.
* [x] Navigator Agent (Tavily integration).
* [x] Scout Agent v1 (Basic Scraper).
* [x] Telegram Integration (Multi-intent routing).

### 🚧 Stage 2: Intelligence & Stealth (NEXT SPRINT)
* **Objective:** Reliability and Smart Filtering.
* **Key Tasks:**
    1.  **Stealth Upgrade:** Replace `requests` with `playwright` or `selenium` in `scout.py` to handle JavaScript-heavy sites and bypass basic bot protection.
    2.  **Price Logic:** Implement comparison logic (Current Price vs. 30-day Average).
    3.  **User Binding:** Update Scout to strictly filter by `preferences` (currently it checks brands, but not sizes).
    4.  **Cron Automation:** Create a schedule to run Navigator weekly and Scout daily.

### 🔮 Stage 3: Ecosystem Expansion (FUTURE)
* **Objective:** Decoupled accessibility.
* **Key Tasks:**
    1.  **MCP Server:** Wrap agents into a Model Context Protocol server for OpenClaw.
    2.  **Omni-Channel:** Add Discord Webhook support for deal alerts.
    3.  **Chat Configuration:** Allow users to update preferences via Telegram commands (e.g., `/size 10.5`).

---

## 6. Technical Debt & Known Issues
* **Price Extraction:** Current regex approach (`$\d+`) is naive; it may capture accessory prices or shipping costs instead of the main shoe price.
* **Scraping Blocks:** High-security sites (StockX, Nike.com) may block the current `requests`-based scraper (403 Forbidden).
* **Hardcoded Fallbacks:** `scout.py` currently falls back to hardcoded brands if the DB query fails.