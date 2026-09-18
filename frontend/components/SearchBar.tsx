"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { trendingDeals } from "@/lib/mockData";

export default function SearchBar() {
  const [value, setValue] = useState("");
  const router = useRouter();

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!value.trim()) return;
    // Hackathon behavior: match against known mock products by loose title match,
    // otherwise just land on the first trending deal so the demo never dead-ends.
    const match = trendingDeals.find((d) =>
      d.title.toLowerCase().includes(value.trim().toLowerCase())
    );
    router.push(`/product/${match?.id ?? trendingDeals[0].id}`);
  }

  return (
    <form onSubmit={handleSubmit} className="mx-auto w-full max-w-2xl">
      <div className="flex items-center gap-2 rounded-search bg-surface p-2 shadow-lifted">
        <span className="pl-3 text-lg" aria-hidden>
          🔎
        </span>
        <input
          type="text"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          placeholder="Paste a product name or link…"
          className="focus-ring w-full bg-transparent px-1 py-3 text-sm text-ink placeholder:text-muted sm:text-base"
        />
        <button
          type="submit"
          className="focus-ring shrink-0 rounded-search bg-lavender px-5 py-3 text-sm font-semibold text-ink transition hover:bg-lavender-deep sm:px-6"
        >
          Track it
        </button>
      </div>
      <div className="mt-3 flex flex-wrap justify-center gap-x-4 gap-y-1 text-xs text-muted">
        <span>Works with</span>
        <span className="text-ink/70">Amazon</span>
        <span className="text-ink/70">Flipkart</span>
        <span className="text-ink/70">eBay</span>
        <span className="text-ink/70">+ any product URL</span>
      </div>
    </form>
  );
}
