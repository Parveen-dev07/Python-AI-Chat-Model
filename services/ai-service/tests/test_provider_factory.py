import pytest

from app.core.config import AIProviderName, Settings
from app.providers.factory import ProviderConfigurationError, create_provider
from app.providers.gemini import GeminiProvider
from app.providers.ollama import OllamaProvider
from app.providers.openai import OpenAIProvider


def test_create_ollama_provider() -> None:
    settings = Settings(
        ai_provider=AIProviderName.OLLAMA,
        ollama_base_url="http://localhost:11434",
        ollama_model="llama3.2",
    )
    provider = create_provider(settings)
    assert isinstance(provider, OllamaProvider)
    assert provider.supports_tool_calling()


def test_create_openai_without_key_raises() -> None:
    settings = Settings(ai_provider=AIProviderName.OPENAI, openai_api_key="")
    with pytest.raises(ProviderConfigurationError):
        create_provider(settings)


def test_create_openai_with_key() -> None:
    settings = Settings(
        ai_provider=AIProviderName.OPENAI,
        openai_api_key="sk-test",
        openai_model="gpt-4o-mini",
    )
    provider = create_provider(settings)
    assert isinstance(provider, OpenAIProvider)


def test_create_gemini_without_key_raises() -> None:
    settings = Settings(ai_provider=AIProviderName.GEMINI, gemini_api_key="")
    with pytest.raises(ProviderConfigurationError):
        create_provider(settings)


def test_create_gemini_with_key() -> None:
    settings = Settings(
        ai_provider=AIProviderName.GEMINI,
        gemini_api_key="AIza-test",
        gemini_model="gemini-2.5-flash",
    )
    provider = create_provider(settings)
    assert isinstance(provider, GeminiProvider)
