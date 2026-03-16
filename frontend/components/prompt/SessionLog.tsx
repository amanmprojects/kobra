import { RiskBadge } from "@/components/shared/RiskBadge";
import type { PromptIncident } from "@/lib/types";

export function SessionLog({ incidents }: { incidents: PromptIncident[] }) {
  return (
    <div className="rounded-[28px] border border-border bg-panel p-6">
      <div className="text-xs uppercase tracking-[0.22em] text-white/45">Session Log</div>
      <div className="mt-4 space-y-3">
        {incidents.length === 0 ? (
          <div className="text-sm text-white/50">No prompt activity yet.</div>
        ) : (
          incidents.map((incident, index) => (
            <div key={`${incident.created_at}-${index}`} className="rounded-2xl border border-border bg-panelAlt p-4">
              <div className="flex items-center justify-between gap-3">
                <RiskBadge tier={incident.safe ? "SAFE" : "CRITICAL"} />
                <div className="text-xs text-white/45">{new Date(incident.created_at).toLocaleString()}</div>
              </div>
              <div className="mt-3 text-sm text-white/80">{incident.message}</div>
              {incident.attack_type ? (
                <div className="mt-2 text-xs uppercase tracking-[0.16em] text-accent">
                  {incident.attack_type.replaceAll("_", " ")} {incident.intent_score ? `(${incident.intent_score})` : ""}
                </div>
              ) : null}
            </div>
          ))
        )}
      </div>
    </div>
  );
}

