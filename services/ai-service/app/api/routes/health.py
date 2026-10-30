from fastapi import APIRouter, HTTPException, status

from app.core.config import get_settings
from app.core.logging import get_logger
from app.database.postgres import PostgresConnector
from app.providers.factory import ProviderConfigurationError, create_provider
from app.schemas.chat import AIHealthResponse, DatabaseHealthResponse, HealthResponse

logger = get_logger(__name__)

router = APIRouter(tags=["health"])
v1_router = APIRouter(prefix="/api/v1", tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok", message="Backend is healthy")


@router.get("/health/database", response_model=DatabaseHealthResponse)
async def database_health() -> DatabaseHealthResponse:
    settings = get_settings()
    if not settings.customer_database_url:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is not configured",
        )
    connector = PostgresConnector(settings.customer_database_url)
    try:
        connector.connect()
        connector.ping()
        return DatabaseHealthResponse(status="ok", database="PostgreSQL connected")
    except Exception as exc:
        logger.exception("Database health check failed")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection failed",
        ) from exc
    finally:
        connector.close()


@v1_router.get("/health/ai", response_model=AIHealthResponse)
async def ai_health() -> AIHealthResponse:
    settings = get_settings()
    try:
        provider = create_provider(settings)
    except ProviderConfigurationError as exc:
        return AIHealthResponse(
            status="error",
            provider=settings.ai_provider.value,
            message=str(exc),
        )

    if not provider.supports_tool_calling():
        return AIHealthResponse(
            status="error",
            provider=settings.ai_provider.value,
            message="Configured provider does not support tool calling",
        )

    ready, message = await provider.check_ready()
    return AIHealthResponse(
        status="ok" if ready else "degraded",
        provider=settings.ai_provider.value,
        message=message,
    )
