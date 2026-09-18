const TILE_BG: Record<string, string> = {
  lavender: "bg-lavender/35",
  sage: "bg-sage/35",
  blush: "bg-blush/35",
};

export default function CategoryTile({
  emoji,
  label,
  accent,
}: {
  emoji: string;
  label: string;
  accent: "lavender" | "sage" | "blush";
}) {
  return (
    <button
      type="button"
      className={`focus-ring flex min-w-[140px] flex-1 flex-col items-start gap-3 rounded-tile p-5 text-left transition hover:-translate-y-0.5 ${TILE_BG[accent]}`}
    >
      <span className="text-2xl" aria-hidden>
        {emoji}
      </span>
      <span className="font-display text-sm font-semibold text-ink">{label}</span>
    </button>
  );
}
