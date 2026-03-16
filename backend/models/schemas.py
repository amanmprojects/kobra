from typing import Literal

from pydantic import BaseModel, Field, HttpUrl


Severity = Literal["SAFE", "SUSPICIOUS", "MALICIOUS", "CRITICAL"]
PromptAttackType = Literal[
    "direct_injection",
    "jailbreak",
    "prompt_leaking",
    "indirect_injection",
    "unknown_injection",
]


class SHAPEntry(BaseModel):
    feature: str
    value: float
    contribution: float


class LIMEEntry(BaseModel):
    word: str
    influence: float


class EvidenceHighlight(BaseModel):
    fragment: str
    reason: str


class ExplanationCard(BaseModel):
    module: Literal["url", "prompt", "phishing"]
    what_was_flagged: str
    why_suspicious: list[str] = Field(default_factory=list)
    evidence: list[EvidenceHighlight] = Field(default_factory=list)
    confidence: int
    severity: Severity
    recommended_action: str
    shap_waterfall: list[SHAPEntry] | None = None
    attention_heatmap: dict[str, float] | None = None
    lime_rationale: list[LIMEEntry] | None = None
    attack_type: PromptAttackType | None = None
    intent_score: int | None = None
    layer_triggered: Literal["heuristic", "similarity", "llm_judge"] | None = None


class RiskScore(BaseModel):
    score: int = Field(ge=0, le=100)
    tier: Severity


class URLAnalyzeRequest(BaseModel):
    urls: list[str] = Field(min_length=1, max_length=50)


class VirusTotalResult(BaseModel):
    engines_flagged: int = 0
    total_engines: int = 0
    categories: list[str] = Field(default_factory=list)
    unavailable: bool = False


class SafeBrowsingResult(BaseModel):
    flagged: bool = False
    threat_type: str | None = None
    unavailable: bool = False


class URLResult(BaseModel):
    url: str
    verdict: Literal["SAFE", "SUSPICIOUS", "MALICIOUS"]
    risk_score: RiskScore
    virustotal: VirusTotalResult
    safe_browsing: SafeBrowsingResult
    xgboost_probability: float
    shap_waterfall: list[SHAPEntry]
    explanation_card: ExplanationCard


class URLAnalyzeResponse(BaseModel):
    results: list[URLResult]


class PromptCheckRequest(BaseModel):
    message: str = Field(min_length=1, max_length=6000)
    session_id: str = Field(min_length=1, max_length=128)
    system_prompt: str = "You are Kobra, a helpful cybersecurity assistant."


class PromptCheckResponse(BaseModel):
    safe: bool
    llm_response: str | None = None
    injection_detected: bool
    attack_type: PromptAttackType | None = None
    intent_score: int | None = None
    matched_trigger: str | None = None
    explanation_card: ExplanationCard | None = None
    layer_triggered: Literal["heuristic", "similarity", "llm_judge"] | None = None
    risk_score: RiskScore


class PromptIncident(BaseModel):
    session_id: str
    message: str
    safe: bool
    attack_type: PromptAttackType | None = None
    intent_score: int | None = None
    created_at: str


class PromptSessionLogResponse(BaseModel):
    incidents: list[PromptIncident]
    total_blocked: int
    total_safe: int


class GmailOAuthStartResponse(BaseModel):
    authorization_url: HttpUrl


class GmailScanRequest(BaseModel):
    access_token: str = Field(min_length=10)


class EmailResult(BaseModel):
    id: str
    subject: str
    sender: str
    sender_domain: str
    received_at: str
    snippet: str
    risk_score: RiskScore
    explanation_card: ExplanationCard
    urls_found: int
    urls_malicious: int
    top_urls: list[str] = Field(default_factory=list)


class GmailScanSummary(BaseModel):
    total: int
    safe: int
    suspicious: int
    malicious: int
    critical: int


class GmailScanResponse(BaseModel):
    emails: list[EmailResult]
    scan_summary: GmailScanSummary


class HealthResponse(BaseModel):
    status: Literal["ok"]
    service: str
    litellm_reachable: bool

