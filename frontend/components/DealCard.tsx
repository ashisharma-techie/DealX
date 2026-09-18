import Link from "next/link";
import { DealSummary } from "@/lib/types";

const ACCENT_BG: Record<DealSummary["accent"], string> = {
  lavender: "bg-lavender/30",
  sage: "bg-sage/30",
  blush: "bg-blush/30",
};

export default function DealCard({ deal }: { deal: DealSummary }) {
  const drop = Math.round(((deal.originalPrice - deal.currentPrice) / deal.originalPrice) * 100);

  return (
    <Link
      href={`/product/${deal.id}`}
      className="focus-ring group block rounded-card bg-surface p-5 transition hover:-translate-y-0.5"
    >
      <div className={`flex h-32 items-center justify-center rounded-card text-4xl ${ACCENT_BG[deal.accent]}`}>
        <span aria-hidden>{deal.imageEmoji}</span>
      </div>
      <p className="mt-4 text-xs text-muted">{deal.retailer}</p>
      <h3 className="mt-1 font-display text-base font-semibold text-ink">{deal.title}</h3>
      <div className="mt-2 flex items-baseline gap-2">
        <span className="font-display text-lg font-semibold text-ink">
          {deal.currency}
          {deal.currentPrice.toLocaleString("en-IN")}
        </span>
        <span className="text-sm text-muted line-through">
          {deal.currency}
          {deal.originalPrice.toLocaleString("en-IN")}
        </span>
        {drop > 0 && (
          <span className="ml-auto rounded-full bg-sage/40 px-2 py-0.5 text-xs font-medium text-ink">
            −{drop}%
          </span>
        )}
      </div>
    </Link>
  );
}
