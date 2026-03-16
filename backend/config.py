from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    gemini_api_key: str = ""
    virustotal_api_key: str = ""
    google_safe_browsing_api_key: str = ""
    gmail_client_id: str = ""
    gmail_client_secret: str = ""
    gmail_redirect_uri: str = "http://localhost:8000/api/gmail/oauth/callback"
    litellm_master_key: str = "kobra-secret-2026"
    litellm_proxy_url: str = "http://localhost:4000"
    frontend_url: str = "http://localhost:3000"
    backend_public_url: str = "http://localhost:8000"
    phishing_model_name: str = "cybersectony/phishing-email-detection-distilbert_v2"
    prompt_model: str = "kobra-model"

    model_config = SettingsConfigDict(env_file="backend/.env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

