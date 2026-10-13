from fastapi import APIRouter
from backend.api import health, leads, ui
api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(leads.router, prefix="/api/leads", tags=["leads"])
api_router.include_router(ui.router, tags=["ui"])
