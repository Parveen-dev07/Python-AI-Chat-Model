from app.core.config import AIProviderName, Settings
from app.providers.base import AIProvider
from app.providers.gemini import GeminiProvider
from app.providers.openai import OpenAIProvider


class ProviderConfigurationError(RuntimeError):
    pass


def create_provider(settings: Settings) -> AIProvider:
    if settings.ai_provider == AIProviderName.OPENAI:
        if not settings.openai_api_key.strip():
            raise ProviderConfigurationError(
                "AI_PROVIDER=openai but OPENAI_API_KEY is empty"
            )
        return OpenAIProvider(
            api_key=settings.openai_api_key,
            model=settings.openai_model,
            timeout=settings.ai_request_timeout_seconds,
        )
    if settings.ai_provider == AIProviderName.GEMINI:
        if not settings.gemini_api_key.strip():
            raise ProviderConfigurationError(
                "AI_PROVIDER=gemini but GEMINI_API_KEY is empty"
            )
        return GeminiProvider(
            api_key=settings.gemini_api_key,
            model=settings.gemini_model,
            api_base=settings.gemini_api_base,
            timeout=settings.ai_request_timeout_seconds,
        )
    raise ProviderConfigurationError(f"Unknown AI provider: {settings.ai_provider}")
