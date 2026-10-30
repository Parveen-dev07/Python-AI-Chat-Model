from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import verify_api_key
from app.core.config import Settings, get_settings
from app.schemas.chat import WidgetConfigResponse
from app.tenants.resolver import TenantNotFoundError, TenantResolver

router = APIRouter(prefix="/api/v1", tags=["widget"])


@router.get("/widget/config", response_model=WidgetConfigResponse)
async def widget_config(
    widget_id: str,
    settings: Settings = Depends(get_settings),
    _: None = Depends(verify_api_key),
) -> WidgetConfigResponse:
    resolver = TenantResolver(settings)
    try:
        tenant = resolver.resolve_by_widget_id(widget_id)
    except TenantNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Widget not found",
        ) from None

    return WidgetConfigResponse(
        widget_id=tenant.widget_id,
        title=tenant.widget_title,
        theme=tenant.widget_theme,
    )
