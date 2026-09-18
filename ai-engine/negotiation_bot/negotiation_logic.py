"""
negotiation_logic.py
---------------------
Given a P2P/marketplace listing and the Deal Integrity Score data for that
product, draft a polite negotiation message proposing a lower price, backed
by the actual pricing data (not just "please lower the price").

Deterministic by default (a template, not an LLM call) so it's reliable for
a live demo. An optional use_llm=True path rewrites the deterministic draft
in a more natural voice via llm_client, with the deterministic version as a
guaranteed fallback if that call fails or no key is configured.

Public API:
    draft_negotiation_message(listing: dict, deal_score_data: dict, use_llm: bool = False) -> dict
        returns: {
            "listing_id": ...,
            "proposed_price": float,
            "message": "...",
            "basis": {...}   # the numbers the message is based on, for transparency
        }
"""

from __future__ import annotations

from typing import Any, Dict


def _compute_proposed_price(asking_price: float, breakdown: Dict[str, Any]) -> float:
    """
    Anchor the counter-offer to the 90-day baseline (the most trustworthy
    "typical price" signal - see deal_integrity/score_calculator.py), with a
    small additional cushion so the opener isn't the seller's own baseline
    (which most sellers would reject outright).
    """
    baseline_90 = breakdown.get("baseline_90d")
    if not baseline_90:
        # No baseline available -> fall back to a flat 10% off the ask.
        return round(asking_price * 0.90, 2)

    baseline_anchor = baseline_90 * 0.97  # 3% under the "typical" price
    if baseline_anchor < asking_price:
        anchor = baseline_anchor
    else:
        # Asking price is already at/below the typical price - there's no
        # baseline-driven leverage, so just nudge a modest 5% off the ask.
        anchor = asking_price * 0.95

    # Never propose a laughably low offer - floor it at 15% off asking.
    floor = asking_price * 0.85
    proposed = max(anchor, floor)
    return round(proposed, 2)


def _pct_above_baseline(asking_price: float, baseline_90: float) -> float:
    if not baseline_90:
        return 0.0
    return round((asking_price - baseline_90) / baseline_90 * 100, 1)


def _draft_deterministic(listing: Dict[str, Any], deal_score_data: Dict[str, Any], proposed_price: float) -> str:
    breakdown = deal_score_data.get("breakdown", {})
    asking_price = listing.get("asking_price")
    baseline_90 = breakdown.get("baseline_90d")
    title = listing.get("title", "this item")
    seller_name = listing.get("seller_name")

    greeting = f"Hi {seller_name}," if seller_name else "Hi,"

    pct_above = _pct_above_baseline(asking_price, baseline_90) if (asking_price and baseline_90) else None

    if pct_above is not None and pct_above > 2:
        data_line = (
            f"I've been tracking this item's price and it's currently listed about {pct_above}% above "
            f"its typical price over the last 90 days (around ${baseline_90:.2f})."
        )
    elif pct_above is not None and pct_above < -2:
        data_line = (
            f"I've been tracking this item's price and your asking price is already below its typical "
            f"90-day price (around ${baseline_90:.2f}), which is a solid deal - just wanted to check if "
            f"there's a little more flexibility."
        )
    elif pct_above is not None:
        data_line = (
            f"I've been tracking this item's price and your asking price is already close to its "
            f"typical 90-day price (around ${baseline_90:.2f})."
        )
    else:
        data_line = "I've been keeping an eye on prices for this item across a few sources."

    return (
        f"{greeting} I'm interested in the {title}. {data_line} "
        f"Would you consider ${proposed_price:.2f}? Happy to arrange pickup/payment quickly if that works for you. Thanks!"
    )


def draft_negotiation_message(
    listing: Dict[str, Any], deal_score_data: Dict[str, Any], use_llm: bool = False
) -> Dict[str, Any]:
    asking_price = listing.get("asking_price")
    if asking_price is None:
        raise ValueError("listing must include 'asking_price'")

    breakdown = deal_score_data.get("breakdown", {})
    proposed_price = _compute_proposed_price(asking_price, breakdown)
    message = _draft_deterministic(listing, deal_score_data, proposed_price)

    if use_llm:
        try:
            try:
                from .llm_client import LLMNotConfiguredError, call_llm
            except ImportError:  # pragma: no cover
                from llm_client import LLMNotConfiguredError, call_llm

            system_prompt = (
                "Rewrite the following negotiation message to sound natural, friendly, and concise. "
                "Keep every number exactly as given. Do not invent new facts. Return only the rewritten "
                "message, no preamble."
            )
            rewritten = call_llm(system_prompt, message)
            if rewritten and rewritten.strip():
                message = rewritten.strip()
        except Exception:
            pass  # keep the deterministic draft - never fail the request over this

    return {
        "listing_id": listing.get("id"),
        "proposed_price": proposed_price,
        "message": message,
        "basis": {
            "asking_price": asking_price,
            "baseline_90d": breakdown.get("baseline_90d"),
            "pct_asking_above_baseline_90d": _pct_above_baseline(asking_price, breakdown.get("baseline_90d"))
            if breakdown.get("baseline_90d")
            else None,
            "deal_integrity_score": deal_score_data.get("score"),
            "deal_integrity_reason": deal_score_data.get("reason"),
        },
    }


if __name__ == "__main__":
    import argparse
    import json
    import os
    import sys

    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "deal_integrity"))
    from score_calculator import calculate_deal_score  # noqa: E402

    parser = argparse.ArgumentParser(description="Draft a negotiation message for a P2P listing")
    parser.add_argument("--use-llm", action="store_true")
    parser.add_argument(
        "--listing-file",
        default=os.path.join(os.path.dirname(__file__), "..", "sample_data", "negotiation_listing_sample.json"),
    )
    parser.add_argument(
        "--history-file",
        default=os.path.join(os.path.dirname(__file__), "..", "sample_data", "price_history_sample.json"),
    )
    args = parser.parse_args()

    with open(args.listing_file) as f:
        listing = json.load(f)["listing"]
    with open(args.history_file) as f:
        products = json.load(f)

    product = products[listing["product_id"]]
    deal_score_data = calculate_deal_score(product["current_price"], product["history"])

    result = draft_negotiation_message(listing, deal_score_data, use_llm=args.use_llm)
    print(json.dumps(result, indent=2))
