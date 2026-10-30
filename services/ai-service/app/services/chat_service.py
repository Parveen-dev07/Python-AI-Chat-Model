import uuid

from app.core.config import Settings
from app.core.logging import get_logger
from app.database.postgres import PostgresConnector
from app.database.query_executor import QueryExecutor
from app.database.schema_inspector import SchemaInspector
from app.providers.base import AIProvider, ChatMessage, ToolDefinition
from app.providers.factory import ProviderConfigurationError, create_provider
from app.services.answer_service import (
    EMPTY_ANSWER,
    format_query_result,
    is_empty_result,
    is_schema_inventory_question,
    normalize_answer,
)
from app.tenants.resolver import TenantConfig

logger = get_logger(__name__)

RUN_QUERY_TOOL = ToolDefinition(
    name="run_readonly_sql",
    description=(
        "Execute a read-only SQL SELECT against the tenant database. "
        "Use only tables and columns from the provided schema. "
        "Return one SELECT statement without semicolons."
    ),
    parameters={
        "type": "object",
        "properties": {
            "sql": {
                "type": "string",
                "description": "A single PostgreSQL SELECT statement.",
            },
        },
        "required": ["sql"],
    },
)

SYSTEM_PROMPT = """You are a helpful assistant that answers questions using ONLY data
returned from database queries.

Response style (important):
- Plain text only (no Markdown: no asterisks, bold, headings, or backticks).
- Simple questions: one or two clear sentences.
- When the user asks for all items, a list, or details (e.g. all events, each record),
  use a structured list:
  1) Start with one line: total count and context.
  2) Number each item (1., 2., 3., …).
  3) For each item, use the same labeled lines (omit a line if data is missing):
     Title: …
     Description: …
     Visibility: …
     Location: …
     When: … (date and time range)
  4) Put a blank line between items. Do not cram multiple records into one paragraph.
  5) If rows look duplicated, say so briefly and still list each row from the query.
- Keep labels exactly as shown (Title:, Description:, etc.) so the layout stays consistent.

Rules:
- Use the run_readonly_sql tool when you need factual data from the database.
- Never invent prices, names, counts, or other values.
- If a query returns no rows, tell the user you could not find that information.
- Only query tables listed in the schema below.
- If the user asks only for table names or table counts in the allowed schemas, answer from
  the schema list below without calling run_readonly_sql.
- For enum columns, use exact enum values shown in the schema (case-sensitive).
- For text and email filters, always use single-quoted string literals, e.g. WHERE email = 'user@example.com'
  or WHERE email ILIKE '%user@example.com%'. Never compare email columns to unquoted numbers.
- Prefer schema-qualified table names (e.g. public.profiles).

Database schema:
{schema}
"""


class ChatService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._provider: AIProvider | None = None

    def _get_provider(self) -> AIProvider:
        if self._provider is None:
            self._provider = create_provider(self._settings)
        return self._provider

    def _connector_for(self, tenant: TenantConfig) -> PostgresConnector:
        return PostgresConnector(tenant.database_url)

    @staticmethod
    def _finalize_answer(text: str) -> str:
        return normalize_answer(text.strip())

    async def answer_question(self, tenant: TenantConfig, message: str) -> tuple[str, str]:
        request_id = str(uuid.uuid4())
        provider = self._get_provider()

        if not provider.supports_tool_calling():
            raise ProviderConfigurationError(
                f"Provider {self._settings.ai_provider} does not support tool calling"
            )

        connector = self._connector_for(tenant)
        connector.connect()
        try:
            inspector = SchemaInspector(connector, tenant.allowed_schemas)
            if is_schema_inventory_question(message):
                return (
                    self._finalize_answer(
                        inspector.table_inventory_answer(tenant.allowed_schemas)
                    ),
                    request_id,
                )

            schema_text = inspector.schema_summary()
            executor = QueryExecutor(
                connector,
                tenant.allowed_schemas,
                self._settings.db_query_timeout_seconds,
                self._settings.db_max_rows,
            )

            messages: list[ChatMessage] = [
                ChatMessage(
                    role="system",
                    content=SYSTEM_PROMPT.replace("{schema}", schema_text),
                ),
                ChatMessage(role="user", content=message),
            ]

            saw_empty_result = False
            saw_query_failure = False
            max_tool_rounds = 3
            for _ in range(max_tool_rounds):
                response = await provider.chat(messages, tools=[RUN_QUERY_TOOL])

                if not response.tool_calls:
                    if response.content and response.content.strip():
                        return self._finalize_answer(response.content), request_id
                    break

                if response.content:
                    messages.append(
                        ChatMessage(role="assistant", content=response.content),
                    )

                for tc in response.tool_calls:
                    if tc.name != RUN_QUERY_TOOL.name:
                        messages.append(
                            ChatMessage(
                                role="tool",
                                content='{"error": "Unsupported tool"}',
                                tool_call_id=tc.id,
                            )
                        )
                        continue

                    sql = tc.arguments.get("sql", "")
                    try:
                        result = executor.run(str(sql))
                        if is_empty_result(result):
                            saw_empty_result = True
                        messages.append(
                            ChatMessage(
                                role="tool",
                                content=format_query_result(result),
                                tool_call_id=tc.id,
                            )
                        )
                    except ValueError as exc:
                        logger.warning("Query rejected: %s", type(exc).__name__)
                        saw_query_failure = True
                        messages.append(
                            ChatMessage(
                                role="tool",
                                content=(
                                    '{"error": "validation_failed", "hint": '
                                    '"Use a single SELECT with quoted strings for emails/text."}'
                                ),
                                tool_call_id=tc.id,
                            )
                        )
                    except RuntimeError:
                        logger.warning("Query rejected or failed")
                        saw_query_failure = True
                        messages.append(
                            ChatMessage(
                                role="tool",
                                content=(
                                    '{"error": "execution_failed", "hint": '
                                    '"Fix SQL types; use quoted email strings on public.profiles.email."}'
                                ),
                                tool_call_id=tc.id,
                            )
                        )

            if saw_empty_result and not saw_query_failure:
                return EMPTY_ANSWER, request_id

            final = await provider.chat(messages, tools=None)
            if final.content and final.content.strip():
                return self._finalize_answer(final.content), request_id

            return EMPTY_ANSWER, request_id
        finally:
            connector.close()
