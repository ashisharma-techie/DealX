import { notFound } from "next/navigation";
import Link from "next/link";
import Header from "@/components/Header";
import PriceChart from "@/components/PriceChart";
import DealIntegrityGauge from "@/components/DealIntegrityGauge";
import AlternativeCard from "@/components/AlternativeCard";
import LiveDemoTrigger from "@/components/LiveDemoTrigger";
import NotifyButton from "@/components/NotifyButton";
import { getProductDetail } from "@/lib/api";

export default async function ProductPage({ params }: { params: { id: string } }) {
  const product = await getProductDetail(params.id);
  if (!product) notFound();

  const cheapestId = [...product.alternatives, { id: "self", price: product.currentPrice }].sort(
    (a, b) => a.price - b.price
  )[0].id;

  return (
    <main>
      <Header />

      <div className="mx-auto max-w-5xl px-6 pb-24">
        <Link href="/" className="focus-ring inline-block text-sm text-muted hover:text-ink">
          ← Back to trending deals
        </Link>

        <div className="mt-6 grid gap-8 md:grid-cols-[240px_1fr]">
          <div className="flex h-52 items-center justify-center rounded-card bg-lavender/25 text-6xl md:h-full">
            <span aria-hidden>{product.imageEmoji}</span>
          </div>

          <div>
            <p className="text-sm text-muted">{product.retailer}</p>
            <h1 className="mt-1 font-display text-2xl font-semibold text-ink sm:text-3xl">
              {product.title}
            </h1>
            <p className="mt-2 max-w-xl text-sm text-muted">{product.description}</p>

            <div className="mt-4 flex items-baseline gap-3">
              <span className="font-display text-3xl font-semibold text-ink">
                {product.currency}
                {product.currentPrice.toLocaleString("en-IN")}
              </span>
              <span className="text-base text-muted line-through">
                {product.currency}
                {product.originalPrice.toLocaleString("en-IN")}
              </span>
            </div>

            <div className="mt-6 flex flex-wrap items-center gap-4">
              <NotifyButton productId={product.id} />
              <LiveDemoTrigger deal={product} />
            </div>
          </div>
        </div>

        <div className="mt-14 grid gap-8 lg:grid-cols-[1fr_260px]">
          <section className="rounded-card bg-surface p-6">
            <h2 className="font-display text-lg font-semibold text-ink">Price history &amp; forecast</h2>
            <p className="mt-1 text-sm text-muted">
              Solid line is what it's actually sold for. Dashed line is where we expect it to go over the next 30 days.
            </p>
            <div className="mt-6">
              <PriceChart
                history={product.priceHistory}
                forecast={product.priceForecast}
                currency={product.currency}
              />
            </div>
          </section>

          <section className="flex flex-col items-center rounded-card bg-surface p-6">
            <h2 className="self-start font-display text-lg font-semibold text-ink">Deal Integrity Score</h2>
            <p className="mt-1 self-start text-sm text-muted">
              How genuine this discount is, versus the product's real baseline price.
            </p>
            <div className="mt-4">
              <DealIntegrityGauge score={product.integrityScore} />
            </div>
          </section>
        </div>

        <section className="mt-10">
          <h2 className="font-display text-lg font-semibold text-ink">Alternative listings</h2>
          <p className="mt-1 text-sm text-muted">The same product, matched across other marketplaces.</p>
          <div className="mt-5 grid gap-3 sm:grid-cols-2">
            <AlternativeCard
              listing={{
                id: "self",
                retailer: product.retailer,
                price: product.currentPrice,
                currency: product.currency,
                url: "#",
                inStock: true,
              }}
              cheapest={cheapestId === "self"}
            />
            {product.alternatives.map((alt) => (
              <AlternativeCard key={alt.id} listing={alt} cheapest={cheapestId === alt.id} />
            ))}
          </div>
        </section>
      </div>
    </main>
  );
}
