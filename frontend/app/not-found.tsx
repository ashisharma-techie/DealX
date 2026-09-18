import Link from "next/link";

export default function NotFound() {
  return (
    <main className="mx-auto flex min-h-screen max-w-md flex-col items-center justify-center px-6 text-center">
      <p className="text-4xl">🔍</p>
      <h1 className="mt-4 font-display text-xl font-semibold text-ink">We couldn't find that product</h1>
      <p className="mt-2 text-sm text-muted">It may have been removed, or the link is off.</p>
      <Link href="/" className="focus-ring mt-6 rounded-full bg-lavender px-5 py-2 text-sm font-semibold text-ink">
        Back to trending deals
      </Link>
    </main>
  );
}
