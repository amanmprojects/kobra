from __future__ import annotations

import asyncio
import base64

import httpx

from backend.config import settings
from backend.models.ml.xgboost_model import XGBoostURLClassifier
from backend.models.schemas import (
    EvidenceHighlight,
    ExplanationCard,
    SafeBrowsingResult,
    SHAPEntry,
    URLResult,
    VirusTotalResult,
)
from backend.services.risk_service import to_risk_score
from backend.services.xai_service import XAIService
from backend.utils.url_features import extract_features


class URLService:
    def __init__(self, model: XGBoostURLClassifier) -> None:
        self.model = model

    async def analyze_batch(self, urls: list[str]) -> list[URLResult]:
        tasks = [self.analyze_single(url) for url in urls]
        return await asyncio.gather(*tasks)

    async def analyze_single(self, url: str) -> URLResult:
        features = extract_features(url)
        prediction = self.model.predict(features)
        vt_result, sb_result = await asyncio.gather(
            self._query_virustotal(url),
            self._query_safe_browsing(url),
        )

        malicious = sb_result.flagged or vt_result.engines_flagged >= 3 or prediction.probability >= 0.75
        suspicious = malicious or vt_result.engines_flagged > 0 or prediction.probability >= 0.45
        verdict = "MALICIOUS" if malicious else "SUSPICIOUS" if suspicious else "SAFE"
        score = max(
            int(prediction.probability * 100),
            100 if sb_result.flagged else 0,
            min(vt_result.engines_flagged * 15, 95),
        )
        risk_score = to_risk_score(score)
        shap_entries = [SHAPEntry(**entry) for entry in prediction.shap_entries]
        explanation = self._build_explanation(
            url=url,
            features=features,
            vt_result=vt_result,
            sb_result=sb_result,
            probability=prediction.probability,
            verdict=verdict,
            risk_score=risk_score.score,
            severity=risk_score.tier,
            shap_entries=shap_entries,
        )
        return URLResult(
            url=url,
            verdict=verdict,
            risk_score=risk_score,
            virustotal=vt_result,
            safe_browsing=sb_result,
            xgboost_probability=round(prediction.probability, 4),
            shap_waterfall=shap_entries,
            explanation_card=explanation,
        )

    async def _query_virustotal(self, url: str) -> VirusTotalResult:
        if not settings.virustotal_api_key:
            return VirusTotalResult(unavailable=True)
        url_id = base64.urlsafe_b64encode(url.encode()).decode().strip("=")
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                response = await client.get(
                    f"https://www.virustotal.com/api/v3/urls/{url_id}",
                    headers={"x-apikey": settings.virustotal_api_key},
                )
            if response.status_code != 200:
                return VirusTotalResult(unavailable=True)
            attributes = response.json()["data"]["attributes"]
            stats = attributes["last_analysis_stats"]
            flagged = stats.get("malicious", 0) + stats.get("suspicious", 0)
            categories = list(attributes.get("categories", {}).values())[:3]
            return VirusTotalResult(
                engines_flagged=flagged,
                total_engines=sum(int(value) for value in stats.values()),
                categories=categories,
            )
        except Exception:
            return VirusTotalResult(unavailable=True)

    async def _query_safe_browsing(self, url: str) -> SafeBrowsingResult:
        if not settings.google_safe_browsing_api_key:
            return SafeBrowsingResult(unavailable=True)
        payload = {
            "client": {"clientId": "kobra", "clientVersion": "1.0"},
            "threatInfo": {
                "threatTypes": [
                    "MALWARE",
                    "SOCIAL_ENGINEERING",
                    "UNWANTED_SOFTWARE",
                    "POTENTIALLY_HARMFUL_APPLICATION",
                ],
                "platformTypes": ["ANY_PLATFORM"],
                "threatEntryTypes": ["URL"],
                "threatEntries": [{"url": url}],
            },
        }
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                response = await client.post(
                    "https://safebrowsing.googleapis.com/v4/threatMatches:find",
                    params={"key": settings.google_safe_browsing_api_key},
                    json=payload,
                )
            if response.status_code != 200:
                return SafeBrowsingResult(unavailable=True)
            matches = response.json().get("matches", [])
            if not matches:
                return SafeBrowsingResult(flagged=False)
            return SafeBrowsingResult(flagged=True, threat_type=matches[0].get("threatType"))
        except Exception:
            return SafeBrowsingResult(unavailable=True)

    def _build_explanation(
        self,
        *,
        url: str,
        features: dict[str, float],
        vt_result: VirusTotalResult,
        sb_result: SafeBrowsingResult,
        probability: float,
        verdict: str,
        risk_score: int,
        severity: str,
        shap_entries: list[SHAPEntry],
    ) -> ExplanationCard:
        reasons: list[str] = []
        evidence: list[EvidenceHighlight] = []
        if vt_result.engines_flagged:
            reasons.append(f"VirusTotal flagged the URL with {vt_result.engines_flagged} suspicious engines.")
        if sb_result.flagged:
            reasons.append(f"Google Safe Browsing marked the URL as {sb_result.threat_type or 'unsafe'}.")
        if features["brand_mimic_score"]:
            reasons.append("The hostname appears to mimic a known brand using character substitution.")
        if features["has_ip_address"]:
            reasons.append("The URL uses a raw IP address instead of a normal domain.")
        if features["suspicious_tld"]:
            reasons.append("The domain ends in a high-risk top-level domain.")
        if features["entropy"] > 4.2:
            reasons.append("The URL has unusually high entropy, which is common in obfuscated links.")
        if not reasons:
            reasons.append("No strong malicious signals were found across the current checks.")
        if shap_entries:
            top = shap_entries[0]
            evidence.append(
                EvidenceHighlight(
                    fragment=url[:120],
                    reason=f"Top model signal: {top.feature} ({top.contribution:+.2f}).",
                )
            )
        action = (
            "Do not open this link. Block or quarantine it before sharing further."
            if verdict == "MALICIOUS"
            else "Verify the source before opening the link."
            if verdict == "SUSPICIOUS"
            else "The link appears low risk based on the current checks."
        )
        return XAIService.build_card(
            module="url",
            what_was_flagged=f"URL: {url}",
            why_suspicious=reasons,
            confidence=risk_score,
            severity=severity,
            recommended_action=action,
            evidence=evidence,
            shap_waterfall=shap_entries,
        )

