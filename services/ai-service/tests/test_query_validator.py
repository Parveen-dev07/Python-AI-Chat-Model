import pytest

from app.database.query_validator import QueryValidationError, validate_readonly_select


def test_accepts_simple_select() -> None:
    sql = validate_readonly_select(
        "SELECT id, name FROM public.products WHERE name = 'Demo Burger'",
        allowed_schemas=["public"],
    )
    assert sql.startswith("SELECT")


@pytest.mark.parametrize(
    "bad_sql",
    [
        "DELETE FROM public.products",
        "INSERT INTO public.products VALUES (1)",
        "SELECT 1; DROP TABLE users",
        "UPDATE public.products SET price = 0",
    ],
)
def test_rejects_unsafe_sql(bad_sql: str) -> None:
    with pytest.raises(QueryValidationError):
        validate_readonly_select(bad_sql, allowed_schemas=["public"])


def test_rejects_empty() -> None:
    with pytest.raises(QueryValidationError):
        validate_readonly_select("   ", allowed_schemas=["public"])
