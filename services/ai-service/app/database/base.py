from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ColumnInfo:
    name: str
    data_type: str
    nullable: bool
    udt_name: str | None = None
    enum_values: list[str] | None = None


@dataclass
class TableInfo:
    schema: str
    name: str
    columns: list[ColumnInfo]


@dataclass
class QueryResult:
    columns: list[str]
    rows: list[list[object]]
    truncated: bool = False


class DatabaseConnector(ABC):
    @abstractmethod
    def connect(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def close(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def ping(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def inspect_schema(self, allowed_schemas: list[str]) -> list[TableInfo]:
        raise NotImplementedError

    @abstractmethod
    def execute_readonly(
        self,
        sql: str,
        *,
        timeout_seconds: int,
        max_rows: int,
    ) -> QueryResult:
        raise NotImplementedError
