import os

import pytest
from fastapi.testclient import TestClient

# Test env must override any local .env before settings are cached.
os.environ["AI_PROVIDER"] = "ollama"
os.environ["CUSTOMER_DATABASE_URL"] = "postgresql+psycopg://u:p@127.0.0.1:5432/test"
os.environ["API_KEY"] = "test-api-key"
os.environ["DEFAULT_WIDGET_ID"] = "demo-widget"

from app.core.config import get_settings  # noqa: E402
from app.main import create_app  # noqa: E402

get_settings.cache_clear()


@pytest.fixture
def client() -> TestClient:
    return TestClient(create_app())
