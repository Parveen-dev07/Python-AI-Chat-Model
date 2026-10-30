from enum import StrEnum
from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AIProviderName(StrEnum):
    OLLAMA = "ollama"
    OPENAI = "openai"
    GEMINI = "gemini"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = "development"
    log_level: str = "INFO"
    cors_origins: str = "http://localhost:5173"

    ai_provider: AIProviderName = AIProviderName.OLLAMA
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"
    ai_request_timeout_seconds: float = 300.0
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.5-flash"
    gemini_api_base: str = "https://generativelanguage.googleapis.com/v1beta"

    customer_database_url: str = ""
    db_query_timeout_seconds: int = 10
    db_max_rows: int = 100
    db_allowed_schemas: str = "public"

    default_widget_id: str = "demo-widget"
    default_tenant_id: str = "demo-tenant"
    widget_public_title: str = "Ask our database"
    widget_theme: str = "light"

    api_key: str = "dev-api-key-change-me"
    rate_limit_per_minute: int = 30

    @field_validator("customer_database_url")
    @classmethod
    def strip_database_url(cls, v: str) -> str:
        return v.strip()

    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    def allowed_schema_list(self) -> list[str]:
        return [s.strip() for s in self.db_allowed_schemas.split(",") if s.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
