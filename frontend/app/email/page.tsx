"use client";

import { Suspense, useEffect, useMemo, useState } from "react";
import { useSearchParams } from "next/navigation";

import { EmailDetailModal } from "@/components/email/EmailDetailModal";
import { EmailListTable } from "@/components/email/EmailListTable";
import { api } from "@/lib/api";
import type { EmailResult, GmailScanResponse } from "@/lib/types";

function EmailPageClient() {
  const searchParams = useSearchParams();
  const accessToken = searchParams.get("access_token");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<GmailScanResponse | null>(null);
  const [selected, setSelected] = useState<EmailResult | null>(null);

  useEffect(() => {
    if (!accessToken) return;
    setLoading(true);
    api.scanGmail(accessToken)
      .then((response) => {
        setData(response);
        setSelected(response.emails[0] ?? null);
      })
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to scan Gmail."))
      .finally(() => setLoading(false));
  }, [accessToken]);

  async function connectGmail() {
    setError(null);
    try {
      const response = await api.startGmailOAuth();
      window.location.href = response.authorization_url;
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to start Gmail OAuth.");
    }
  }

  const stats = useMemo(() => data?.scan_summary, [data]);

  return (
    <div className="space-y-6">
      <div className="rounded-[28px] border border-border bg-panel p-6">
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div>
            <div className="text-xs uppercase tracking-[0.22em] text-white/45">Inbox Scan</div>
            <h2 className="mt-2 text-2xl font-semibold">Scan recent Gmail messages for phishing</h2>
          </div>
          <button
            type="button"
            onClick={connectGmail}
            disabled={loading}
            className="rounded-full bg-accent px-5 py-3 text-sm font-semibold text-slate-950 disabled:opacity-50"
          >
            {loading ? "Scanning..." : accessToken ? "Rescan Inbox" : "Connect Gmail"}
          </button>
        </div>
        {stats ? (
          <div className="mt-5 grid gap-3 md:grid-cols-5">
            {Object.entries(stats).map(([key, value]) => (
              <div key={key} className="rounded-2xl border border-border bg-panelAlt p-4">
                <div className="text-xs uppercase tracking-[0.18em] text-white/45">{key}</div>
                <div className="mt-2 text-2xl font-semibold">{value}</div>
              </div>
            ))}
          </div>
        ) : null}
      </div>

      {error ? <div className="rounded-2xl border border-critical/20 bg-critical/10 p-4 text-sm text-critical">{error}</div> : null}

      <div className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
        <EmailListTable emails={data?.emails ?? []} selectedId={selected?.id ?? null} onSelect={setSelected} />
        <EmailDetailModal email={selected} />
      </div>
    </div>
  );
}

export default function EmailPage() {
  return (
    <Suspense
      fallback={
        <div className="rounded-[28px] border border-border bg-panel p-6 text-sm text-white/55">
          Loading email scanner...
        </div>
      }
    >
      <EmailPageClient />
    </Suspense>
  );
}
