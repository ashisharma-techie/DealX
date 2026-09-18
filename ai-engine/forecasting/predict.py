"""
predict.py
----------
Loads (or trains on demand) a per-product forecasting model and returns a
30-day forecast shaped for GET /products/{id}/forecast.

Public API:
    predict_forecast(product_id: str, history: list[dict], days: int = 30,
                      retrain: bool = False) -> dict

Returned shape (matches the forecast endpoint):
{
    "product_id": "prod_001",
    "model_type": "prophet" | "linear_regression",
    "generated_at": "2026-09-18T00:00:00Z",
    "forecast": [
        {
            "date": "2026-09-19",
            "predicted_price": 312.45,
            "confidence_interval": {"lower": 298.10, "upper": 326.80}
        },
        ...
    ]
}

NOTE ON SCHEMA ALIGNMENT: backend/app/db/schema.sql and shared/api_schema.json
were not present in the repo at build time. This shape was inferred directly
from the endpoint name/description in the brief. Once those files land, diff
field names here (predicted_price / confidence_interval.lower / .upper) against
the real contract and adjust - the logic itself won't need to change.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List

import numpy as np

# Support running as a script (`python predict.py`) and as part of the package.
try:
    from .train_model import MODELS_DIR, load_model, save_model, train_forecast_model
except ImportError:  # pragma: no cover
    from train_model import MODELS_DIR, load_model, save_model, train_forecast_model

Z_80 = 1.2816  # z-score for an 80% confidence interval (matches Prophet's default interval_width=0.80)


def _forecast_with_prophet(model, last_date: datetime, days: int):
    from prophet import Prophet  # noqa: F401  (import kept local, optional dependency)
    import pandas as pd

    future_dates = [last_date + timedelta(days=i) for i in range(1, days + 1)]
    future_df = pd.DataFrame({"ds": future_dates})
    fcst = model.predict(future_df)

    results = []
    for _, row in fcst.iterrows():
        results.append(
            {
                "date": row["ds"].strftime("%Y-%m-%d"),
                "predicted_price": round(float(row["yhat"]), 2),
                "confidence_interval": {
                    "lower": round(float(row["yhat_lower"]), 2),
                    "upper": round(float(row["yhat_upper"]), 2),
                },
            }
        )
    return results


def _forecast_with_linear_regression(model, n_points: int, residual_std: float, last_date: datetime, days: int):
    future_x = np.arange(n_points, n_points + days).reshape(-1, 1)
    preds = model.predict(future_x)

    results = []
    for i, pred in enumerate(preds):
        d = last_date + timedelta(days=i + 1)
        lower = pred - Z_80 * residual_std
        upper = pred + Z_80 * residual_std
        results.append(
            {
                "date": d.strftime("%Y-%m-%d"),
                "predicted_price": round(max(float(pred), 0.0), 2),
                "confidence_interval": {
                    "lower": round(max(float(lower), 0.0), 2),
                    "upper": round(max(float(upper), 0.0), 2),
                },
            }
        )
    return results


def predict_forecast(
    product_id: str,
    history: List[Dict[str, Any]],
    days: int = 30,
    retrain: bool = False,
    models_dir: str = MODELS_DIR,
) -> Dict[str, Any]:
    trained = None if retrain else load_model(product_id, models_dir)

    if trained is None:
        trained = train_forecast_model(history)
        save_model(product_id, trained, models_dir)

    last_date = datetime.strptime(trained["last_date"], "%Y-%m-%d")

    if trained["model_type"] == "prophet":
        forecast = _forecast_with_prophet(trained["model"], last_date, days)
    else:
        forecast = _forecast_with_linear_regression(
            trained["model"], trained["n_points"], trained["residual_std"], last_date, days
        )

    return {
        "product_id": product_id,
        "model_type": trained["model_type"],
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "forecast": forecast,
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Predict 30-day price forecast for one product")
    parser.add_argument("product_id", help="e.g. prod_001 (see sample_data/price_history_sample.json)")
    parser.add_argument("--days", type=int, default=30)
    parser.add_argument("--retrain", action="store_true")
    parser.add_argument(
        "--sample-file",
        default=os.path.join(os.path.dirname(__file__), "..", "sample_data", "price_history_sample.json"),
    )
    args = parser.parse_args()

    with open(args.sample_file) as f:
        data = json.load(f)

    if args.product_id not in data:
        raise SystemExit(f"Unknown product_id '{args.product_id}'. Options: {list(data.keys())}")

    result = predict_forecast(args.product_id, data[args.product_id]["history"], days=args.days, retrain=args.retrain)
    print(json.dumps(result, indent=2))
