"""
service.py
----------
Optional tiny Flask microservice, if Person 2 (backend) would rather call
this over HTTP than import ai-engine's Python functions directly.

WHY FLASK, NOT FASTAPI: Flask is the simplest thing that works for a
hackathon weekend - one file, no extra async setup, and it's already battle
tested by the time you read this (see README.md "How this was built /
tested" section). If your team already prefers FastAPI, the same three
route functions below can be pasted almost as-is into a FastAPI app - the
only real difference is the decorator and how path params are typed.

Run it with:
    python ai-engine/service.py
It starts on http://localhost:8100 by default (override with PORT env var).

Routes (mirroring the shapes the backend needs to serve to the frontend):
    GET /products/<product_id>/forecast
    GET /products/<product_id>/deal-score
    GET /products/<product_id>/alternatives

By default, every route returns data already reshaped to match
backend/main.py's exact response format (via backend_adapter.py) - so
Person 2's backend (or anyone else) can call this service over plain HTTP
and get back something that's a drop-in match for what their mock currently
returns, with zero translation code needed on their end.

Add ?detailed=true to any route to instead get the fuller, un-adapted
shape (snake_case, includes the full transparent score breakdown) - useful
for your own testing/notebook work, or for showing judges the underlying
math.

IMPORTANT: this service reads from sample_data/ so it works standalone
before the real scraper/DB exists. Once real data is available, swap
`_load_price_history`/`_load_listings` for a real DB/API call - every
function this calls already takes plain Python dicts/lists, so nothing
else needs to change.
"""

from __future__ import annotations

import json
import os
import sys

from flask import Flask, jsonify, request

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "forecasting"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "deal_integrity"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "llm_matching"))

from predict import predict_forecast  # noqa: E402
from score_calculator import calculate_deal_score  # noqa: E402
from spec_matcher import match_products  # noqa: E402
from backend_adapter import (  # noqa: E402
    get_forecast_response,
    get_deal_score_response,
    get_alternatives_response,
)


def _wants_detailed() -> bool:
    return request.args.get("detailed", "").lower() in ("true", "1", "yes")

SAMPLE_DATA_DIR = os.path.join(os.path.dirname(__file__), "sample_data")

app = Flask(__name__)


def _load_price_history():
    with open(os.path.join(SAMPLE_DATA_DIR, "price_history_sample.json")) as f:
        return json.load(f)


def _load_listings():
    with open(os.path.join(SAMPLE_DATA_DIR, "listings_sample.json")) as f:
        return json.load(f)


@app.get("/products/<product_id>/forecast")
def forecast(product_id: str):
    data = _load_price_history()
    if product_id not in data:
        return jsonify({"error": f"unknown product_id '{product_id}'"}), 404
    history = data[product_id]["history"]

    if _wants_detailed():
        return jsonify(predict_forecast(product_id, history))
    return jsonify(get_forecast_response(product_id, history))


@app.get("/products/<product_id>/deal-score")
def deal_score(product_id: str):
    data = _load_price_history()
    if product_id not in data:
        return jsonify({"error": f"unknown product_id '{product_id}'"}), 404
    product = data[product_id]

    if _wants_detailed():
        result = calculate_deal_score(product["current_price"], product["history"])
        result["product_id"] = product_id
        return jsonify(result)
    return jsonify(get_deal_score_response(product["current_price"], product["history"]))


@app.get("/products/<product_id>/alternatives")
def alternatives(product_id: str):
    listings = _load_listings()
    source = listings["source_product"]
    if source.get("id") != product_id:
        return jsonify({"error": f"no candidate listings bundled for '{product_id}' in sample data"}), 404

    if _wants_detailed():
        return jsonify(match_products(source, listings["candidates"]))
    return jsonify(get_alternatives_response(source, listings["candidates"]))


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8100))
    app.run(host="0.0.0.0", port=port, debug=True)
