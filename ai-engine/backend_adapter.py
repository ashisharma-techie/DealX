"""
backend_adapter.py
-------------------
This file exists for ONE reason: Person 2's backend (backend/main.py) uses
different field names (camelCase, flatter JSON shapes) than the internal
ai-engine functions do (snake_case, more detailed/nested - kept that way on
purpose so the Deal Integrity Score stays fully transparent for judges).

Rather than rewriting the tested core logic in forecasting/, deal_integrity/,
and llm_matching/, this file wraps each one and re-shapes its output to
match backend/main.py's exact response format - so Person 2 can replace
their fake/random mock logic with a single function call from here, with
zero extra glue code on their end.

Usage in backend/main.py, for example:

    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ai-engine"))
    from backend_adapter import get_forecast_response, get_deal_score_response, get_alternatives_response

    @app.get("/products/{product_id}/forecast")
    def get_forecast(product_id: str):
        history = get_price_history_from_db(product_id)  # however Person 2 stores it
        return get_forecast_response(product_id, history)

    @app.get("/products/{product_id}/deal-score")
    def get_deal_score(product_id: str):
        history = get_price_history_from_db(product_id)
        current_price = history[-1]["price"]
        return get_deal_score_response(current_price, history)

    @app.get("/products/{product_id}/alternatives")
    def get_alternatives(product_id: str):
        source_product = get_product_from_db(product_id)
        candidates = get_scraped_candidates(product_id)  # from the scrapers
        return get_alternatives_response(source_product, candidates)

IMPORTANT: this file assumes `history` is a list of {"date": "YYYY-MM-DD",
"price": float} dicts - the same shape used everywhere else in ai-engine
and matching backend/main.py's own mock data shape.
"""

from __future__ import annotations

import os
import sys
from typing import Any, Dict, List

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "forecasting"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "deal_integrity"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "llm_matching"))

from predict import predict_forecast  # noqa: E402
from score_calculator import calculate_deal_score  # noqa: E402
from spec_matcher import match_products  # noqa: E402


# ---------- Forecast: GET /products/{id}/forecast ----------

def get_forecast_response(product_id: str, history: List[Dict[str, Any]], days: int = 30) -> Dict[str, Any]:
    """
    Matches backend/main.py's get_forecast() shape exactly:
    {"history": [...], "forecast": [{"date", "predictedPrice", "confidenceLow", "confidenceHigh"}]}
    """
    result = predict_forecast(product_id, history, days=days)

    forecast_out = [
        {
            "date": f["date"],
            "predictedPrice": f["predicted_price"],
            "confidenceLow": f["confidence_interval"]["lower"],
            "confidenceHigh": f["confidence_interval"]["upper"],
        }
        for f in result["forecast"]
    ]

    return {"history": history, "forecast": forecast_out}


# ---------- Deal Integrity Score: GET /products/{id}/deal-score ----------

def _score_to_label(score: float) -> str:
    """
    Turns the 0-100 score into the human-readable label backend/main.py
    expects (its mock currently hardcodes "Mediocre Deal" - this makes it
    dynamic based on the real score).
    """
    if score >= 80:
        return "Great Deal"
    if score >= 60:
        return "Good Deal"
    if score >= 40:
        return "Mediocre Deal"
    if score >= 20:
        return "Poor Deal"
    return "Bad Deal"


def get_deal_score_response(current_price: float, history: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Matches backend/main.py's get_deal_score() shape exactly:
    {"score", "label", "reason", "baseline30d", "baseline60d", "baseline90d"}
    """
    result = calculate_deal_score(current_price, history)
    breakdown = result["breakdown"]

    return {
        "score": result["score"],
        "label": _score_to_label(result["score"]),
        "reason": result["reason"],
        "baseline30d": breakdown["baseline_30d"],
        "baseline60d": breakdown["baseline_60d"],
        "baseline90d": breakdown["baseline_90d"],
    }


# ---------- Alternatives: GET /products/{id}/alternatives ----------

def get_alternatives_response(source_product: Dict[str, Any], candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Matches backend/main.py's get_alternatives() shape exactly:
    {"alternatives": [{"retailer", "url", "price", "currency", "matchConfidence", "condition"}]}

    Only candidates the matcher actually confirms as the same product are
    included - a non-match never gets shown to the user as an "alternative."
    """
    result = match_products(source_product, candidates)
    candidates_by_id = {c.get("id"): c for c in candidates}

    alternatives = []
    for m in result["matches"]:
        if not m["is_match"]:
            continue
        candidate = candidates_by_id.get(m["candidate_id"], {})
        alternatives.append(
            {
                "retailer": m.get("marketplace") or candidate.get("retailer", ""),
                "url": candidate.get("url", ""),
                "price": m.get("price"),
                "currency": candidate.get("currency", "INR"),
                "matchConfidence": m.get("confidence"),
                "condition": candidate.get("condition", "used"),
            }
        )

    return {"alternatives": alternatives}


if __name__ == "__main__":
    # Quick standalone check that each adapter function produces backend-shaped output.
    import json

    sample_dir = os.path.join(os.path.dirname(__file__), "sample_data")

    with open(os.path.join(sample_dir, "price_history_sample.json")) as f:
        products = json.load(f)

    product = products["prod_001"]
    print("--- forecast ---")
    print(json.dumps(get_forecast_response("prod_001", product["history"], days=5), indent=2)[:600])

    print("\n--- deal score ---")
    print(json.dumps(get_deal_score_response(product["current_price"], product["history"]), indent=2))

    with open(os.path.join(sample_dir, "listings_sample.json")) as f:
        listings = json.load(f)

    print("\n--- alternatives ---")
    print(json.dumps(get_alternatives_response(listings["source_product"], listings["candidates"]), indent=2))
