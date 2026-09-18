"use client";

import {
  ComposedChart,
  Line,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { PricePoint, ForecastPoint } from "@/lib/types";

interface ChartRow {
  date: string;
  actual?: number;
  forecast?: number;
  band?: [number, number];
}

function formatDate(iso: string) {
  const d = new Date(iso);
  return d.toLocaleDateString("en-IN", { month: "short", day: "numeric" });
}

export default function PriceChart({
  history,
  forecast,
  currency,
}: {
  history: PricePoint[];
  forecast: ForecastPoint[];
  currency: string;
}) {
  const rows: ChartRow[] = [
    ...history.map((p) => ({ date: p.date, actual: p.price })),
    ...forecast.map((p, i) => ({
      date: p.date,
      forecast: p.price,
      band: [p.confidenceLow, p.confidenceHigh] as [number, number],
      // bridge the gap so the dashed line starts exactly where the solid one ends
      ...(i === 0 ? { actual: history[history.length - 1]?.price } : {}),
    })),
  ];

  return (
    <div className="h-72 w-full sm:h-80">
      <ResponsiveContainer width="100%" height="100%">
        <ComposedChart data={rows} margin={{ top: 8, right: 8, bottom: 0, left: -12 }}>
          <CartesianGrid stroke="#3B362F" strokeOpacity={0.08} vertical={false} />
          <XAxis
            dataKey="date"
            tickFormatter={formatDate}
            interval={Math.floor(rows.length / 6)}
            tick={{ fill: "#8A8072", fontSize: 12 }}
            axisLine={{ stroke: "#3B362F", strokeOpacity: 0.1 }}
            tickLine={false}
          />
          <YAxis
            tick={{ fill: "#8A8072", fontSize: 12 }}
            axisLine={false}
            tickLine={false}
            tickFormatter={(v) => `${currency}${Math.round(v / 100) / 10}k`}
            width={56}
          />
          <Tooltip
            formatter={(value: number, name: string) => [
              `${currency}${Math.round(value).toLocaleString("en-IN")}`,
              name === "actual" ? "Price" : "Forecast",
            ]}
            labelFormatter={(label: string) => formatDate(label)}
            contentStyle={{
              background: "#FBF8F3",
              border: "1px solid rgba(59,54,47,0.1)",
              borderRadius: 12,
              fontSize: 13,
            }}
          />
          <Area
            dataKey="band"
            stroke="none"
            fill="#B9A9DB"
            fillOpacity={0.15}
            isAnimationActive={false}
          />
          <Line
            type="monotone"
            dataKey="actual"
            stroke="#3B362F"
            strokeWidth={2.5}
            dot={false}
            isAnimationActive={false}
          />
          <Line
            type="monotone"
            dataKey="forecast"
            stroke="#9C87C4"
            strokeWidth={2.5}
            strokeDasharray="6 5"
            dot={false}
            isAnimationActive={false}
          />
        </ComposedChart>
      </ResponsiveContainer>
      <div className="mt-2 flex items-center gap-5 text-xs text-muted">
        <span className="flex items-center gap-1.5">
          <span className="h-0.5 w-4 bg-ink" /> Price history
        </span>
        <span className="flex items-center gap-1.5">
          <span
            className="h-0.5 w-4"
            style={{
              backgroundImage: "repeating-linear-gradient(90deg, #9C87C4 0 4px, transparent 4px 7px)",
            }}
          />
          30-day forecast
        </span>
      </div>
    </div>
  );
}
