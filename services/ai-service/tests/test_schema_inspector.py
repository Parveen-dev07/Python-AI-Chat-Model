from unittest.mock import MagicMock

from app.database.base import ColumnInfo, TableInfo
from app.database.schema_inspector import SchemaInspector


def test_schema_summary_includes_enum_values() -> None:
    connector = MagicMock()
    inspector = SchemaInspector(connector, ["public"])
    inspector.get_schema = MagicMock(  # type: ignore[method-assign]
        return_value=[
            TableInfo(
                schema="public",
                name="profiles",
                columns=[
                    ColumnInfo(
                        name="role",
                        data_type="USER-DEFINED",
                        nullable=False,
                        udt_name="UserRole",
                        enum_values=["ADMIN", "USER"],
                    ),
                    ColumnInfo(name="name", data_type="text", nullable=True),
                ],
            )
        ]
    )
    summary = inspector.schema_summary()
    assert "enum UserRole: ADMIN, USER" in summary
    assert "public.profiles" in summary
