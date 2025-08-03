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
  // Function to calculate tick interval based on data length
  const getTickInterval = (dataLength: number) => {
    if (dataLength <= 10) return 0; // Show all ticks
    if (dataLength <= 30) return Math.floor(dataLength / 8);
    if (dataLength <= 60) return Math.floor(dataLength / 6);
    return Math.floor(dataLength / 5); // Show ~5 ticks for large datasets
  };

  // Format date for display (shorter format)
  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "2-digit",
    });
  };

  return (
    <div className="h-64 w-full rounded-lg border border-border bg-card p-2">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData}>
          <ReferenceArea
            y1={-6}
            y2={-2}
            stroke="#228B41"
            fill="#228B22"
            fillOpacity={0.12}
          />
          <ReferenceArea
            y1={3}
            y2={6}
            stroke="#b72222"
            fill="#B22222"
            fillOpacity={0.12}
          />
          <XAxis
            dataKey="date"
            axisLine={false}
            tickLine={false}
            tick={{
              fontSize: 11,
              fill: "hsl(var(--muted-foreground))",
              angle: -45,
              textAnchor: "end",
              height: 60,
            }}
            tickFormatter={formatDate}
            interval={getTickInterval(chartData.length)}
            height={70} // Increased height to accommodate angled text
          />
          <ReferenceLine
            y={0}
            stroke="hsl(var(--muted-foreground))"
            strokeOpacity={0.5}
            strokeDasharray="3 3"
          />
          <ReferenceLine y={2} stroke="#B22222" strokeDasharray="3 3" />
          <ReferenceLine y={-1} stroke="#228B22" strokeDasharray="3 3" />

          <YAxis
            domain={[-8, 6]}
            axisLine={false}
            tickLine={false}
            tick={{ fontSize: 12, fill: "hsl(var(--muted-foreground))" }}
          />

          {/* Tooltip: show full date + value on hover */}
          <Tooltip
            labelFormatter={(label: string) => {
              const date = new Date(label);
              return `Date: ${date.toLocaleDateString("en-US", {
                weekday: "short",
                year: "numeric",
                month: "short",
                day: "numeric",
              })}`;
            }}
            formatter={(value: any) => [`${value.toFixed(2)}`, "Score"]}
            contentStyle={{
              backgroundColor: "hsl(var(--card))",
              borderRadius: 4,
              color: "hsl(var(--foreground))",
              border: "1px solid hsl(var(--border))",
              boxShadow: "0 2px 8px rgba(0,0,0,0.07)",
              fontSize: "clamp(0.75rem, 2vw, 0.875rem)",
              padding: "clamp(6px, 1.5vw, 8px)",
              maxWidth: "min(250px, 90vw)",
            }}
            itemStyle={{
              color: "hsl(var(--muted-foreground))",
              fontSize: "clamp(0.7rem, 1.8vw, 0.8rem)",
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
