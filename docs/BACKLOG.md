# Technical Backlog & Known Issues 🔧

## 1. OpenClaw Re-Integration (Priority: Medium)
* **Current Status:** The OpenClaw v2026 beta is unstable. `npx clawhub` fails with "Only HTML requests" error, and manual config editing causes "Sanitizer" crashes.
* **Goal:** Once OpenClaw stabilizes, migrate our Python logic back into the `~/.openclaw/workspace/skills/` folder.
* **Verified Path:** The correct path for future skills is `~/.openclaw/workspace/skills/<skill_name>/`.
* **Blocker:** The `clawhub` registry server seems to be rejecting API calls from the CLI.

## 2. Foodie Sentinel Improvements
* **Column Cleanup:** The database schema uses `notes` for descriptions, but we previously queried for `cuisine` and `news_source` which do not exist. Future updates should formally migrate the schema if we want those fields.
* **Automation:** Currently, the sentinel script (`mcp_server.py`) needs to be run manually to find *new* news. We need to set up a `cron` job or background scheduler to run it every morning.

## 3. General Maintenance
* **Environment:** We are using a fresh `.venv` created on Jan 31.
* **Secrets:** Telegram Token is in `.env`.