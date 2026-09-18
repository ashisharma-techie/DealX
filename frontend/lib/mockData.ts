import { DealSummary, ProductDetail } from "./types";

function daysAgoISO(n: number): string {
  const d = new Date();
  d.setDate(d.getDate() - n);
  return d.toISOString().slice(0, 10);
}

function daysAheadISO(n: number): string {
  const d = new Date();
  d.setDate(d.getDate() + n);
  return d.toISOString().slice(0, 10);
}

export const trendingDeals: DealSummary[] = [
  {
    id: "wireless-headphones-x2",
    title: "Aria X2 Wireless Headphones",
    imageEmoji: "🎧",
    accent: "lavender",
    retailer: "Amazon",
    currentPrice: 4499,
    originalPrice: 7999,
    currency: "₹",
  },
  {
    id: "standing-desk-oak",
    title: "Oakline Adjustable Standing Desk",
    imageEmoji: "🪑",
    accent: "sage",
    retailer: "Flipkart",
    currentPrice: 12999,
    originalPrice: 15499,
    currency: "₹",
  },
  {
    id: "espresso-machine-mini",
    title: "Brewline Mini Espresso Machine",
    imageEmoji: "☕",
    accent: "blush",
    retailer: "Amazon",
    currentPrice: 6299,
    originalPrice: 9999,
    currency: "₹",
  },
  {
    id: "running-shoes-cloud",
    title: "Cloudpace Running Shoes",
    imageEmoji: "👟",
    accent: "lavender",
    retailer: "eBay",
    currentPrice: 3199,
    originalPrice: 3299,
    currency: "₹",
  },
  {
    id: "mechanical-keyboard-75",
    title: "Keystone 75% Mechanical Keyboard",
    imageEmoji: "⌨️",
    accent: "sage",
    retailer: "Flipkart",
    currentPrice: 5499,
    originalPrice: 8999,
    currency: "₹",
  },
  {
    id: "air-purifier-breeze",
    title: "Breeze Compact Air Purifier",
    imageEmoji: "🌬️",
    accent: "blush",
    retailer: "Amazon",
    currentPrice: 7999,
    originalPrice: 8499,
    currency: "₹",
  },
];

// Deterministic-ish history so charts look intentional, not random noise.
function buildHistory(base: number, volatility: number) {
  const points = [];
  let price = base * 1.18;
  for (let i = 60; i >= 1; i--) {
    const wobble = Math.sin(i / 6) * volatility + (i % 9 === 0 ? -volatility * 1.5 : 0);
    price = Math.max(base * 0.85, price - (i === 60 ? 0 : wobble * 0.4) - (60 - i) * (volatility * 0.02));
    points.push({ date: daysAgoISO(i), price: Math.round(price) });
  }
  points.push({ date: daysAgoISO(0), price: base });
  return points;
}

function buildForecast(base: number, direction: "down" | "flat" | "up") {
  const points = [];
  const slope = direction === "down" ? -0.55 : direction === "up" ? 0.4 : 0.05;
  for (let i = 1; i <= 30; i++) {
    const price = Math.round(base + slope * i * 6 + Math.sin(i / 4) * 40);
    points.push({
      date: daysAheadISO(i),
      price,
      confidenceLow: Math.round(price - 8 * Math.sqrt(i)),
      confidenceHigh: Math.round(price + 8 * Math.sqrt(i)),
    });
  }
  return points;
}

const productExtras: Record<
  string,
  { description: string; integrityScore: number; forecastDirection: "down" | "flat" | "up"; volatility: number }
> = {
  "wireless-headphones-x2": {
    description:
      "Active noise cancelling over-ear headphones with 40-hour battery life and a fold-flat hinge for travel.",
    integrityScore: 82,
    forecastDirection: "down",
    volatility: 90,
  },
  "standing-desk-oak": {
    description: "Dual-motor standing desk with memory presets and a 1200×700mm oak-finish top.",
    integrityScore: 58,
    forecastDirection: "flat",
    volatility: 140,
  },
  "espresso-machine-mini": {
    description: "15-bar pump espresso machine with a compact footprint, built for one or two cups at a time.",
    integrityScore: 34,
    forecastDirection: "up",
    volatility: 110,
  },
  "running-shoes-cloud": {
    description: "Lightweight daily trainer with responsive foam and a breathable knit upper.",
    integrityScore: 71,
    forecastDirection: "flat",
    volatility: 60,
  },
  "mechanical-keyboard-75": {
    description: "Hot-swappable 75% mechanical keyboard with gasket mount and PBT keycaps.",
    integrityScore: 88,
    forecastDirection: "down",
    volatility: 130,
  },
  "air-purifier-breeze": {
    description: "HEPA air purifier rated for rooms up to 300 sq ft, with a whisper-quiet night mode.",
    integrityScore: 41,
    forecastDirection: "up",
    volatility: 70,
  },
};

export function getMockProductDetail(id: string): ProductDetail | undefined {
  const summary = trendingDeals.find((d) => d.id === id);
  const extra = productExtras[id];
  if (!summary || !extra) return undefined;

  const history = buildHistory(summary.currentPrice, extra.volatility / 20);
  const forecast = buildForecast(summary.currentPrice, extra.forecastDirection);

  const alternatives = (["Amazon", "Flipkart", "eBay"] as const)
    .filter((r) => r !== summary.retailer)
    .map((retailer, i) => ({
      id: `${id}-${retailer.toLowerCase()}`,
      retailer,
      price: Math.round(summary.currentPrice * (1 + (i === 0 ? 0.04 : -0.03))),
      currency: summary.currency,
      url: "#",
      inStock: true,
    }));

  return {
    ...summary,
    description: extra.description,
    integrityScore: extra.integrityScore,
    priceHistory: history,
    priceForecast: forecast,
    alternatives,
  };
}
