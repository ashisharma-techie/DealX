// Types mirror the shapes we expect from shared/api_schema.json.
// NOTE: this file was written without direct access to that schema —
// verify field names against the real file and adjust here (only here).

export type Retailer = "Amazon" | "Flipkart" | "eBay";

export interface PricePoint {
  date: string; // ISO date, e.g. "2026-08-01"
  price: number;
}

export interface ForecastPoint {
  date: string;
  price: number;
  confidenceLow: number;
  confidenceHigh: number;
}

export interface AlternativeListing {
  id: string;
  retailer: Retailer;
  price: number;
  currency: string;
  url: string;
  inStock: boolean;
}

export interface DealSummary {
  id: string;
  title: string;
  imageEmoji: string; // stand-in for a real product image
  accent: "lavender" | "sage" | "blush";
  retailer: Retailer;
  currentPrice: number;
  originalPrice: number;
  currency: string;
}

export interface ProductDetail extends DealSummary {
  description: string;
  integrityScore: number; // 0-100
  priceHistory: PricePoint[];
  priceForecast: ForecastPoint[];
  alternatives: AlternativeListing[];
}

export interface SubscribeRequest {
  productId: string;
  channel: "telegram" | "sms";
  contact: string;
  targetPrice?: number;
}

export interface SubscribeResponse {
  subscriptionId: string;
  status: "confirmed" | "pending";
}
