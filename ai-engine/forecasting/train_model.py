"""
train_model.py
---------------
Trains a 30-day price forecasting model for a single product.

Strategy:
  - If Prophet is installed AND we have enough history (>= MIN_DAYS_FOR_PROPHET
    data points), train a Prophet model (handles trend + weekly seasonality well).
  - Otherwise (Prophet missing, or short history e.g. a brand-new product with
    only a couple weeks of scraped prices), fall back to a simple scikit-learn
    linear regression on (day_index -> price), which degrades gracefully with
    very little data and never crashes the pipeline.

Public API (both standalone-callable and importable):
    train_forecast_model(history: list[dict]) -> dict
        history: [{"date": "YYYY-MM-DD", "price": float}, ...] sorted or not.
        returns: {
            "model_type": "prophet" | "linear_regression",
            "model": <fitted model object>,
            "residual_std": float,   # used by predict.py for confidence intervals
            "n_points": int,
            "last_date": "YYYY-MM-DD",
        }

    save_model(product_id: str, trained: dict, models_dir=MODELS_DIR) -> str
    load_model(product_id: str, models_dir=MODELS_DIR) -> dict | None
"""

from __future__ import annotations

import json
import os
import pickle
from datetime import datetime
from typing import Any, Dict, List, Optional

import numpy as np

MIN_DAYS_FOR_PROPHET = 30  # below this, Prophet tends to overfit / is overkill
MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")

try:
    from prophet import Prophet  # type: ignore

    PROPHET_AVAILABLE = True
except Exception:  # pragma: no cover - environment dependent
    PROPHET_AVAILABLE = False


def _parse_history(history: List[Dict[str, Any]]):
    cleaned = sorted(
        ({"date": h["date"], "price": float(h["price"])} for h in history),
        key=lambda h: h["date"],
    )
    dates = [datetime.strptime(h["date"], "%Y-%m-%d") for h in cleaned]
    prices = np.array([h["price"] for h in cleaned], dtype=float)
    return dates, prices, cleaned


def _train_prophet(dates, prices):
    import pandas as pd

    df = pd.DataFrame({"ds": dates, "y": prices})
    model = Prophet(
        daily_seasonality=False,
        weekly_seasonality=True,
        yearly_seasonality=False,
        interval_width=0.80,
    )
    model.fit(df)

    # residual std from in-sample fit, used later for a fallback CI if needed
    in_sample = model.predict(df[["ds"]])
    residuals = prices - in_sample["yhat"].values
    residual_std = float(np.std(residuals)) if len(residuals) else 0.0
    return model, residual_std


def _train_linear_regression(dates, prices):
    from sklearn.linear_model import LinearRegression

    x = np.arange(len(prices)).reshape(-1, 1)
    model = LinearRegression()
    model.fit(x, prices)

    preds = model.predict(x)
    residuals = prices - preds
    residual_std = float(np.std(residuals)) if len(residuals) else 0.0
    return model, residual_std


def train_forecast_model(history: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not history:
        raise ValueError("train_forecast_model requires at least one price point")

    dates, prices, cleaned = _parse_history(history)
    n_points = len(prices)

    use_prophet = PROPHET_AVAILABLE and n_points >= MIN_DAYS_FOR_PROPHET

    if use_prophet:
        try:
            model, residual_std = _train_prophet(dates, prices)
            model_type = "prophet"
        except Exception:
            # Any Prophet runtime failure (e.g. missing cmdstan backend on this
            # machine) should never break the pipeline -> fall back silently.
            model, residual_std = _train_linear_regression(dates, prices)
            model_type = "linear_regression"
    else:
        model, residual_std = _train_linear_regression(dates, prices)
        model_type = "linear_regression"

    return {
        "model_type": model_type,
        "model": model,
        "residual_std": residual_std,
        "n_points": n_points,
        "last_date": cleaned[-1]["date"],
    }


def save_model(product_id: str, trained: Dict[str, Any], models_dir: str = MODELS_DIR) -> str:
    os.makedirs(models_dir, exist_ok=True)
    path = os.path.join(models_dir, f"{product_id}.pkl")
    with open(path, "wb") as f:
        pickle.dump(trained, f)
    return path


def load_model(product_id: str, models_dir: str = MODELS_DIR) -> Optional[Dict[str, Any]]:
    path = os.path.join(models_dir, f"{product_id}.pkl")
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        return pickle.load(f)


if __name__ == "__main__":
    # Quick standalone smoke test using bundled sample data.
    import argparse

    parser = argparse.ArgumentParser(description="Train a forecasting model for one product")
    parser.add_argument("product_id", help="e.g. prod_001 (see sample_data/price_history_sample.json)")
    parser.add_argument(
        "--sample-file",
        default=os.path.join(os.path.dirname(__file__), "..", "sample_data", "price_history_sample.json"),
    )
    args = parser.parse_args()

    with open(args.sample_file) as f:
        data = json.load(f)

    if args.product_id not in data:
        raise SystemExit(f"Unknown product_id '{args.product_id}'. Options: {list(data.keys())}")

    trained = train_forecast_model(data[args.product_id]["history"])
    save_path = save_model(args.product_id, trained)
    print(f"Trained {trained['model_type']} model on {trained['n_points']} points -> saved to {save_path}")
