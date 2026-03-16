from fastapi import APIRouter, Request

from backend.models.schemas import PromptCheckRequest, PromptCheckResponse, PromptSessionLogResponse
from backend.services.prompt_service import PromptService


router = APIRouter()
service = PromptService()


@router.post("/check", response_model=PromptCheckResponse)
async def check_prompt(request: Request, body: PromptCheckRequest) -> PromptCheckResponse:
    response = await service.check(body.message, body.session_id, body.system_prompt)
    service.log_incident(request.app.state.prompt_sessions, body.session_id, response, body.message)
    return response


@router.get("/session/{session_id}/log", response_model=PromptSessionLogResponse)
async def get_session_log(request: Request, session_id: str) -> PromptSessionLogResponse:
    incidents = request.app.state.prompt_sessions.get(session_id, [])
    total_safe = sum(1 for incident in incidents if incident.safe)
    total_blocked = sum(1 for incident in incidents if not incident.safe)
    return PromptSessionLogResponse(
        incidents=incidents,
        total_blocked=total_blocked,
        total_safe=total_safe,
    )

