from contextlib import contextmanager

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from app.core.logging import get_logger
from app.database.base import ColumnInfo, DatabaseConnector, QueryResult, TableInfo

logger = get_logger(__name__)


class PostgresConnector(DatabaseConnector):
    def __init__(self, database_url: str) -> None:
        self._database_url = database_url
        self._engine: Engine | None = None

    def connect(self) -> None:
        if self._engine is None:
            self._engine = create_engine(
                self._database_url,
                pool_pre_ping=True,
                pool_size=5,
                max_overflow=2,
            )

    def close(self) -> None:
        if self._engine is not None:
            self._engine.dispose()
            self._engine = None

    @contextmanager
    def _connection(self):
        self.connect()
        assert self._engine is not None
        with self._engine.connect() as conn:
            yield conn

    def ping(self) -> None:
        with self._connection() as conn:
            conn.execute(text("SELECT 1"))

    def inspect_schema(self, allowed_schemas: list[str]) -> list[TableInfo]:
        if not allowed_schemas:
            return []

        placeholders = ", ".join(f":s{i}" for i in range(len(allowed_schemas)))
        params = {f"s{i}": s for i, s in enumerate(allowed_schemas)}

        sql = f"""
            SELECT table_schema, table_name, column_name, data_type, udt_name, is_nullable
            FROM information_schema.columns
            WHERE table_schema IN ({placeholders})
              AND table_name NOT LIKE 'pg_%'
            ORDER BY table_schema, table_name, ordinal_position
        """

        enum_sql = f"""
            SELECT n.nspname AS type_schema, t.typname AS type_name, e.enumlabel
            FROM pg_enum e
            JOIN pg_type t ON e.enumtypid = t.oid
            JOIN pg_namespace n ON t.typnamespace = n.oid
            WHERE n.nspname IN ({placeholders})
            ORDER BY t.typname, e.enumsortorder
        """

        tables: dict[tuple[str, str], list[ColumnInfo]] = {}
        enum_labels: dict[str, list[str]] = {}
        with self._connection() as conn:
            for row in conn.execute(text(enum_sql), params):
                mapping = row._mapping
                type_name = mapping["type_name"]
                enum_labels.setdefault(type_name, []).append(mapping["enumlabel"])

            result = conn.execute(text(sql), params)
            for row in result:
                mapping = row._mapping
                key = (mapping["table_schema"], mapping["table_name"])
                if key not in tables:
                    tables[key] = []
                udt = mapping["udt_name"]
                enums = enum_labels.get(udt) if mapping["data_type"] == "USER-DEFINED" else None
                tables[key].append(
                    ColumnInfo(
                        name=mapping["column_name"],
                        data_type=mapping["data_type"],
                        nullable=mapping["is_nullable"] == "YES",
                        udt_name=udt,
                        enum_values=enums,
                    )
                )

        return [
            TableInfo(schema=schema, name=name, columns=columns)
            for (schema, name), columns in sorted(tables.items())
        ]

    def execute_readonly(
        self,
        sql: str,
        *,
        timeout_seconds: int,
        max_rows: int,
    ) -> QueryResult:
        # Driver-level SQL: avoid SQLAlchemy :bind parsing on model-generated SQL.
        # Double "%" so psycopg3 does not treat ILIKE '%foo%' as pyformat placeholders.
        escaped = sql.replace("%", "%%")
        row_cap = int(max_rows) + 1
        limited_sql = f"SELECT * FROM ({escaped}) AS _q LIMIT {row_cap}"
        with self._connection() as conn:
            conn.exec_driver_sql(f"SET LOCAL statement_timeout = '{int(timeout_seconds)}s'")
            result = conn.exec_driver_sql(limited_sql)
            columns = list(result.keys())
            raw_rows = result.fetchall()
            truncated = len(raw_rows) > max_rows
            rows = [list(r) for r in raw_rows[:max_rows]]
            return QueryResult(columns=columns, rows=rows, truncated=truncated)
