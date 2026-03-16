from backend.models.schemas import EvidenceHighlight, ExplanationCard, LIMEEntry, SHAPEntry


class XAIService:
    @staticmethod
    def build_card(
        *,
        module: str,
        what_was_flagged: str,
        why_suspicious: list[str],
        confidence: int,
        severity: str,
        recommended_action: str,
        evidence: list[EvidenceHighlight] | None = None,
        shap_waterfall: list[SHAPEntry] | None = None,
        attention_heatmap: dict[str, float] | None = None,
        lime_rationale: list[LIMEEntry] | None = None,
        attack_type: str | None = None,
        intent_score: int | None = None,
        layer_triggered: str | None = None,
    ) -> ExplanationCard:
        return ExplanationCard(
            module=module,
            what_was_flagged=what_was_flagged,
            why_suspicious=why_suspicious[:6],
            evidence=evidence or [],
            confidence=confidence,
            severity=severity,
            recommended_action=recommended_action,
            shap_waterfall=shap_waterfall,
            attention_heatmap=attention_heatmap,
            lime_rationale=lime_rationale,
            attack_type=attack_type,
            intent_score=intent_score,
            layer_triggered=layer_triggered,
        )

