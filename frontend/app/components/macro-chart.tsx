import {
  ResponsiveContainer,
  LineChart,
  XAxis,
  YAxis,
  Line,
  Tooltip,
  ReferenceLine,
  ReferenceArea,
} from "recharts";

export function MacroChart({
  chartData,
}: {
  chartData: Array<{ date: string; value: number }>;
}) {
  return (
    <div className="h-64 w-full rounded-lg border border-border bg-card p-4">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData}>
          {/* X‑Axis: show only YYYY‑MM‑DD */}
          <ReferenceArea
            y1={-6}
            y2={-2}
            stroke="#228B41"
            fill="#228B22"
            fillOpacity={0.12}
          />
          {/* Red area above 3 */}
          <ReferenceArea
            y1={3}
            y2={5}
            stroke="#b72222"
            fill="#B22222"
            fillOpacity={0.12}
          />
          <XAxis
            dataKey="date"
            axisLine={false}
            tickLine={false}
            tick={{ fontSize: 12, fill: "hsl(var(--muted-foreground))" }}
            tickFormatter={(dateStr: string) => dateStr.slice(0, 10)}
            interval="preserveStartEnd"
          />
          <ReferenceLine
            y={0}
            stroke="hsl(var(--muted-foreground))"
            strokeOpacity={0.5}
            strokeDasharray="3 3"
          />
          <ReferenceLine y={2} stroke="#B22222" strokeDasharray="3 3" />
          <ReferenceLine y={-1} stroke="#228B22" strokeDasharray="3 3" />
          {/* Y‑Axis: fix domain from –8 to +5 */}
          <YAxis
            domain={[-8, 5]}
            axisLine={false}
            tickLine={false}
            tick={{ fontSize: 12, fill: "hsl(var(--muted-foreground))" }}
          />

          {/* Tooltip: show date + value on hover */}
          <Tooltip
            labelFormatter={(label: string) => `Date: ${label.slice(0, 10)}`}
            formatter={(value: any) => [`${value.toFixed(2)}`, "Score"]}
            contentStyle={{
              backgroundColor: "hsl(var(--card))", // Use your theme’s card color
              borderRadius: 4,
              color: "hsl(var(--foreground))", // Use your theme’s foreground/text
              border: "1px solid hsl(var(--border))", // Optional: for clarity
              boxShadow: "0 2px 8px rgba(0,0,0,0.07)",
            }}
            itemStyle={{
              color: "hsl(var(--muted-foreground))", // Muted for secondary text
            }}
          />

          <Line
            type="monotone"
            dataKey="value"
            stroke="hsl(var(--foreground))"
            strokeWidth={2}
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
