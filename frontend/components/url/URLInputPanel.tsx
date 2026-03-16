"use client";

type Props = {
  value: string;
  loading: boolean;
  onChange: (value: string) => void;
  onSubmit: () => void;
};

export function URLInputPanel({ value, loading, onChange, onSubmit }: Props) {
  return (
    <div className="rounded-[28px] border border-border bg-panel p-6">
      <div className="flex items-center justify-between">
        <div>
          <div className="text-xs uppercase tracking-[0.22em] text-white/45">URL Scanner</div>
          <h2 className="mt-2 text-2xl font-semibold">Paste one or more URLs</h2>
        </div>
        <button
          type="button"
          onClick={onSubmit}
          disabled={loading}
          className="rounded-full bg-accent px-5 py-3 text-sm font-semibold text-slate-950 transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {loading ? "Scanning..." : "Analyze URLs"}
        </button>
      </div>
      <textarea
        className="mt-5 min-h-40 w-full rounded-3xl border border-border bg-panelAlt p-4 text-sm outline-none placeholder:text-white/35"
        placeholder={"https://example.com\nhttp://paypa1-login.xyz"}
        value={value}
        onChange={(event) => onChange(event.target.value)}
      />
      <p className="mt-3 text-sm text-white/50">One URL per line. The backend trims to 50 entries.</p>
    </div>
  );
}

