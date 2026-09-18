import { AlternativeListing } from "@/lib/types";

export default function AlternativeCard({
  listing,
  cheapest,
}: {
  listing: AlternativeListing;
  cheapest: boolean;
}) {
  return (
    <a
      href={listing.url}
      className="focus-ring flex items-center justify-between rounded-card border border-ink/10 bg-surface p-4 transition hover:border-ink/20"
    >
      <div>
        <p className="text-sm font-medium text-ink">{listing.retailer}</p>
        <p className="text-xs text-muted">{listing.inStock ? "In stock" : "Out of stock"}</p>
      </div>
      <div className="text-right">
        <p className="font-display text-base font-semibold text-ink">
          {listing.currency}
          {listing.price.toLocaleString("en-IN")}
        </p>
        {cheapest && (
          <span className="mt-1 inline-block rounded-full bg-sage/40 px-2 py-0.5 text-[11px] font-medium text-ink">
            Best price
          </span>
        )}
      </div>
    </a>
  );
}
