"""FastAPI application entrypoint."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from .api.deps import get_ocr_service
from .api.v1.router import api_router
from .core.config import get_settings
from .core.logging import setup_logging

setup_logging()

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings.ensure_dirs()
    yield
    get_ocr_service().close()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        lifespan=lifespan,
        debug=settings.debug,
    )

    @app.get("/healthz", tags=["system"])
    def healthz() -> dict:
        return {
            "status": "ok",
            "service": settings.app_name,
            "version": settings.app_version,
        }

    app.include_router(api_router, prefix=settings.api_v1_prefix)
    return app


app = create_app()
