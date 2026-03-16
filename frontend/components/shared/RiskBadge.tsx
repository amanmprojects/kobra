import type { Severity } from "@/lib/types";

const STYLES: Record<Severity, string> = {
  SAFE: "bg-safe/15 text-safe ring-safe/30",
  SUSPICIOUS: "bg-suspicious/15 text-suspicious ring-suspicious/30",
  MALICIOUS: "bg-malicious/15 text-malicious ring-malicious/30",
  CRITICAL: "bg-critical/15 text-critical ring-critical/30",
};

export function RiskBadge({ tier }: { tier: Severity }) {
  return (
    <span className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] ring-1 ${STYLES[tier]}`}>
      {tier}
    </span>
  );
}

