# Project 2: The Multi-Agent Shoe Tracker 👟

## 1. Objective
Build an intelligent, multi-agent system to track running shoe prices, find new retailers, and monitor deals. The system is designed to evolve from a standalone Python tool into a scalable ecosystem that integrates with OpenClaw and multiple chat platforms (Telegram, Discord, etc.).

---

## 2. Architecture: The Agent Swarm
The system consists of specialized agents managed by a central Orchestrator.

### The Agents
* **Agent A (The Navigator):**
    * **Role:** The Explorer. Uses Search APIs (Google/DuckDuckGo) to discover *new* online retailers or boutique shops.
    * **Task:** Validates if a found URL sells the target brands and adds it to the "Scout List."
* **Agent B (The Scout):**
    * **Role:** The Worker. Visits URLs (from the manual list + Navigator discoveries) to scrape raw data (Price, Size, Stock).
    * **Capability:** Supports distinct parsing logic for different site structures (Shopify vs. Custom).
* **Agent C (The Analyst):**
    * **Role:** The Brain. Compares scraped data against:
        1.  **Price History:** Detects fake sales vs. real drops.
        2.  **User Personas:** Matches deals to specific User IDs based on size, brand loyalty, and category (Road vs. Trail).
* **Agent D (The Reporter):**
    * **Role:** The Messenger. A platform-agnostic notification manager that routes alerts to the correct user on their preferred app.

---

## 3. Data Structures
We will expand the database (`foodie_memory.db` -> `agent_memory.db`) to support multi-tenancy:

* `users`: `user_id`, `platform` (Telegram/Discord), `chat_id`.
* `preferences`: `user_id`, `shoe_size` (e.g., 10.5), `category` (Road/Trail), `brands` (Nike, Hoka).
* `watched_urls`: Source URLs (tagged as 'Manual' or 'Auto-Discovered').
* `price_history`: Longitudinal data for trend analysis.

---

## 4. Implementation Stages

### Stage 1: The Python Foundation (Immediate)
* **Goal:** A working, standalone system controlled via the existing `bot.py`.
* **Tech Stack:** Python 3.12+, SQLite, Requests/Playwright.
* **Interface:** Telegram (Single Platform).
* **Deliverables:**
    1.  Database migration to support Users and Preferences.
    2.  The "Navigator" script to find new URLs.
    3.  The "Scout" script to scrape prices.
    4.  `bot.py` commands: `/subscribe road size:10` and `/check_deals`.

### Stage 2: Ecosystem Integration (Future)
* **Goal:** Decouple the logic so it can be used by OpenClaw and other apps.
* **OpenClaw Integration (MCP Bridge):**
    * Wrap Agents A, B, and C into a **Model Context Protocol (MCP) Server**.
    * This allows OpenClaw (and other AI clients) to "call" our tools natively (e.g., *“Hey OpenClaw, use the Shoe Scout to find me Vaporflys”*).
* **Omni-Channel Support:**
    * Refactor "The Reporter" to use an **Adapter Pattern**.
    * **Adapters:**
        * `TelegramAdapter`: (Existing) Rich text, commands.
        * `DiscordAdapter`: Webhooks for channel alerts.
        * `APIAdapter`: JSON output for external dashboards.

---

## 5. Technical Backlog & Risks
* **Anti-Bot Measures:** High-value shoe sites (Nike, StockX) have heavy bot protection. We may need to use `playwright` with stealth plugins or rotate User-Agents.
* **OpenClaw Stability:** Stage 2 depends on OpenClaw v2026 stabilizing its local skill registry.