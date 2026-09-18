# DealX

An autonomous, predictive shopping agent. DealX forecasts upcoming price drops, calculates a **Deal Integrity Score** to expose fake sales, matches product specs across new and refurbished marketplaces, and sends interactive instant-messaging alerts — shifting price tracking from reactive to proactive.

## The problem

Consumers struggle to find genuine savings online due to fake discount inflation, siloed cross-platform pricing, and unpredictable sales cycles. Traditional price trackers just notify you *after* a price drops, leaving you to manually compare retailers, secondary markets, and historical data yourself.

## The solution

DealX uses machine learning and LLM agents to:
- **Forecast** prices up to 30 days ahead, so you know whether to buy now or wait
- **Score deal integrity** (0–100) by comparing the current price against 30/60/90-day baselines, exposing inflated "sales"
- **Match specs across marketplaces** (new and refurbished listings) using an LLM pipeline, so you always see the real cheapest genuine option
- **Alert instantly** over Telegram/SMS the moment a real price drop happens, with interactive one-tap actions

## Team

| Person | Area | Folder |
| --- | --- | --- |
| Person 1 | Frontend & UI/UX (Next.js, Tailwind, Recharts) | [`frontend/`](./frontend) |
| Person 2 | Backend Core, Scraping & Alerts (FastAPI, Playwright, Twilio/Telegram) | [`backend/`](./backend) |
| Person 3 | AI Intelligence, Predictive Models & NLP (Prophet/scikit-learn, LLM matching) | [`ai-engine/`](./ai-engine) |

Each folder is owned end-to-end by one person and is built against the shared API contract in [`shared/api_schema.json`](./shared/api_schema.json), so all three can work in parallel. See [`docs/architecture.md`](./docs/architecture.md) for how the pieces connect.

## Project layout

```
dealx/
├── frontend/      # Next.js dashboard — Person 1
├── backend/       # FastAPI + scraping + alerts — Person 2
├── ai-engine/     # Forecasting, Deal Integrity Score, LLM matching — Person 3
├── shared/        # api_schema.json — the contract everyone builds against
├── docs/          # architecture, API reference, demo script
├── docker-compose.yml
└── .env.example
```

## Running it locally

1. Copy the env file and fill in real keys:
   ```bash
   cp .env.example .env
   ```
2. Start everything with Docker Compose:
   ```bash
   docker-compose up --build
   ```
   - Frontend → http://localhost:3000
   - Backend → http://localhost:8000
   - Postgres → localhost:5432

3. Or run each service individually during development — see each folder's own README for local (non-Docker) setup instructions once it's scaffolded.

## Docs

- [`docs/architecture.md`](./docs/architecture.md) — how frontend, backend, and ai-engine talk to each other
- [`docs/api_reference.md`](./docs/api_reference.md) — human-readable API reference
- [`docs/demo_script.md`](./docs/demo_script.md) — 2-minute hackathon demo walkthrough
