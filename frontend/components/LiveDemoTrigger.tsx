"use client";

import { useState } from "react";
import { DealSummary } from "@/lib/types";

export default function LiveDemoTrigger({ deal }: { deal: DealSummary }) {
  const [toast, setToast] = useState(false);

  function fire() {
    setToast(true);
    window.setTimeout(() => setToast(false), 4500);
  }

  return (
    <>
      <button
        type="button"
        onClick={fire}
        className="focus-ring rounded-full border border-ink/15 bg-surface px-4 py-2 text-xs font-medium text-muted transition hover:border-ink/30 hover:text-ink"
      >
        Simulate a live price-drop alert (demo)
      </button>

      {toast && (
        <div
          role="status"
          className="animate-toast-in fixed left-1/2 top-6 z-50 w-[calc(100%-2rem)] max-w-sm -translate-x-1/2 rounded-card bg-surface p-4 shadow-lifted"
        >
          <div className="flex items-start gap-3">
            <span className="text-xl" aria-hidden>
              🔔
            </span>
            <div className="min-w-0">
              <p className="text-sm font-semibold text-ink">Price drop on {deal.title}</p>
              <p className="mt-0.5 text-xs text-muted">
                Now {deal.currency}
                {Math.round(deal.currentPrice * 0.92).toLocaleString("en-IN")} — down from{" "}
                {deal.currency}
                {deal.currentPrice.toLocaleString("en-IN")}. Sent via Telegram.
              </p>
            </div>
            <button
              type="button"
              onClick={() => setToast(false)}
              aria-label="Dismiss"
              className="focus-ring ml-auto text-muted hover:text-ink"
            >
              ✕
            </button>
          </div>
        </div>
      )}
    </>
  );
}
