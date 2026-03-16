"use client";

import { useEffect, useMemo, useState } from "react";

import { ExplanationCard } from "@/components/shared/ExplanationCard";
import { ChatInterface } from "@/components/prompt/ChatInterface";
import { SessionLog } from "@/components/prompt/SessionLog";
import { api } from "@/lib/api";
import type { PromptCheckResponse, PromptIncident } from "@/lib/types";

const SESSION_ID = "demo-session";

export default function PromptPage() {
  const [response, setResponse] = useState<PromptCheckResponse | null>(null);
  const [incidents, setIncidents] = useState<PromptIncident[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.getPromptLog(SESSION_ID)
      .then((data) => setIncidents(data.incidents))
      .catch(() => undefined);
  }, []);

  async function handleSend(message: string) {
    setError(null);
    try {
      const data = await api.checkPrompt(message, SESSION_ID);
      setResponse(data);
      const log = await api.getPromptLog(SESSION_ID);
      setIncidents(log.incidents);
      return data;
    } catch (err) {
      setError(err instanceof Error ? err.message : "Prompt check failed.");
      return { safe: false, injection_detected: false };
    }
  }

  const card = useMemo(() => {
    if (!response?.explanation_card) {
      return (
        <div className="rounded-[28px] border border-dashed border-border bg-panel p-6 text-sm text-white/55">
          A blocked prompt will render its explanation card here.
        </div>
      );
    }
    return <ExplanationCard card={response.explanation_card} />;
  }, [response]);

  return (
    <div className="space-y-6">
      {error ? <div className="rounded-2xl border border-critical/20 bg-critical/10 p-4 text-sm text-critical">{error}</div> : null}
      <ChatInterface onSend={handleSend} activeCard={card} />
      <SessionLog incidents={incidents} />
    </div>
  );
}
