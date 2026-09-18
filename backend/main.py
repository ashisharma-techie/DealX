from fastapi import FastAPI

app = FastAPI(title="DealX Backend")

@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/products/search")
def search_products(q: str):
    # For now this returns fake/mock data.
    # Later we'll replace this with real scraped data.
    return {
        "results": [
            {
                "id": "prod_001",
                "title": f"Sample product matching '{q}'",
                "image": "https://via.placeholder.com/200",
                "price": 24999,
                "currency": "INR",
                "retailer": "Amazon"
            }
        ]
    }
@app.get("/products/{product_id}")
def get_product(product_id: str):
    # Mock data for now — later this comes from the database
    return {
        "id": product_id,
        "title": "Sample Product",
        "image": "https://via.placeholder.com/200",
        "currentPrice": 24999,
        "currency": "INR",
        "retailer": "Amazon",
        "url": "https://amazon.in/sample-product",
        "specs": {
            "color": "Black",
            "storage": "128GB"
        }
    }
from datetime import date, timedelta
import random


@app.get("/products/{product_id}/forecast")
def get_forecast(product_id: str):
    today = date.today()

    # last 15 days of "history" - mock, slightly random for realism
    history = []
    base_price = 24999
    for i in range(15, 0, -1):
        d = today - timedelta(days=i)
        price = base_price + random.randint(-500, 500)
        history.append({"date": str(d), "price": price})

    # next 30 days "forecast" - trending slightly down
    forecast = []
    predicted = base_price
    for i in range(1, 31):
        d = today + timedelta(days=i)
        predicted -= random.randint(0, 50)
        forecast.append({
            "date": str(d),
            "predictedPrice": predicted,
            "confidenceLow": predicted - 300,
            "confidenceHigh": predicted + 300
        })

    return {"history": history, "forecast": forecast}


@app.get("/products/{product_id}/deal-score")
def get_deal_score(product_id: str):
    return {
        "score": 42,
        "label": "Mediocre Deal",
        "reason": "Price is only 3% below its 90-day average.",
        "baseline30d": 25400,
        "baseline60d": 25800,
        "baseline90d": 25750
    }
@app.get("/products/{product_id}/alternatives")
def get_alternatives(product_id: str):
    return {
        "alternatives": [
            {
                "retailer": "eBay",
                "url": "https://ebay.com/sample-listing",
                "price": 23499,
                "currency": "INR",
                "matchConfidence": 0.92,
                "condition": "refurbished"
            },
            {
                "retailer": "Flipkart",
                "url": "https://flipkart.com/sample-listing",
                "price": 24799,
                "currency": "INR",
                "matchConfidence": 0.97,
                "condition": "new"
            }
        ]
    }


@app.post("/alerts/subscribe")
def subscribe_alert(product_id: str, channel: str, contact: str, target_price: float = None):
    # Mock: pretend we saved this subscription
    return {
        "subscribed": True,
        "alertId": "alert_001"
    }
