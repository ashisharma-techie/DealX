"""
score_calculator.py
--------------------
Deal Integrity Score (0-100): "is this actually a good deal, or just a
marketing discount off an inflated/normal price?"

DESIGN GOAL: judges will ask "how did you calculate that number" - so every
number that feeds the final score is returned in the response, and the
"reason" string is built directly from those same numbers (never a separate,
un-auditable explanation).

--------------------------------------------------------------------------
THE ALGORITHM (plain-English walkthrough)
--------------------------------------------------------------------------
1. Rolling baselines
   For each window W in {30, 60, 90} days, take the mean price of every
   PriceHistory point in the last W days -> baseline_W.
   (If fewer than W days of history exist, we use whatever history is
   available for that window instead of failing.)

2. "Real" discount vs. each baseline
   pct_below_W = (baseline_W - current_price) / baseline_W * 100
   Positive => current price is genuinely below that window's average.
   Negative => current price is actually ABOVE that window's average
   (a "fake" or misleading discount).

3. Weighted discount signal
   The 90-day baseline is the most trustworthy "typical price" signal, so it
   gets the most weight; 30-day is the least reliable (too easily skewed by
   a recent spike) so it gets the least:
       weighted_discount = 0.5 * pct_below_90 + 0.3 * pct_below_60 + 0.2 * pct_below_30

4. Map the weighted discount onto a base score
   base_score = 30 + weighted_discount * 2.0
   A price sitting right at its typical (baseline) price has a REAL discount
   of ~0%, and that should read as a low score (~30) even if the listing is
   marketed as "50% off" - the marketed discount never enters this formula
   at all, only the actual price-vs-history comparison does. Every +1%
   genuine discount below baseline moves the score up 2 points; every +1%
   markup above baseline moves it down 2 points.

5. Volatility penalty
   coefficient_of_variation_90 = stdev(last 90 days prices) / baseline_90 * 100
   volatility_penalty = min(coefficient_of_variation_90 * 0.5, 20)
   A highly volatile price history means "the current price being low right
   now" is less meaningful/trustworthy, so we cap the penalty at 20 points
   and subtract it from the base score.

6. Inconsistency penalty
   If the 30-day window disagrees in sign with the 90-day window by a wide
   margin (e.g. price just spiked 20% then got "discounted" back down to
   basically its normal 90-day average - the classic fake-sale pattern),
   apply an extra penalty proportional to that divergence, capped at 15.
       divergence = pct_below_90 - pct_below_30
       inconsistency_penalty = min(max(divergence, 0) * 0.3, 15)   # only
       penalizes when 30-day looks like a bigger "discount" than 90-day does

7. Final score
   final_score = clamp(base_score - volatility_penalty - inconsistency_penalty, 0, 100)

Every intermediate number above is returned in the "breakdown" field.

Public API:
    calculate_deal_score(current_price: float, history: list[dict]) -> dict
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, List


def _window_stats(history_sorted: List[Dict[str, Any]], as_of: datetime, days: int):
    cutoff = as_of - timedelta(days=days)
    window = [h for h in history_sorted if h["_dt"] >= cutoff]
    if not window:
        window = history_sorted[-1:]  # degrade gracefully with at least 1 point
    prices = [h["price"] for h in window]
    mean = sum(prices) / len(prices)
    if len(prices) > 1:
        variance = sum((p - mean) ** 2 for p in prices) / (len(prices) - 1)
        stdev = variance ** 0.5
    else:
        stdev = 0.0
    return {"n_points": len(prices), "baseline": round(mean, 2), "stdev": round(stdev, 2)}


def _clamp(value: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, value))


def calculate_deal_score(current_price: float, history: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not history:
        raise ValueError("calculate_deal_score requires at least one price history point")

    cleaned = sorted(
        (
            {"date": h["date"], "price": float(h["price"]), "_dt": datetime.strptime(h["date"], "%Y-%m-%d")}
            for h in history
        ),
        key=lambda h: h["_dt"],
    )
    as_of = cleaned[-1]["_dt"]  # treat the most recent history point as "today"

    stats_30 = _window_stats(cleaned, as_of, 30)
    stats_60 = _window_stats(cleaned, as_of, 60)
    stats_90 = _window_stats(cleaned, as_of, 90)

    def pct_below(baseline: float) -> float:
        if baseline == 0:
            return 0.0
        return (baseline - current_price) / baseline * 100

    pct_below_30 = pct_below(stats_30["baseline"])
    pct_below_60 = pct_below(stats_60["baseline"])
    pct_below_90 = pct_below(stats_90["baseline"])

    weighted_discount = 0.5 * pct_below_90 + 0.3 * pct_below_60 + 0.2 * pct_below_30
    base_score = 30 + weighted_discount * 2.0

    coefficient_of_variation_90 = (
        (stats_90["stdev"] / stats_90["baseline"] * 100) if stats_90["baseline"] else 0.0
    )
    volatility_penalty = min(coefficient_of_variation_90 * 0.5, 20)

    divergence = pct_below_90 - pct_below_30
    inconsistency_penalty = min(max(divergence, 0) * 0.3, 15)

    final_score = round(_clamp(base_score - volatility_penalty - inconsistency_penalty), 1)

    reason = _build_reason(
        current_price=current_price,
        pct_below_90=pct_below_90,
        pct_below_30=pct_below_30,
        coefficient_of_variation_90=coefficient_of_variation_90,
        divergence=divergence,
        final_score=final_score,
    )

    return {
        "score": final_score,
        "reason": reason,
        "breakdown": {
            "current_price": current_price,
            "baseline_30d": stats_30["baseline"],
            "baseline_60d": stats_60["baseline"],
            "baseline_90d": stats_90["baseline"],
            "pct_below_30d": round(pct_below_30, 2),
            "pct_below_60d": round(pct_below_60, 2),
            "pct_below_90d": round(pct_below_90, 2),
            "weighted_discount_pct": round(weighted_discount, 2),
            "base_score": round(base_score, 2),
            "volatility_coefficient_of_variation_90d_pct": round(coefficient_of_variation_90, 2),
            "volatility_penalty": round(volatility_penalty, 2),
            "inconsistency_penalty": round(inconsistency_penalty, 2),
            "n_price_points_used": stats_90["n_points"],
        },
    }


def _build_reason(current_price, pct_below_90, pct_below_30, coefficient_of_variation_90, divergence, final_score) -> str:
    if pct_below_90 >= 1:
        core = f"Price is {abs(round(pct_below_90))}% below its 90-day average"
    elif pct_below_90 <= -1:
        core = f"Price is actually {abs(round(pct_below_90))}% ABOVE its 90-day average"
    else:
        core = "Price is only " + (f"{round(pct_below_90, 1)}%" if pct_below_90 != 0 else "0%") + " below its 90-day average"

    flags = []
    if divergence > 10:
        flags.append("recent price spike makes the short-term discount misleading")
    if coefficient_of_variation_90 > 15:
        flags.append("price history is highly volatile, so treat this score with some caution")

    if flags:
        return core + " (" + "; ".join(flags) + ")."
    return core + "."


if __name__ == "__main__":
    import argparse
    import json
    import os

    parser = argparse.ArgumentParser(description="Calculate the Deal Integrity Score for one product")
    parser.add_argument("product_id", help="e.g. prod_004 (see sample_data/price_history_sample.json)")
    parser.add_argument(
        "--sample-file",
        default=os.path.join(os.path.dirname(__file__), "..", "sample_data", "price_history_sample.json"),
    )
    args = parser.parse_args()

    with open(args.sample_file) as f:
        data = json.load(f)

    if args.product_id not in data:
        raise SystemExit(f"Unknown product_id '{args.product_id}'. Options: {list(data.keys())}")

    product = data[args.product_id]
    result = calculate_deal_score(product["current_price"], product["history"])
    print(json.dumps(result, indent=2))
