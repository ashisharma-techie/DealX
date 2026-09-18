# backend

Owner: Person 2 (Backend Core, Data Ingestion & Alerts)

FastAPI service for DealX. This folder is currently empty and will be scaffolded by Person 2 using their dedicated prompt (see the team's DealX Claude Code Prompts doc).

Planned structure:
- `main.py` — FastAPI entrypoint
- `app/api/` — routes for products, deals, alerts (must match `shared/api_schema.json`)
- `app/scraping/` — Playwright scrapers (Amazon, eBay, Flipkart)
- `app/notifications/` — Telegram + Twilio alert delivery
- `app/db/` — SQLAlchemy models, schema, and session handling
- `tests/` — endpoint tests

Runs on **port 8000** (see root `docker-compose.yml`). Talks to the `postgres` service for storage.
