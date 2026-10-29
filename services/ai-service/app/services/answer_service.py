import json

from app.database.base import QueryResult

EMPTY_ANSWER = (
    "I couldn't find that information in the database. "
    "Try rephrasing your question or check that the data exists."
)


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
