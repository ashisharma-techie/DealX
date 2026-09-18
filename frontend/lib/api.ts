// Typed fetch layer. When NEXT_PUBLIC_BACKEND_URL is unset, every function
// falls back to local mock data — flip the env var once the real backend
// is up and nothing else in the app needs to change.
//
// Endpoint paths below (/deals/trending, /products/:id, etc.) are assumed —
// line them up against the real shared/api_schema.json / docs/api_reference.md
// once you have them; that's the only edit this file should need.

import { DealSummary, ProductDetail, SubscribeRequest, SubscribeResponse } from "./types";
import { trendingDeals, getMockProductDetail } from "./mockData";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL;

async function fetchJSON<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BACKEND_URL}${path}`, {
    ...init,
    cache:"no-store",
    headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
  });
  if (!res.ok) {
    throw new Error(`DealX API error ${res.status} on ${path}`);
  }
  return res.json() as Promise<T>;
}

export async function getTrendingDeals(): Promise<DealSummary[]> {
  if (!BACKEND_URL) return trendingDeals;
  return fetchJSON<DealSummary[]>("/deals/trending");
}

export async function getProductDetail(id: string): Promise<ProductDetail | undefined> {
  if (!BACKEND_URL) return getMockProductDetail(id);
  return fetchJSON<ProductDetail>(`/products/${id}`);
}

export async function subscribeToAlerts(req: SubscribeRequest): Promise<SubscribeResponse> {
  if (!BACKEND_URL) {
    // Mocked confirmation for the demo — no real message is sent.
    await new Promise((r) => setTimeout(r, 600));
    return { subscriptionId: `mock-${req.productId}-${Date.now()}`, status: "confirmed" };
  }
  return fetchJSON<SubscribeResponse>("/alerts/subscribe", {
    method: "POST",
    body: JSON.stringify(req),
  });
}
