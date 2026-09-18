"use client";

import { useState } from "react";

export default function LoginModal({ onClose }: { onClose: () => void }) {
  const [stage, setStage] = useState<"start" | "otp-sent">("start");
  const [email, setEmail] = useState("");

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-ink/30 backdrop-blur-sm px-4"
      role="dialog"
      aria-modal="true"
      aria-label="Log in to DealX"
      onClick={onClose}
    >
      <div
        className="w-full max-w-sm rounded-modal bg-surface p-8 shadow-lifted"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex justify-center">
          <div className="flex h-14 w-14 items-center justify-center rounded-full bg-lavender/40">
            <span className="text-2xl">🔐</span>
          </div>
        </div>

        <h2 className="mt-5 text-center font-display text-xl font-semibold text-ink">
          Log in to DealX
        </h2>
        <p className="mt-1 text-center text-sm text-muted">
          Track deals and get alerted the moment prices move.
        </p>

        {stage === "start" && (
          <div className="mt-6 space-y-4">
            <button
              type="button"
              className="focus-ring flex w-full items-center justify-center gap-3 rounded-full border border-ink/10 bg-white py-3 text-sm font-medium text-ink transition hover:border-ink/20"
              onClick={onClose}
            >
              <span
                aria-hidden
                className="flex h-4 w-4 items-center justify-center rounded-full bg-gradient-to-br from-blush via-lavender to-sage text-[10px] font-bold text-ink"
              >
                G
              </span>
              Continue with Google
            </button>

            <div className="flex items-center gap-3 text-xs text-muted">
              <span className="h-px flex-1 bg-ink/10" />
              Or
              <span className="h-px flex-1 bg-ink/10" />
            </div>

            <form
              className="space-y-3"
              onSubmit={(e) => {
                e.preventDefault();
                if (email) setStage("otp-sent");
              }}
            >
              <label htmlFor="email" className="sr-only">
                Email address
              </label>
              <input
                id="email"
                type="email"
                required
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="focus-ring w-full rounded-full border border-ink/10 bg-white px-4 py-3 text-sm text-ink placeholder:text-muted"
              />
              <button
                type="submit"
                className="focus-ring w-full rounded-full bg-lavender py-3 text-sm font-semibold text-ink transition hover:bg-lavender-deep"
              >
                Send code
              </button>
            </form>
          </div>
        )}

        {stage === "otp-sent" && (
          <form
            className="mt-6 space-y-3"
            onSubmit={(e) => {
              e.preventDefault();
              onClose();
            }}
          >
            <p className="text-center text-sm text-ink">
              We sent a 6-digit code to <span className="font-medium">{email}</span>
            </p>
            <input
              type="text"
              inputMode="numeric"
              maxLength={6}
              placeholder="••••••"
              className="focus-ring w-full rounded-full border border-ink/10 bg-white px-4 py-3 text-center text-lg tracking-[0.5em] text-ink placeholder:tracking-normal placeholder:text-muted"
            />
            <button
              type="submit"
              className="focus-ring w-full rounded-full bg-lavender py-3 text-sm font-semibold text-ink transition hover:bg-lavender-deep"
            >
              Verify and continue
            </button>
            <button
              type="button"
              onClick={() => setStage("start")}
              className="focus-ring w-full text-center text-xs text-muted underline-offset-2 hover:underline"
            >
              Use a different email
            </button>
          </form>
        )}

        <button
          type="button"
          onClick={onClose}
          aria-label="Close"
          className="focus-ring mt-6 block w-full text-center text-xs text-muted hover:text-ink"
        >
          Close
        </button>
      </div>
    </div>
  );
}
