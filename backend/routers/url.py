from fastapi import APIRouter, Request

from backend.models.schemas import URLAnalyzeRequest, URLAnalyzeResponse
from backend.services.url_service import URLService


router = APIRouter()


@router.post("/analyze", response_model=URLAnalyzeResponse)
async def analyze_urls(request: Request, body: URLAnalyzeRequest) -> URLAnalyzeResponse:
    service = URLService(request.app.state.xgboost_model)
    results = await service.analyze_batch(body.urls[:50])
    return URLAnalyzeResponse(results=results)

