# DealX Architecture

DealX has three independently-built pieces that talk to each other over a single REST contract, so all three teammates can work in parallel without blocking each other.

```
┌─────────────┐        REST (JSON)         ┌─────────────┐
│  frontend   │ ─────────────────────────▶ │   backend   │
│  (Next.js)  │ ◀───────────────────────── │  (FastAPI)  │
└─────────────┘                            └──────┬──────┘
                                                    │
                                    direct import   │  or internal
                                    OR internal      │  HTTP call
                                    service call     ▼
                                            ┌─────────────┐
                                            │  ai-engine  │
                                            │ (forecast,  │
                                            │ deal score, │
                                            │ spec match) │
                                            └─────────────┘
                                                    │
                                                    ▼
                                            ┌─────────────┐
                                            │  postgres   │
                                            │ (price      │
                                            │  history)   │
                                            └─────────────┘
```

## Flow

1. **Frontend** sends a search query or product URL to the backend (`GET /products/search`).
2. **Backend** either returns a cached product or triggers a scrape (Playwright) to pull fresh data from Amazon/eBay/Flipkart, then stores price history in Postgres.
3. **Backend** calls into **ai-engine** (as a Python import or a lightweight internal HTTP call — the ai-engine team decides which and documents it in `ai-engine/README.md`) to get:
   - a 30-day price forecast
   - a Deal Integrity Score
   - cross-marketplace alternative listings via LLM spec matching
4. **Backend** serves all of this back to the **frontend** in the exact shapes defined in `shared/api_schema.json`.
5. When a user subscribes to alerts (`POST /alerts/subscribe`), the **backend** stores the subscription and, on a price drop, pushes an interactive message via Telegram or SMS (Twilio).

## Why this split

Keeping the contract in `shared/api_schema.json` means the frontend can build entirely against mock data matching that contract, the backend can build and test its endpoints independently, and the AI engine can be developed and validated on synthetic data — all in parallel, then wired together at the end.
