from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    widget_id: str = Field(..., min_length=1, max_length=128)
    message: str = Field(..., min_length=1, max_length=4000)


class ChatResponse(BaseModel):
    answer: str
    request_id: str


class HealthResponse(BaseModel):
    status: str
    message: str | None = None


class DatabaseHealthResponse(BaseModel):
    status: str
    database: str


class AIHealthResponse(BaseModel):
    status: str
    provider: str
    message: str


class WidgetConfigResponse(BaseModel):
    widget_id: str
    title: str
    theme: str
