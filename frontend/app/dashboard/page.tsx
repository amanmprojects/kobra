"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { RiskBadge } from "@/components/shared/RiskBadge";
import { api } from "@/lib/api";

export default function DashboardPage() {
  const [health, setHealth] = useState<{ status: string; service: string; litellm_reachable: boolean } | null>(null);

  useEffect(() => {
    api.health().then(setHealth).catch(() => setHealth(null));
  }, []);

  const cards = [
    { href: "/urls", title: "URL Scanner", copy: "Analyze suspicious links with multi-source verdicts." },
    { href: "/prompt", title: "Prompt Guard", copy: "Test guarded LLM prompts through the LiteLLM proxy." },
    { href: "/email", title: "Inbox Scan", copy: "Connect Gmail and scan recent messages for phishing." },
  ];

  return (
    <div className="space-y-8">
      <section className="rounded-[32px] border border-border bg-panel p-8 shadow-glow">
        <div className="text-xs uppercase tracking-[0.28em] text-accent">Demo Control Center</div>
        <h2 className="mt-3 max-w-3xl text-4xl font-semibold leading-tight">
          One dashboard for suspicious URLs, adversarial prompts, and phishing emails.
        </h2>
        <p className="mt-4 max-w-2xl text-white/65">
          Kobra is wired for a demo-first workflow: scan fast, explain every verdict, and keep the guardrails visible.
        </p>
        <div className="mt-6 flex items-center gap-3">
          <RiskBadge tier={health?.litellm_reachable ? "SAFE" : "SUSPICIOUS"} />
          <span className="text-sm text-white/65">
            LiteLLM proxy {health ? (health.litellm_reachable ? "reachable" : "unreachable") : "not checked yet"}
          </span>
        </div>
      </section>

      <section className="grid gap-5 md:grid-cols-3">
        {cards.map((card) => (
          <Link key={card.href} href={card.href} className="rounded-[28px] border border-border bg-panel p-6 transition hover:-translate-y-1 hover:border-accent/40 hover:bg-panelAlt">
            <div className="text-xs uppercase tracking-[0.22em] text-white/45">Module</div>
            <h3 className="mt-3 text-2xl font-semibold">{card.title}</h3>
            <p className="mt-4 text-sm text-white/65">{card.copy}</p>
          </Link>
        ))}
      </section>
    </div>
  );
}

