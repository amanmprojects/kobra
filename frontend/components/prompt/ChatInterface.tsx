"use client";

import { useState } from "react";

type Message = {
  role: "user" | "assistant" | "blocked";
  content: string;
};

export function ChatInterface({
  onSend,
  activeCard,
}: {
  onSend: (message: string) => Promise<{ safe: boolean; llm_response?: string | null; injection_detected: boolean }>;
  activeCard: React.ReactNode;
}) {
  const [draft, setDraft] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [pending, setPending] = useState(false);

  async function submit() {
    if (!draft.trim() || pending) return;
    const outgoing = draft;
    setMessages((current) => [...current, { role: "user", content: outgoing }]);
    setDraft("");
    setPending(true);
    try {
      const response = await onSend(outgoing);
      if (response.safe && response.llm_response) {
        setMessages((current) => [...current, { role: "assistant", content: response.llm_response ?? "" }]);
      } else if (response.injection_detected) {
        setMessages((current) => [...current, { role: "blocked", content: "Blocked by prompt guard." }]);
      }
    } finally {
      setPending(false);
    }
  }

  return (
    <div className="grid gap-6 lg:grid-cols-[1.15fr_0.85fr]">
      <div className="rounded-[28px] border border-border bg-panel p-6">
        <div className="flex items-center justify-between">
          <div>
            <div className="text-xs uppercase tracking-[0.24em] text-white/45">Prompt Guard</div>
            <h2 className="mt-2 text-2xl font-semibold">Live guarded chat</h2>
          </div>
          <div className="rounded-full border border-safe/20 bg-safe/10 px-3 py-2 text-xs uppercase tracking-[0.18em] text-safe">
            Guard Active
          </div>
        </div>
        <div className="mt-5 h-[26rem] space-y-3 overflow-y-auto rounded-3xl border border-border bg-panelAlt p-4">
          {messages.length === 0 ? (
            <div className="text-sm text-white/45">Try a benign prompt or an obvious jailbreak to see the guard react.</div>
          ) : null}
          {messages.map((message, index) => (
            <div
              key={`${message.role}-${index}`}
              className={`max-w-[85%] rounded-3xl px-4 py-3 text-sm ${
                message.role === "user"
                  ? "ml-auto bg-accent text-slate-950"
                  : message.role === "blocked"
                  ? "bg-critical/20 text-critical"
                  : "bg-white/10 text-white"
              }`}
            >
              {message.content}
            </div>
          ))}
        </div>
        <div className="mt-4 flex gap-3">
          <textarea
            className="min-h-24 flex-1 rounded-3xl border border-border bg-panelAlt p-4 text-sm outline-none placeholder:text-white/35"
            value={draft}
            placeholder="Type a user prompt..."
            onChange={(event) => setDraft(event.target.value)}
          />
          <button
            type="button"
            onClick={submit}
            disabled={pending}
            className="rounded-full bg-accent px-5 py-4 text-sm font-semibold text-slate-950 disabled:opacity-50"
          >
            {pending ? "Sending..." : "Send"}
          </button>
        </div>
      </div>
      <div>{activeCard}</div>
    </div>
  );
}
