"use client";

import { useState } from "react";
import Link from "next/link";
import LoginModal from "./LoginModal";

const NAV_ITEMS = ["Live Deals", "Compare", "Deal Check", "Alerts", "Refer & Earn"];

export default function Header() {
  const [loginOpen, setLoginOpen] = useState(false);

  return (
    <>
      <div className="bg-lavender/60">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-2 text-xs text-ink">
          <span>New: forecast confidence bands now live on every product page.</span>
          <button
            type="button"
            className="focus-ring hidden rounded-full bg-ink px-3 py-1 font-medium text-surface sm:inline-block"
          >
            See what's new
          </button>
        </div>
      </div>

      <header className="mx-auto flex max-w-6xl items-center justify-between px-6 py-5">
        <Link href="/" className="font-display text-xl font-semibold text-ink">
          DealX
        </Link>

        <nav className="hidden items-center gap-1 rounded-full border border-ink/10 bg-surface/70 p-1 md:flex">
          {NAV_ITEMS.map((item) => (
            <button
              key={item}
              type="button"
              className="focus-ring rounded-full px-4 py-2 text-sm text-ink/80 transition hover:bg-white hover:text-ink"
            >
              {item}
            </button>
          ))}
        </nav>

        <button
          type="button"
          onClick={() => setLoginOpen(true)}
          className="focus-ring rounded-full bg-ink px-5 py-2 text-sm font-medium text-surface transition hover:bg-ink/90"
        >
          Login
        </button>
      </header>

      {loginOpen && <LoginModal onClose={() => setLoginOpen(false)} />}
    </>
  );
}
