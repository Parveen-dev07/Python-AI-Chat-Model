from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import check_rate_limit, verify_api_key
from app.core.config import Settings, get_settings
from app.core.logging import get_logger
from app.providers.errors import AIProviderError, AIProviderTimeoutError
from app.providers.factory import ProviderConfigurationError
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService
from app.tenants.resolver import TenantNotFoundError, TenantResolver

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(
    body: ChatRequest,
    settings: Settings = Depends(get_settings),
    _: None = Depends(verify_api_key),
    __: None = Depends(check_rate_limit),
) -> ChatResponse:

    resolver = TenantResolver(settings)
    try:
        tenant = resolver.resolve_by_widget_id(body.widget_id)
    except TenantNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Widget is not authorized",
        ) from None

    service = ChatService(settings)
    try:
        answer, request_id = await service.answer_question(tenant, body.message)
    except ProviderConfigurationError as exc:
        logger.error("Provider misconfiguration: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI provider is not configured correctly",
        ) from exc
    except AIProviderTimeoutError as exc:
        logger.warning("AI provider timeout: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=str(exc),
        ) from exc
    except AIProviderError as exc:
        logger.warning("AI provider error: %s", exc)
        detail = "AI provider is temporarily unavailable"
        if settings.app_env == "development":
            detail = str(exc)[:500]
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail,
        ) from exc
    except Exception:
        logger.exception("Chat request failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to process your question",
        ) from None

    return ChatResponse(answer=answer, request_id=request_id)
