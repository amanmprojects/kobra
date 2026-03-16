type Props = {
  value: number;
  label?: string;
};

export function ConfidenceMeter({ value, label = "Confidence" }: Props) {
  const clamped = Math.max(0, Math.min(100, value));
  return (
    <div className="flex min-w-[112px] flex-col items-center justify-center rounded-2xl border border-border bg-panelAlt px-4 py-3">
      <div className="text-[10px] uppercase tracking-[0.22em] text-white/60">{label}</div>
      <div className="mt-2 text-3xl font-semibold">{clamped}%</div>
    </div>
  );
}

