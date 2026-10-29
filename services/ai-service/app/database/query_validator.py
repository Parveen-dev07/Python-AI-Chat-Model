import re

import sqlparse
from sqlparse.sql import Identifier, IdentifierList, Parenthesis
from sqlparse.tokens import DML, Keyword

FORBIDDEN_KEYWORDS = frozenset(
    {
        "insert",
        "update",
        "delete",
        "drop",
        "create",
        "alter",
        "truncate",
        "grant",
        "revoke",
        "copy",
        "execute",
        "call",
        "merge",
        "replace",
        "into",
    }
)

SYSTEM_SCHEMAS = frozenset(
    {
        "pg_catalog",
        "information_schema",
        "pg_toast",
    }
)


class QueryValidationError(ValueError):
    pass


def _flatten_identifiers(token) -> list[str]:
    names: list[str] = []
    if isinstance(token, Identifier):
        names.append(token.get_real_name() or str(token))
    elif isinstance(token, IdentifierList):
        for item in token.get_identifiers():
            names.extend(_flatten_identifiers(item))
    elif isinstance(token, Parenthesis):
        pass
    return names


def _collect_table_refs(statement) -> set[str]:
    refs: set[str] = set()
    from_seen = False
    for token in statement.tokens:
        if token.ttype is Keyword and token.value.upper() == "FROM":
            from_seen = True
            continue
        if from_seen and not token.is_whitespace:
            stop_words = ("WHERE", "JOIN", "GROUP", "ORDER", "LIMIT")
            if token.ttype is Keyword and token.value.upper() in stop_words:
                from_seen = False
            else:
                refs.update(_flatten_identifiers(token))
    return refs


def validate_readonly_select(
    sql: str,
    *,
    allowed_schemas: list[str],
) -> str:
    stripped = sql.strip()
    if not stripped:
        raise QueryValidationError("Query is empty")

    if ";" in stripped.rstrip(";"):
        raise QueryValidationError("Multiple statements are not allowed")

    parsed = sqlparse.parse(stripped)
    if len(parsed) != 1:
        raise QueryValidationError("Exactly one SQL statement is required")

    statement = parsed[0]
    first = statement.token_first(skip_cm=True)
    if first is None or first.ttype is not DML or first.value.upper() != "SELECT":
        raise QueryValidationError("Only SELECT queries are allowed")

    upper = stripped.upper()
    for kw in FORBIDDEN_KEYWORDS:
        if re.search(rf"\b{kw.upper()}\b", upper):
            if kw == "into" and "SELECT" in upper:
                raise QueryValidationError("SELECT INTO is not allowed")
            if kw != "into":
                raise QueryValidationError(f"Forbidden keyword: {kw}")

    allowed = {s.lower() for s in allowed_schemas}
    for ref in _collect_table_refs(statement):
        ref_lower = ref.lower().strip('"')
        if "." in ref_lower:
            schema, _table = ref_lower.split(".", 1)
            if schema in SYSTEM_SCHEMAS:
                raise QueryValidationError(f"System schema not allowed: {schema}")
            if schema not in allowed:
                raise QueryValidationError(f"Schema not in allowlist: {schema}")
        else:
            if "public" not in allowed and len(allowed) == 1:
                pass
            elif len(allowed) == 1 and "public" in allowed:
                pass

    return stripped.rstrip(";")
