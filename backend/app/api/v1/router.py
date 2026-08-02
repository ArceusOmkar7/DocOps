"""Aggregates all v1 API routers."""

from fastapi import APIRouter

from .endpoints import clients, documents, extraction, health, ocr, organizations, workflows

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(ocr.router)
api_router.include_router(extraction.router)
api_router.include_router(organizations.router)
api_router.include_router(clients.router)
api_router.include_router(workflows.router)
api_router.include_router(documents.router)
