import Header from "@/components/Header";
import SearchBar from "@/components/SearchBar";
import DealCard from "@/components/DealCard";
import CategoryTile from "@/components/CategoryTile";
import { getTrendingDeals } from "@/lib/api";

const TRUST_STATS = [
  { icon: "📈", value: "3.2M+", label: "prices tracked daily" },
  { icon: "⏱️", value: "< 2 min", label: "to set up an alert" },
  { icon: "✅", value: "94%", label: "forecast accuracy at 7 days" },
];

const CATEGORIES: { emoji: string; label: string; accent: "lavender" | "sage" | "blush" }[] = [
  { emoji: "📦", label: "Track Amazon", accent: "lavender" },
  { emoji: "🛒", label: "Track Flipkart", accent: "sage" },
  { emoji: "🔍", label: "Deal Integrity Check", accent: "blush" },
  { emoji: "🔔", label: "Price Alerts", accent: "lavender" },
];

export default async function HomePage() {
  const deals = await getTrendingDeals();

  return (
    <main>
      <Header />

      <section className="mx-auto max-w-3xl px-6 pb-16 pt-10 text-center sm:pt-16">
        <p className="text-sm text-muted">A predictive shopping agent</p>
        <h1 className="mt-3 font-display text-4xl font-semibold leading-tight text-ink sm:text-5xl">
          Stop guessing.
          <br />
          Know when prices will actually drop.
        </h1>
        <p className="mx-auto mt-4 max-w-xl text-base text-muted">
          Paste any product and DealX forecasts where the price is headed, flags
          fake &ldquo;sales,&rdquo; and tells you the moment it&apos;s genuinely worth buying.
        </p>

        <div className="mt-8">
          <SearchBar />
        </div>

        <div className="mx-auto mt-12 grid max-w-xl grid-cols-3 gap-4">
          {TRUST_STATS.map((s) => (
            <div key={s.label} className="flex flex-col items-center gap-1">
              <span className="text-xl" aria-hidden>
                {s.icon}
              </span>
              <span className="font-display text-lg font-semibold text-ink">{s.value}</span>
              <span className="text-xs text-muted">{s.label}</span>
            </div>
          ))}
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-6 pb-20">
        <div className="grid gap-10 md:grid-cols-[minmax(0,220px)_1fr] md:items-start">
          <div>
            <h2 className="font-display text-2xl font-semibold text-ink">
              Compare everything, before you buy anything
            </h2>
            <p className="mt-3 text-sm text-muted">
              One search checks every marketplace, scores the discount, and
              tells you whether to buy now or wait.
            </p>
          </div>
          <div className="flex flex-wrap gap-4">
            {CATEGORIES.map((c) => (
              <CategoryTile key={c.label} {...c} />
            ))}
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-6 pb-24">
        <h2 className="font-display text-2xl font-semibold text-ink">Trending deals</h2>
        <p className="mt-2 text-sm text-muted">Picked from products with real, verified price drops right now.</p>
        <div className="mt-8 grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {deals.map((deal) => (
            <DealCard key={deal.id} deal={deal} />
          ))}
        </div>
      </section>
    </main>
  );
}
