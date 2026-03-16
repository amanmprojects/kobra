from __future__ import annotations

import re
from datetime import UTC, datetime

from backend.models.schemas import PromptCheckResponse, PromptIncident
from backend.services.risk_service import to_risk_score
from backend.services.xai_service import XAIService
from backend.utils.litellm_client import check_prompt_injection


ATTACK_PATTERNS = {
    "direct_injection": [
        r"ignore (all |previous |prior )?instructions",
        r"forget (everything|all|your instructions)",
        r"disregard (your |all |previous )?instructions",
        r"override (all |previous )?instructions",
        r"do not follow the system prompt",
    ],
    "jailbreak": [
        r"you are now .*dan",
        r"developer mode",
        r"do anything now",
        r"roleplay as",
        r"act as if you have no rules",
    ],
    "prompt_leaking": [
        r"(show|reveal|repeat|output) (your |the )?(system prompt|instructions)",
        r"what are your original instructions",
        r"repeat everything above",
    ],
    "indirect_injection": [
        r"the following document says",
        r"hidden instruction",
        r"<\|system\|>",
        r"\[inst\]",
    ],
}


class PromptService:
    async def check(self, message: str, session_id: str, system_prompt: str) -> PromptCheckResponse:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message},
        ]
        try:
            result = await check_prompt_injection(messages)
        except Exception:
            result = {"safe": False, "error_body": {"error": {"message": "LiteLLM unavailable"}}}

        if result["safe"]:
            return PromptCheckResponse(
                safe=True,
                llm_response=result["response"],
                injection_detected=False,
                risk_score=to_risk_score(5),
            )
        return self._blocked_response(message, result["error_body"])

    def log_incident(self, store: dict[str, list[PromptIncident]], session_id: str, response: PromptCheckResponse, message: str) -> None:
        incident = PromptIncident(
            session_id=session_id,
            message=message,
            safe=response.safe,
            attack_type=response.attack_type,
            intent_score=response.intent_score,
            created_at=datetime.now(UTC).isoformat(),
        )
        store.setdefault(session_id, []).append(incident)

    def _blocked_response(self, message: str, error_body: dict) -> PromptCheckResponse:
        attack_type, matched_trigger = self._classify_attack(message)
        layer = self._detect_layer(error_body)
        intent_score = self._compute_intent_score(message, attack_type)
        risk_score = to_risk_score(intent_score)
        reasons = self._reasons_for_attack(attack_type, matched_trigger)
        card = XAIService.build_card(
            module="prompt",
            what_was_flagged=f"Prompt: {message[:180]}",
            why_suspicious=reasons,
            confidence=intent_score,
            severity=risk_score.tier,
            recommended_action=self._recommended_action(attack_type),
            evidence=[] if not matched_trigger else [{"fragment": matched_trigger, "reason": "Matched a known prompt attack pattern."}],
            attack_type=attack_type,
            intent_score=intent_score,
            layer_triggered=layer,
        )
        return PromptCheckResponse(
            safe=False,
            injection_detected=True,
            attack_type=attack_type,
            intent_score=intent_score,
            matched_trigger=matched_trigger,
            explanation_card=card,
            layer_triggered=layer,
            risk_score=risk_score,
        )

    def _classify_attack(self, message: str) -> tuple[str, str | None]:
        lowered = message.lower()
        for attack_type, patterns in ATTACK_PATTERNS.items():
            for pattern in patterns:
                match = re.search(pattern, lowered)
                if match:
                    return attack_type, match.group(0)
        return "unknown_injection", None

    def _detect_layer(self, error_body: dict) -> str:
        body = str(error_body).lower()
        if "similarity" in body:
            return "similarity"
        if "judge" in body or "unsafe" in body or "llm" in body:
            return "llm_judge"
        return "heuristic"

    def _compute_intent_score(self, message: str, attack_type: str) -> int:
        base = {
            "direct_injection": 92,
            "jailbreak": 86,
            "prompt_leaking": 78,
            "indirect_injection": 72,
            "unknown_injection": 65,
        }
        score = base.get(attack_type, 65)
        if len(message) > 250:
            score += 4
        if message.count("\n") > 3:
            score += 4
        return min(score, 100)

    def _reasons_for_attack(self, attack_type: str, matched_trigger: str | None) -> list[str]:
        trigger_text = f' Trigger: "{matched_trigger}".' if matched_trigger else ""
        reasons = {
            "direct_injection": [
                "The message explicitly tries to override the assistant's existing instructions." + trigger_text,
                "This is a classic direct prompt injection pattern.",
                "Forwarding the request could cause unsafe instruction following.",
            ],
            "jailbreak": [
                "The message attempts to assign a new unrestricted role to the model." + trigger_text,
                "This matches known jailbreak behavior.",
                "The request is designed to bypass guardrails rather than ask for normal help.",
            ],
            "prompt_leaking": [
                "The message attempts to reveal system-level instructions." + trigger_text,
                "System prompt leakage can expose security boundaries.",
                "The request is adversarial even if phrased as a question.",
            ],
            "indirect_injection": [
                "The message contains wrapper text or instruction markers linked to indirect prompt attacks." + trigger_text,
                "Indirect injections can smuggle hostile instructions through quoted content.",
                "The request should be blocked before it reaches the model.",
            ],
            "unknown_injection": [
                "LiteLLM flagged the message as adversarial even though no local pattern matched.",
                "The prompt should be treated as unsafe until reviewed.",
            ],
        }
        return reasons[attack_type]

    def _recommended_action(self, attack_type: str) -> str:
        if attack_type == "prompt_leaking":
            return "Block the message and avoid exposing any internal prompts or system instructions."
        if attack_type == "jailbreak":
            return "Block the message and log the session for abuse review."
        return "Block the message and keep the prompt out of the downstream model."

