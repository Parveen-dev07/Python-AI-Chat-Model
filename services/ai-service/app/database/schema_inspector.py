import time
from dataclasses import dataclass

from app.database.base import DatabaseConnector, TableInfo


@dataclass
class CachedSchema:
    tables: list[TableInfo]
    fetched_at: float


class SchemaInspector:
    def __init__(
        self,
        connector: DatabaseConnector,
        allowed_schemas: list[str],
        cache_ttl_seconds: int = 300,
    ) -> None:
        self._connector = connector
        self._allowed_schemas = allowed_schemas
        self._cache_ttl = cache_ttl_seconds
        self._cache: CachedSchema | None = None

    def get_schema(self, *, force_refresh: bool = False) -> list[TableInfo]:
        now = time.time()
        if (
            not force_refresh
            and self._cache is not None
            and (now - self._cache.fetched_at) < self._cache_ttl
        ):
            return self._cache.tables

        tables = self._connector.inspect_schema(self._allowed_schemas)
        self._cache = CachedSchema(tables=tables, fetched_at=now)
        return tables

    def schema_summary(self) -> str:
        lines: list[str] = []
        for table in self.get_schema():
            col_parts: list[str] = []
            for c in table.columns:
                if c.enum_values:
                    values = ", ".join(c.enum_values)
                    col_parts.append(f"{c.name} (enum {c.udt_name}: {values})")
                else:
                    col_parts.append(f"{c.name} ({c.data_type})")
            lines.append(f"{table.schema}.{table.name}: {', '.join(col_parts)}")
        return "\n".join(lines) if lines else "(no tables in allowed schemas)"

    def table_inventory_answer(self, allowed_schema_labels: list[str]) -> str:
        tables = self.get_schema()
        names = sorted(f"{t.schema}.{t.name}" for t in tables)
        schemas = ", ".join(allowed_schema_labels) if allowed_schema_labels else "configured schemas"
        if not names:
            return f"There are 0 tables visible in {schemas}."
        bullet_list = "\n".join(f"- {name}" for name in names)
        return (
            f"There are {len(names)} tables in {schemas}:\n{bullet_list}\n\n"
            "Column details were loaded from database metadata (no row data scanned)."
        )
