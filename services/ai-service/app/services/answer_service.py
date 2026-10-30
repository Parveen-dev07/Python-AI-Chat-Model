import json
import re

from app.database.base import QueryResult

EMPTY_ANSWER = (
    "I couldn't find that information in the database. "
    "Try rephrasing your question or check that the data exists."
)


def normalize_answer(text: str) -> str:
    """Plain text for the widget (no Markdown — UI does not render it)."""
    cleaned = text.strip()
    if not cleaned:
        return cleaned
    cleaned = re.sub(r"\*\*(.+?)\*\*", r"\1", cleaned)
    cleaned = re.sub(r"__(.+?)__", r"\1", cleaned)
    cleaned = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"\1", cleaned)
    cleaned = re.sub(r"`([^`]+)`", r"\1", cleaned)
    cleaned = re.sub(r"^#{1,6}\s+", "", cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def format_query_result(result: QueryResult) -> str:
    if not result.rows:
        return json.dumps({"rows": [], "message": "no rows"})
    data = {
        "columns": result.columns,
        "rows": result.rows,
        "truncated": result.truncated,
    }
    return json.dumps(data, default=str)


def is_empty_result(result: QueryResult) -> bool:
    return len(result.rows) == 0


def is_schema_inventory_question(message: str) -> bool:
    lower = message.lower()
    if "table" not in lower and "tables" not in lower:
        return False
    inventory_hints = (
        "list",
        "name",
        "names",
        "count",
        "how many",
        "all ",
        "schema",
        "database",
    )
    return any(hint in lower for hint in inventory_hints)
