import { ExplanationCard } from "@/components/shared/ExplanationCard";
import type { EmailResult } from "@/lib/types";

export function EmailDetailModal({ email }: { email: EmailResult | null }) {
  if (!email) {
    return (
      <div className="rounded-[28px] border border-dashed border-border bg-panel p-6 text-sm text-white/55">
        Select an email to inspect its explanation card.
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="rounded-[28px] border border-border bg-panel p-6">
        <div className="text-xs uppercase tracking-[0.22em] text-white/45">Email Detail</div>
        <div className="mt-3 text-sm text-white/80">
          <div><span className="text-white/50">Subject:</span> {email.subject}</div>
          <div className="mt-2"><span className="text-white/50">Sender:</span> {email.sender}</div>
          <div className="mt-2"><span className="text-white/50">Snippet:</span> {email.snippet}</div>
          {email.top_urls.length > 0 ? (
            <div className="mt-3">
              <div className="mb-2 text-white/50">Top URLs</div>
              <div className="space-y-2">
                {email.top_urls.map((url) => (
                  <div key={url} className="rounded-2xl border border-border bg-panelAlt px-3 py-2 text-xs text-white/75">
                    {url}
                  </div>
                ))}
              </div>
            </div>
          ) : null}
        </div>
      </div>
      <ExplanationCard card={email.explanation_card} />
    </div>
  );
}

