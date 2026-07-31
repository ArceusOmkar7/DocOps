"""Aggregates all v1 API routers."""

from fastapi import APIRouter

from .endpoints import health, ocr

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(ocr.router)
