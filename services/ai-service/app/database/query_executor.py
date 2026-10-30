from app.core.logging import get_logger
from app.database.base import DatabaseConnector, QueryResult
from app.database.query_validator import QueryValidationError, validate_readonly_select

logger = get_logger(__name__)


class QueryExecutor:
    def __init__(
        self,
        connector: DatabaseConnector,
        allowed_schemas: list[str],
        timeout_seconds: int,
        max_rows: int,
    ) -> None:
        self._connector = connector
        self._allowed_schemas = allowed_schemas
        self._timeout_seconds = timeout_seconds
        self._max_rows = max_rows

    def run(self, sql: str) -> QueryResult:
        safe_sql = validate_readonly_select(sql, allowed_schemas=self._allowed_schemas)
        logger.info("Executing validated read-only query")
        try:
            return self._connector.execute_readonly(
                safe_sql,
                timeout_seconds=self._timeout_seconds,
                max_rows=self._max_rows,
            )
        except QueryValidationError:
            raise
        except Exception as exc:
            logger.exception("Query execution failed")
            raise RuntimeError("Database query failed") from exc
