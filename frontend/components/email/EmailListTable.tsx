import { RiskBadge } from "@/components/shared/RiskBadge";
import type { EmailResult } from "@/lib/types";

export function EmailListTable({
  emails,
  selectedId,
  onSelect,
}: {
  emails: EmailResult[];
  selectedId: string | null;
  onSelect: (email: EmailResult) => void;
}) {
  if (emails.length === 0) {
    return (
      <div className="rounded-[28px] border border-dashed border-border bg-panel p-6 text-sm text-white/55">
        Connect Gmail and run a scan to populate inbox results.
      </div>
    );
  }

  return (
    <div className="overflow-hidden rounded-[28px] border border-border bg-panel">
      <table className="min-w-full divide-y divide-border text-left text-sm">
        <thead className="bg-panelAlt text-white/55">
          <tr>
            <th className="px-5 py-4 font-medium">Sender</th>
            <th className="px-5 py-4 font-medium">Subject</th>
            <th className="px-5 py-4 font-medium">Received</th>
            <th className="px-5 py-4 font-medium">Risk</th>
            <th className="px-5 py-4 font-medium">Links</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-border">
          {emails.map((email) => (
            <tr
              key={email.id}
              onClick={() => onSelect(email)}
              className={`cursor-pointer transition hover:bg-panelAlt/60 ${selectedId === email.id ? "bg-panelAlt/70" : ""}`}
            >
              <td className="px-5 py-4">{email.sender}</td>
              <td className="max-w-[280px] truncate px-5 py-4">{email.subject}</td>
              <td className="px-5 py-4">{email.received_at || "-"}</td>
              <td className="px-5 py-4"><RiskBadge tier={email.risk_score.tier} /></td>
              <td className="px-5 py-4">{email.urls_malicious}/{email.urls_found}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

