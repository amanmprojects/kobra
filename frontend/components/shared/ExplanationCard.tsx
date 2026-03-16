import { ConfidenceMeter } from "@/components/shared/ConfidenceMeter";
import { RiskBadge } from "@/components/shared/RiskBadge";
import { SHAPWaterfallChart } from "@/components/shared/SHAPWaterfallChart";
import type { ExplanationCard as ExplanationCardType } from "@/lib/types";

export function ExplanationCard({ card }: { card: ExplanationCardType }) {
  return (
    <section className="space-y-5 rounded-[28px] border border-border bg-panel p-6 shadow-glow">
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div className="space-y-2">
          <div className="text-xs uppercase tracking-[0.28em] text-white/45">Threat Explanation</div>
          <div className="flex items-center gap-3">
            <RiskBadge tier={card.severity} />
            {card.attack_type ? (
              <span className="rounded-full border border-accent/20 bg-accent/10 px-3 py-1 text-xs uppercase tracking-[0.18em] text-accent">
                {card.attack_type.replaceAll("_", " ")}
              </span>
            ) : null}
          </div>
        </div>
        <ConfidenceMeter value={card.confidence} />
      </div>

      <div>
        <div className="text-xs uppercase tracking-[0.22em] text-white/50">What Was Flagged</div>
        <p className="mt-2 text-lg text-white">{card.what_was_flagged}</p>
      </div>

      <div>
        <div className="text-xs uppercase tracking-[0.22em] text-white/50">Why Suspicious</div>
        <ol className="mt-3 space-y-2 text-sm text-white/80">
          {card.why_suspicious.map((item, index) => (
            <li key={`${item}-${index}`} className="rounded-2xl border border-border bg-panelAlt px-4 py-3">
              <span className="mr-3 text-accent">{String(index + 1).padStart(2, "0")}</span>
              {item}
            </li>
          ))}
        </ol>
      </div>

      {card.evidence.length > 0 ? (
        <div>
          <div className="text-xs uppercase tracking-[0.22em] text-white/50">Evidence</div>
          <div className="mt-3 grid gap-3 md:grid-cols-2">
            {card.evidence.map((item, index) => (
              <div key={`${item.fragment}-${index}`} className="rounded-2xl border border-border bg-panelAlt p-4">
                <div className="text-sm font-medium text-white">{item.fragment}</div>
                <p className="mt-1 text-sm text-white/65">{item.reason}</p>
              </div>
            ))}
          </div>
        </div>
      ) : null}

      {card.shap_waterfall && card.shap_waterfall.length > 0 ? (
        <div>
          <div className="mb-3 text-xs uppercase tracking-[0.22em] text-white/50">Top Feature Contributions</div>
          <SHAPWaterfallChart entries={card.shap_waterfall} />
        </div>
      ) : null}

      {card.attention_heatmap && Object.keys(card.attention_heatmap).length > 0 ? (
        <div>
          <div className="text-xs uppercase tracking-[0.22em] text-white/50">Highlighted Tokens</div>
          <div className="mt-3 flex flex-wrap gap-2">
            {Object.entries(card.attention_heatmap).map(([token, weight]) => (
              <span key={token} className="rounded-full border border-border bg-panelAlt px-3 py-2 text-xs text-white/80">
                {token} <span className="text-accent">{Math.round(weight * 100)}%</span>
              </span>
            ))}
          </div>
        </div>
      ) : null}

      {card.lime_rationale && card.lime_rationale.length > 0 ? (
        <div>
          <div className="text-xs uppercase tracking-[0.22em] text-white/50">Local Rationale</div>
          <div className="mt-3 flex flex-wrap gap-2">
            {card.lime_rationale.map((item) => (
              <span key={item.word} className="rounded-full border border-border bg-panelAlt px-3 py-2 text-xs text-white/75">
                {item.word} <span className="text-accent">{item.influence.toFixed(2)}</span>
              </span>
            ))}
          </div>
        </div>
      ) : null}

      <div className="rounded-2xl border border-suspicious/20 bg-suspicious/10 p-4">
        <div className="text-xs uppercase tracking-[0.22em] text-suspicious">Recommended Action</div>
        <p className="mt-2 text-sm text-white/85">{card.recommended_action}</p>
      </div>
    </section>
  );
}

