"use client";

import { useState } from "react";

import { ExplanationCard } from "@/components/shared/ExplanationCard";
import { URLInputPanel } from "@/components/url/URLInputPanel";
import { URLResultsTable } from "@/components/url/URLResultsTable";
import { api } from "@/lib/api";
import type { URLResult } from "@/lib/types";

export default function URLsPage() {
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<URLResult[]>([]);
  const [selected, setSelected] = useState<URLResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit() {
    const urls = input
      .split("\n")
      .map((item) => item.trim())
      .filter(Boolean);
    if (urls.length === 0) return;
    setLoading(true);
    setError(null);
    try {
      const response = await api.analyzeUrls(urls);
      setResults(response.results);
      setSelected(response.results[0] ?? null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to analyze URLs.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      <URLInputPanel value={input} loading={loading} onChange={setInput} onSubmit={handleSubmit} />
      {error ? <div className="rounded-2xl border border-critical/20 bg-critical/10 p-4 text-sm text-critical">{error}</div> : null}
      <div className="grid gap-6 xl:grid-cols-[1.05fr_0.95fr]">
        <URLResultsTable results={results} selectedUrl={selected?.url ?? null} onSelect={setSelected} />
        {selected ? (
          <ExplanationCard card={selected.explanation_card} />
        ) : (
          <div className="rounded-[28px] border border-dashed border-border bg-panel p-6 text-sm text-white/55">
            Scan at least one URL to populate the explanation panel.
          </div>
        )}
      </div>
    </div>
  );
}

