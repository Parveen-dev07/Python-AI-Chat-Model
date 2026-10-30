from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import chat, health, widget
from app.core.config import get_settings
from app.core.logging import setup_logging


@asynccontextmanager
async def lifespan(_app: FastAPI):
    settings = get_settings()
    setup_logging(settings)
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI(
        title="Reusable AI Chat Platform",
        description="Database-backed AI chat API",
        version="1.0.0",
        lifespan=lifespan,
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list(),
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )

    application.include_router(health.router)
    application.include_router(health.v1_router)
    application.include_router(chat.router)
    application.include_router(widget.router)

    @application.get("/")
    def root() -> dict[str, str]:
        return {"message": "AI Chat Backend is running"}

    return application


app = create_app()
