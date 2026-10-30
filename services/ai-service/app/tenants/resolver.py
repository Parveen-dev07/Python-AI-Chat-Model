from dataclasses import dataclass

from app.core.config import Settings


@dataclass(frozen=True)
class TenantConfig:
    tenant_id: str
    widget_id: str
    database_url: str
    allowed_schemas: list[str]
    widget_title: str
    widget_theme: str


class TenantNotFoundError(LookupError):
    pass


class TenantResolver:
    """Resolves tenant from widget_id using server-side configuration only."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def resolve_by_widget_id(self, widget_id: str) -> TenantConfig:
        if widget_id != self._settings.default_widget_id:
            raise TenantNotFoundError(f"Unknown widget: {widget_id}")

        if not self._settings.customer_database_url:
            raise TenantNotFoundError("No database configured for this tenant")

        return TenantConfig(
            tenant_id=self._settings.default_tenant_id,
            widget_id=widget_id,
            database_url=self._settings.customer_database_url,
            allowed_schemas=self._settings.allowed_schema_list(),
            widget_title=self._settings.widget_public_title,
            widget_theme=self._settings.widget_theme,
        )
