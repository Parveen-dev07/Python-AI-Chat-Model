import pytest

from app.core.config import Settings
from app.tenants.resolver import TenantNotFoundError, TenantResolver


def test_resolve_known_widget() -> None:
    settings = Settings(
        default_widget_id="demo-widget",
        customer_database_url="postgresql+psycopg://u:p@localhost/db",
        db_allowed_schemas="public,auth", 
    )
    tenant = TenantResolver(settings).resolve_by_widget_id("demo-widget")
    assert tenant.tenant_id == settings.default_tenant_id
    assert "auth" in tenant.allowed_schemas


def test_unknown_widget_raises() -> None:
    settings = Settings(default_widget_id="demo-widget", customer_database_url="postgresql://x")
    with pytest.raises(TenantNotFoundError):
        TenantResolver(settings).resolve_by_widget_id("other")
