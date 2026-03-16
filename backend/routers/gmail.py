from urllib.parse import quote

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import RedirectResponse

from backend.config import settings
from backend.models.schemas import GmailOAuthStartResponse, GmailScanRequest, GmailScanResponse, GmailScanSummary, EmailResult
from backend.services.gmail_service import GmailService
from backend.services.phishing_service import PhishingService
from backend.services.url_service import URLService


router = APIRouter()
gmail_service = GmailService()
phishing_service = PhishingService()


@router.get("/oauth/start", response_model=GmailOAuthStartResponse)
async def gmail_oauth_start() -> GmailOAuthStartResponse:
    if not settings.gmail_client_id:
        raise HTTPException(status_code=503, detail="Gmail OAuth is not configured.")
    return GmailOAuthStartResponse(authorization_url=gmail_service.build_authorization_url())


@router.get("/oauth/callback")
async def gmail_oauth_callback(code: str = Query(...)) -> RedirectResponse:
    access_token = await gmail_service.exchange_code(code)
    destination = f"{settings.frontend_url}/email?access_token={quote(access_token)}"
    return RedirectResponse(destination)


@router.post("/scan", response_model=GmailScanResponse)
async def scan_gmail(request: Request, body: GmailScanRequest) -> GmailScanResponse:
    try:
        emails = await gmail_service.fetch_emails(body.access_token, max_results=20)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Failed to fetch Gmail messages: {exc}") from exc

    url_service = URLService(request.app.state.xgboost_model)
    results: list[EmailResult] = []
    for email in emails:
        url_results = await url_service.analyze_batch(email["urls"]) if email["urls"] else []
        phishing = phishing_service.analyze_email(email, [item.risk_score.score for item in url_results])
        results.append(
            EmailResult(
                id=email["id"],
                subject=email["subject"],
                sender=email["sender"],
                sender_domain=email["sender_domain"],
                received_at=email["received_at"],
                snippet=email["snippet"],
                risk_score=phishing["risk_score"],
                explanation_card=phishing["explanation_card"],
                urls_found=len(email["urls"]),
                urls_malicious=sum(1 for item in url_results if item.risk_score.score >= 60),
                top_urls=email["urls"],
            )
        )
    results.sort(key=lambda item: item.risk_score.score, reverse=True)
    tiers = [item.risk_score.tier for item in results]
    return GmailScanResponse(
        emails=results,
        scan_summary=GmailScanSummary(
            total=len(results),
            safe=tiers.count("SAFE"),
            suspicious=tiers.count("SUSPICIOUS"),
            malicious=tiers.count("MALICIOUS"),
            critical=tiers.count("CRITICAL"),
        ),
    )

