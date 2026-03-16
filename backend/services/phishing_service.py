from __future__ import annotations

import re
from collections import Counter

from backend.config import settings
from backend.models.schemas import EvidenceHighlight, LIMEEntry
from backend.services.risk_service import to_risk_score
from backend.services.xai_service import XAIService

try:
    import torch
    from transformers import AutoModelForSequenceClassification, AutoTokenizer
except Exception:  # pragma: no cover
    AutoModelForSequenceClassification = None
    AutoTokenizer = None
    torch = None


class PhishingService:
    def __init__(self) -> None:
        self._loaded = False
        self._tokenizer = None
        self._model = None

    def _ensure_model(self) -> None:
        if self._loaded:
            return
        self._loaded = True
        if AutoTokenizer is None or AutoModelForSequenceClassification is None:
            return
        try:
            self._tokenizer = AutoTokenizer.from_pretrained(settings.phishing_model_name)
            self._model = AutoModelForSequenceClassification.from_pretrained(settings.phishing_model_name)
            self._model.eval()
        except Exception:
            self._tokenizer = None
            self._model = None

    def analyze_email(self, email: dict, url_scores: list[int]) -> dict:
        self._ensure_model()
        if self._tokenizer is not None and self._model is not None and torch is not None:
            return self._model_analyze(email, url_scores)
        return self._heuristic_analyze(email, url_scores)

    def _model_analyze(self, email: dict, url_scores: list[int]) -> dict:
        text = f"{email['subject']} [SEP] {email['sender']} [SEP] {email['body'][:1200]}"
        inputs = self._tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        with torch.no_grad():
            outputs = self._model(**inputs, output_attentions=True)
        probabilities = torch.softmax(outputs.logits, dim=-1)[0]
        phishing_probability = float(probabilities[-1])
        tokens = self._tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])
        attention = outputs.attentions[-1][0].mean(dim=0)[0]
        top_pairs = sorted(
            ((token, float(attention[index])) for index, token in enumerate(tokens) if token not in {"<s>", "</s>", "<pad>"}),
            key=lambda item: item[1],
            reverse=True,
        )[:8]
        attention_heatmap = {token: round(weight, 4) for token, weight in top_pairs}
        return self._build_response(email, phishing_probability, attention_heatmap, url_scores)

    def _heuristic_analyze(self, email: dict, url_scores: list[int]) -> dict:
        text = f"{email['subject']} {email['body']}".lower()
        score = 0
        keyword_hits = [kw for kw in ["urgent", "verify", "password", "suspended", "payment", "login", "click"] if kw in text]
        score += min(len(keyword_hits) * 10, 30)
        if re.search(r"paypa1|g00gle|micros0ft|amaz0n", email["sender_domain"]):
            score += 25
        if len(email.get("urls", [])) >= 3:
            score += 15
        if any(url_score >= 60 for url_score in url_scores):
            score += 25
        phishing_probability = min(max(score / 100, 0.05), 0.95)
        token_counts = Counter(re.findall(r"[a-zA-Z]{4,}", text))
        attention_heatmap = {word: round(min(count / 5, 1.0), 2) for word, count in token_counts.most_common(8)}
        return self._build_response(email, phishing_probability, attention_heatmap, url_scores)

    def _build_response(self, email: dict, phishing_probability: float, attention_heatmap: dict[str, float], url_scores: list[int]) -> dict:
        risk_score = to_risk_score(int(phishing_probability * 100))
        reasons = []
        body_lower = email["body"].lower()
        if any(word in body_lower for word in ["urgent", "verify", "immediately", "suspended", "login"]):
            reasons.append("The email uses urgency or credential-related language common in phishing.")
        if re.search(r"paypa1|g00gle|micros0ft|amaz0n", email["sender_domain"]):
            reasons.append(f"The sender domain looks like a spoofed brand: {email['sender_domain']}.")
        if any(score >= 60 for score in url_scores):
            reasons.append("The email contains one or more links that were scored as risky.")
        if not reasons:
            reasons.append("No major phishing heuristics triggered strongly, but the content was still scored.")
        top_tokens = list(attention_heatmap.items())[:3]
        evidence = [EvidenceHighlight(fragment=token, reason=f"Elevated token signal ({weight}).") for token, weight in top_tokens]
        lime = [LIMEEntry(word=token, influence=round(weight / 2, 3)) for token, weight in top_tokens]
        card = XAIService.build_card(
            module="phishing",
            what_was_flagged=f"Email from {email['sender']} with subject '{email['subject']}'",
            why_suspicious=reasons,
            confidence=risk_score.score,
            severity=risk_score.tier,
            recommended_action=(
                "Do not interact with the message until the sender is verified."
                if risk_score.score >= 60
                else "Verify the sender through a trusted channel before acting on the email."
                if risk_score.score >= 30
                else "The message appears low risk based on current analysis."
            ),
            evidence=evidence,
            attention_heatmap=attention_heatmap,
            lime_rationale=lime,
        )
        return {
            "risk_score": risk_score,
            "explanation_card": card,
        }

