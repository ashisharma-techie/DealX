"use client";

import { useState } from "react";
import { subscribeToAlerts } from "@/lib/api";

type Status = "idle" | "open" | "sending" | "done";

export default function NotifyButton({ productId }: { productId: string }) {
  const [status, setStatus] = useState<Status>("idle");
  const [channel, setChannel] = useState<"telegram" | "sms">("telegram");
  const [contact, setContact] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!contact.trim()) return;
    setStatus("sending");
    await subscribeToAlerts({ productId, channel, contact });
    setStatus("done");
  }

  if (status === "idle") {
    return (
      <button
        type="button"
        onClick={() => setStatus("open")}
        className="focus-ring rounded-full bg-blush px-6 py-3 text-sm font-semibold text-ink transition hover:bg-blush-deep"
      >
        Notify me on a price drop
      </button>
    );
  }

  if (status === "done") {
    return (
      <p className="rounded-full bg-sage/30 px-5 py-3 text-sm font-medium text-ink">
        You're set — we'll message you on {channel === "telegram" ? "Telegram" : "SMS"}.
      </p>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-3 rounded-card bg-surface p-4 sm:flex-row sm:items-center">
      <div className="flex rounded-full bg-base p-1 text-xs">
        {(["telegram", "sms"] as const).map((c) => (
          <button
            key={c}
            type="button"
            onClick={() => setChannel(c)}
            className={`focus-ring rounded-full px-3 py-1.5 font-medium transition ${
              channel === c ? "bg-lavender text-ink" : "text-muted"
            }`}
          >
            {c === "telegram" ? "Telegram" : "SMS"}
          </button>
        ))}
      </div>
      <input
        type="text"
        required
        value={contact}
        onChange={(e) => setContact(e.target.value)}
        placeholder={channel === "telegram" ? "@username" : "Phone number"}
        className="focus-ring flex-1 rounded-full border border-ink/10 bg-white px-4 py-2 text-sm text-ink placeholder:text-muted"
      />
      <button
        type="submit"
        disabled={status === "sending"}
        className="focus-ring rounded-full bg-blush px-5 py-2 text-sm font-semibold text-ink transition hover:bg-blush-deep disabled:opacity-60"
      >
        {status === "sending" ? "Subscribing…" : "Confirm"}
      </button>
    </form>
  );
}
