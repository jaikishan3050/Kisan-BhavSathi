"""Health check endpoint definition."""

from fastapi import APIRouter
from pydantic import BaseModel, Field
from app.core.config import get_settings

router = APIRouter()


class HealthResponse(BaseModel):
    """Schema for application health check response."""

    status: str = Field(default="healthy", description="Current operational health status")
    environment: str = Field(description="Active environment mode")
    version: str = Field(description="Application semantic version")
    app_name: str = Field(description="Application display name")


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Service Health Check",
    description="Returns standard JSON status confirming application availability.",
)
async def get_health_status() -> HealthResponse:
    """Return application availability status and active metadata."""
    settings = get_settings()
    return HealthResponse(
        status="healthy",
        environment=settings.ENVIRONMENT,
        version=settings.VERSION,
        app_name=settings.PROJECT_NAME,
    )
