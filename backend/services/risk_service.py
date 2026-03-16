from backend.models.schemas import RiskScore


def tier_from_score(score: int) -> str:
    if score >= 80:
        return "CRITICAL"
    if score >= 60:
        return "MALICIOUS"
    if score >= 30:
        return "SUSPICIOUS"
    return "SAFE"


def to_risk_score(score: int) -> RiskScore:
    bounded = max(0, min(100, int(score)))
    return RiskScore(score=bounded, tier=tier_from_score(bounded))

