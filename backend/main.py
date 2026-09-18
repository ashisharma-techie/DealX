from fastapi import FastAPI
from pydantic import BaseModel
from datetime import date, timedelta
import random

app = FastAPI(title="DealX Backend")


# ---------- Health check ----------

@app.get("/health")
def health():
    return {"status": "ok"}


# ---------- Product search ----------

@app.get("/products/search")
def search_products(q: str):
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


# ---------- Trending deals (for the landing page) ----------

@app.get("/deals/trending")
def get_trending_deals():
    return [
        {
            "id": "prod_001",
            "title": "Sample Trending Product",
            "imageEmoji": "📱",
            "accent": "lavender",
            "retailer": "Amazon",
            "currentPrice": 24999,
            "originalPrice": 29999,
            "currency": "INR"
        },
        {
            "id": "prod_002",
            "title": "Another Trending Product",
            "imageEmoji": "🎧",
            "accent": "sage",
            "retailer": "Flipkart",
            "currentPrice": 15999,
            "originalPrice": 18999,
            "currency": "INR"
        }
    ]


# ---------- Product detail (bundles price history, forecast, alternatives) ----------

@app.get("/products/{product_id}")
def get_product(product_id: str):
    today = date.today()

    price_history = []
    base_price = 24999
    for i in range(15, 0, -1):
        d = today - timedelta(days=i)
        price = base_price + random.randint(-500, 500)
        price_history.append({"date": str(d), "price": price})

    price_forecast = []
    predicted = base_price
    for i in range(1, 31):
        d = today + timedelta(days=i)
        predicted -= random.randint(0, 50)
        price_forecast.append({
            "date": str(d),
            "price": predicted,
            "confidenceLow": predicted - 300,
            "confidenceHigh": predicted + 300
        })

    alternatives = [
        {
            "id": "alt_ebay_001",
            "retailer": "eBay",
            "price": 23499,
            "currency": "INR",
            "url": "https://ebay.com/sample-listing",
            "inStock": True
        },
        {
            "id": "alt_flipkart_001",
            "retailer": "Flipkart",
            "price": 24799,
            "currency": "INR",
            "url": "https://flipkart.com/sample-listing",
            "inStock": True
        }
    ]

    return {
        "id": product_id,
        "title": "Sample Product",
        "imageEmoji": "📱",
        "accent": "lavender",
        "retailer": "Amazon",
        "currentPrice": 24999,
        "originalPrice": 29999,
        "currency": "INR",
        "description": "A sample product description for demo purposes.",
        "integrityScore": 42,
        "priceHistory": price_history,
        "priceForecast": price_forecast,
        "alternatives": alternatives
    }


# ---------- Standalone forecast endpoint (kept for the original API contract) ----------

@app.get("/products/{product_id}/forecast")
def get_forecast(product_id: str):
    today = date.today()

    history = []
    base_price = 24999
    for i in range(15, 0, -1):
        d = today - timedelta(days=i)
        price = base_price + random.randint(-500, 500)
        history.append({"date": str(d), "price": price})

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


# ---------- Standalone Deal Integrity Score endpoint ----------

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


# ---------- Standalone alternatives endpoint ----------

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


# ---------- Alert subscription ----------

class AlertSubscribeRequest(BaseModel):
    productId: str
    channel: str
    contact: str
    targetPrice: float | None = None


@app.post("/alerts/subscribe")
def subscribe_alert(req: AlertSubscribeRequest):
    return {
        "subscriptionId": "sub_001",
        "status": "confirmed"
    }