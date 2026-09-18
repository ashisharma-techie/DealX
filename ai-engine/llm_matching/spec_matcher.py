"""
spec_matcher.py
----------------
Given a source product and a list of candidate listings scraped from other
marketplaces, decide which candidates are true matches for the same physical
product - powering the data behind GET /products/{id}/alternatives.

Primary path: call an LLM (via llm_client.call_llm) with the prompt template
in prompts/match_prompt.txt, per candidate, and parse its JSON verdict.

Fallback path: if no LLM API key is configured (or a call fails / returns
unparsable JSON), fall back to a deterministic heuristic matcher based on
title string similarity + exact-field spec overlap. This keeps the demo
working end-to-end even with no keys set up, and keeps results deterministic
for testing.

Public API:
    match_products(source_product: dict, candidates: list[dict]) -> dict
        returns: {
            "product_id": <source id if present>,
            "matches": [
                {
                    "candidate_id": ...,
                    "marketplace": ...,
                    "price": ...,
                    "is_match": bool,
                    "confidence": float,
                    "spec_diff": {...},
                    "notes": "...",
                    "match_method": "llm" | "heuristic",
                },
                ...
            ]
        }
"""

from __future__ import annotations

import difflib
import json
import os
import re
from typing import Any, Dict, List

try:
    from .llm_client import LLMNotConfiguredError, call_llm
except ImportError:  # pragma: no cover
    from llm_client import LLMNotConfiguredError, call_llm

PROMPT_PATH = os.path.join(os.path.dirname(__file__), "prompts", "match_prompt.txt")

with open(PROMPT_PATH) as _f:
    _RAW_TEMPLATE = _f.read()

_SYSTEM_TEMPLATE = _RAW_TEMPLATE.split("USER:")[0].replace("SYSTEM:", "", 1).strip()
_USER_TEMPLATE = _RAW_TEMPLATE.split("USER:")[1].strip()


def _build_prompts(source_product: Dict[str, Any], candidate: Dict[str, Any]) -> tuple[str, str]:
    user_prompt = _USER_TEMPLATE.format(
        source_title=source_product.get("title", ""),
        source_specs_json=json.dumps(source_product.get("specs", {})),
        candidate_marketplace=candidate.get("marketplace", "unknown"),
        candidate_title=candidate.get("title", ""),
        candidate_specs_json=json.dumps(candidate.get("specs", {})),
    )
    return _SYSTEM_TEMPLATE, user_prompt


def _extract_json(text: str) -> Dict[str, Any]:
    """LLMs occasionally wrap JSON in markdown fences despite instructions - strip those."""
    cleaned = text.strip()
    cleaned = re.sub(r"^```(json)?", "", cleaned).strip()
    cleaned = re.sub(r"```$", "", cleaned).strip()
    return json.loads(cleaned)


def _llm_match_one(source_product: Dict[str, Any], candidate: Dict[str, Any]) -> Dict[str, Any]:
    system_prompt, user_prompt = _build_prompts(source_product, candidate)
    raw = call_llm(system_prompt, user_prompt, json_mode=True)
    parsed = _extract_json(raw)
    return {
        "is_match": bool(parsed.get("is_match", False)),
        "confidence": float(parsed.get("confidence", 0.0)),
        "spec_diff": parsed.get("spec_diff", {}),
        "notes": parsed.get("notes", ""),
        "match_method": "llm",
    }


def _heuristic_match_one(source_product: Dict[str, Any], candidate: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deterministic fallback used when no LLM key is configured (or the call
    fails). Combines:
      - fuzzy title similarity (difflib SequenceMatcher ratio)
      - exact-match ratio across shared spec fields (brand/model carry more
        weight; color/cosmetic fields are informational only)
    """
    source_title = (source_product.get("title") or "").lower()
    candidate_title = (candidate.get("title") or "").lower()
    title_similarity = difflib.SequenceMatcher(None, source_title, candidate_title).ratio()

    source_specs = source_product.get("specs", {}) or {}
    candidate_specs = candidate.get("specs", {}) or {}

    spec_diff: Dict[str, Any] = {}
    all_fields = set(source_specs.keys()) | set(candidate_specs.keys())
    critical_fields = {"brand", "model"}
    critical_matches = 0
    critical_total = 0
    other_matches = 0
    other_total = 0

    for field in all_fields:
        s_val = source_specs.get(field)
        c_val = candidate_specs.get(field)
        matches = (s_val is not None) and (c_val is not None) and (str(s_val).lower() == str(c_val).lower())
        spec_diff[field] = {"source": s_val, "candidate": c_val, "matches": matches}
        if field in critical_fields:
            critical_total += 1
            if matches:
                critical_matches += 1
        else:
            other_total += 1
            if matches:
                other_matches += 1

    critical_score = (critical_matches / critical_total) if critical_total else 0.5
    other_score = (other_matches / other_total) if other_total else 0.5

    # Weighted blend: brand/model agreement matters most, then title text
    # similarity, then the remaining spec fields.
    confidence = round(0.5 * critical_score + 0.3 * title_similarity + 0.2 * other_score, 2)

    # A model mismatch is disqualifying regardless of everything else.
    model_field_mismatch = (
        "model" in spec_diff and spec_diff["model"]["source"] and spec_diff["model"]["candidate"] and not spec_diff["model"]["matches"]
    )
    is_match = confidence >= 0.6 and not model_field_mismatch

    if model_field_mismatch:
        notes = f"Model mismatch ({spec_diff['model']['source']} vs {spec_diff['model']['candidate']}) - treated as a different product."
    elif is_match:
        notes = "Title and spec overlap strongly suggest the same product."
    else:
        notes = "Insufficient title/spec overlap to confirm a match."

    return {
        "is_match": is_match,
        "confidence": confidence,
        "spec_diff": spec_diff,
        "notes": notes,
        "match_method": "heuristic",
    }


def match_products(source_product: Dict[str, Any], candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
    results = []
    for candidate in candidates:
        try:
            verdict = _llm_match_one(source_product, candidate)
        except LLMNotConfiguredError:
            verdict = _heuristic_match_one(source_product, candidate)
        except Exception:
            # Any LLM/network/parsing failure -> don't blow up the whole
            # request, fall back for just this candidate.
            verdict = _heuristic_match_one(source_product, candidate)

        results.append(
            {
                "candidate_id": candidate.get("id"),
                "marketplace": candidate.get("marketplace"),
                "price": candidate.get("price"),
                **verdict,
            }
        )

    return {
        "product_id": source_product.get("id"),
        "matches": results,
    }


if __name__ == "__main__":
    sample_file = os.path.join(os.path.dirname(__file__), "..", "sample_data", "listings_sample.json")
    with open(sample_file) as f:
        data = json.load(f)

    result = match_products(data["source_product"], data["candidates"])
    print(json.dumps(result, indent=2))
