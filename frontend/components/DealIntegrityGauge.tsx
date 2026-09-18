function polarToCartesian(cx: number, cy: number, r: number, angleDeg: number) {
  const angleRad = ((angleDeg - 180) * Math.PI) / 180;
  return { x: cx + r * Math.cos(angleRad), y: cy + r * Math.sin(angleRad) };
}

function arcPath(cx: number, cy: number, r: number, startDeg: number, endDeg: number) {
  const start = polarToCartesian(cx, cy, r, startDeg);
  const end = polarToCartesian(cx, cy, r, endDeg);
  const largeArc = endDeg - startDeg <= 180 ? 0 : 1;
  return `M ${start.x} ${start.y} A ${r} ${r} 0 ${largeArc} 1 ${end.x} ${end.y}`;
}

function verdict(score: number) {
  if (score >= 70) return { label: "Genuine discount", color: "#87A882" };
  if (score >= 40) return { label: "Mixed signal", color: "#9C87C4" };
  return { label: "Inflated \u2018sale\u2019", color: "#D69A90" };
}

export default function DealIntegrityGauge({ score }: { score: number }) {
  const clamped = Math.max(0, Math.min(100, score));
  const cx = 110;
  const cy = 100;
  const r = 84;
  const needleAngle = (clamped / 100) * 180;
  const needleTip = polarToCartesian(cx, cy, r - 14, needleAngle);
  const { label, color } = verdict(clamped);

  return (
    <div className="flex flex-col items-center">
      <svg viewBox="0 0 220 120" className="w-full max-w-[260px]">
        <path d={arcPath(cx, cy, r, 0, 72)} stroke="#E3B8B0" strokeWidth={16} fill="none" strokeLinecap="round" />
        <path d={arcPath(cx, cy, r, 72, 126)} stroke="#B9A9DB" strokeWidth={16} fill="none" />
        <path d={arcPath(cx, cy, r, 126, 180)} stroke="#A9C4A5" strokeWidth={16} fill="none" strokeLinecap="round" />
        <line x1={cx} y1={cy} x2={needleTip.x} y2={needleTip.y} stroke="#3B362F" strokeWidth={3} strokeLinecap="round" />
        <circle cx={cx} cy={cy} r={5} fill="#3B362F" />
      </svg>
      <div className="-mt-2 text-center">
        <span className="font-display text-3xl font-semibold text-ink">{clamped}</span>
        <span className="text-sm text-muted">/100</span>
      </div>
      <span
        className="mt-2 rounded-full px-3 py-1 text-xs font-medium text-ink"
        style={{ backgroundColor: `${color}40` }}
      >
        {label}
      </span>
    </div>
  );
}
