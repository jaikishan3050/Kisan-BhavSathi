"""Central API v1 router.

Aggregates all domain routers for the version 1 API namespace.
"""

from fastapi import APIRouter
from app.api.v1.health import router as health_router

api_v1_router = APIRouter()

# Mount health router under /api/v1/health
api_v1_router.include_router(health_router, tags=["Health"])
