import { Bar, BarChart, Cell, ResponsiveContainer, XAxis, YAxis } from "recharts";

type Entry = {
  feature: string;
  value: number;
  contribution: number;
};

export function SHAPWaterfallChart({ entries }: { entries: Entry[] }) {
  const data = [...entries].sort((a, b) => Math.abs(b.contribution) - Math.abs(a.contribution));

  return (
    <div className="h-64 w-full rounded-2xl border border-border bg-panelAlt p-3">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} layout="vertical" margin={{ left: 20, right: 12 }}>
          <XAxis type="number" stroke="#93a7cc" />
          <YAxis type="category" dataKey="feature" stroke="#93a7cc" width={110} />
          <Bar dataKey="contribution" radius={[8, 8, 8, 8]}>
            {data.map((entry) => (
              <Cell key={entry.feature} fill={entry.contribution >= 0 ? "#dc2626" : "#3b82f6"} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

