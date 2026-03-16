from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings
from backend.models.ml.xgboost_model import load_xgboost
from backend.models.schemas import HealthResponse
from backend.routers import gmail, prompt, url
from backend.utils.litellm_client import healthcheck as litellm_healthcheck


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.xgboost_model = load_xgboost()
    app.state.prompt_sessions = {}
    yield


app = FastAPI(title="Kobra API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(url.router, prefix="/api/url", tags=["url"])
app.include_router(prompt.router, prefix="/api/prompt", tags=["prompt"])
app.include_router(gmail.router, prefix="/api/gmail", tags=["gmail"])


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        service="kobra-api",
        litellm_reachable=await litellm_healthcheck(),
    )

