import { RiskBadge } from "@/components/shared/RiskBadge";
import type { URLResult } from "@/lib/types";

export function URLResultsTable({
  results,
  selectedUrl,
  onSelect,
}: {
  results: URLResult[];
  selectedUrl: string | null;
  onSelect: (value: URLResult) => void;
}) {
  if (results.length === 0) {
    return (
      <div className="rounded-[28px] border border-dashed border-border bg-panel p-6 text-sm text-white/55">
        Results will appear here after the first scan.
      </div>
    );
  }

  return (
    <div className="overflow-hidden rounded-[28px] border border-border bg-panel">
      <table className="min-w-full divide-y divide-border text-left text-sm">
        <thead className="bg-panelAlt text-white/55">
          <tr>
            <th className="px-5 py-4 font-medium">URL</th>
            <th className="px-5 py-4 font-medium">Verdict</th>
            <th className="px-5 py-4 font-medium">Score</th>
            <th className="px-5 py-4 font-medium">VirusTotal</th>
            <th className="px-5 py-4 font-medium">Safe Browsing</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-border">
          {results.map((result) => (
            <tr
              key={result.url}
              onClick={() => onSelect(result)}
              className={`cursor-pointer transition hover:bg-panelAlt/60 ${selectedUrl === result.url ? "bg-panelAlt/70" : ""}`}
            >
              <td className="max-w-[280px] truncate px-5 py-4">{result.url}</td>
              <td className="px-5 py-4"><RiskBadge tier={result.risk_score.tier} /></td>
              <td className="px-5 py-4">{result.risk_score.score}</td>
              <td className="px-5 py-4">
                {result.virustotal.unavailable ? "Unavailable" : `${result.virustotal.engines_flagged}/${result.virustotal.total_engines}`}
              </td>
              <td className="px-5 py-4">
                {result.safe_browsing.unavailable ? "Unavailable" : result.safe_browsing.flagged ? result.safe_browsing.threat_type || "Flagged" : "Clear"}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

