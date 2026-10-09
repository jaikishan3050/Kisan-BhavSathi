"""Main application entry point for Kisan BhavSaathi Backend API."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.health import HealthResponse, get_health_status
from app.api.v1.router import api_v1_router
from app.core.config import get_settings
from app.core.logging import get_logger, setup_logging

logger = get_logger("app.main")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application startup and shutdown lifecycle events."""
    setup_logging()
    settings = get_settings()
    logger.info(
        "Starting %s v%s [Environment: %s, Debug: %s]",
        settings.PROJECT_NAME,
        settings.VERSION,
        settings.ENVIRONMENT,
        settings.DEBUG,
    )
    logger.info("Configured CORS Allowed Origins: %s", settings.CORS_ORIGINS)
    yield
    logger.info("Shutting down %s", settings.PROJECT_NAME)


def create_application() -> FastAPI:
    """Application factory initializing FastAPI with settings and middleware."""
    settings = get_settings()

    application = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description=settings.DESCRIPTION,
        debug=settings.DEBUG,
        lifespan=lifespan,
    )

    # Cross-Origin Resource Sharing (CORS) Middleware
    # Configured from Settings. In local development, common dev ports are allowed.
    # In production, explicit origins must be set via the CORS_ORIGINS environment variable.
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Root Health check endpoint: GET /health
    application.get(
        "/health",
        response_model=HealthResponse,
        tags=["Health"],
        summary="Root Health Check",
        description="Returns JSON health status confirming the application service is running.",
    )(get_health_status)

    # Root metadata endpoint: GET /
    @application.get(
        "/",
        tags=["Root"],
        summary="API Root Metadata",
        description="Returns basic platform metadata and documentation links.",
    )
    async def root_index() -> dict[str, str]:
        return {
            "name": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "environment": settings.ENVIRONMENT,
            "docs_url": "/docs",
            "health_url": "/health",
        }

    # Mount versioned API routes under /api/v1
    application.include_router(api_v1_router, prefix=settings.API_V1_PREFIX)

    return application


app = create_application()

if __name__ == "__main__":
    import uvicorn

    active_settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=active_settings.HOST,
        port=active_settings.PORT,
        reload=active_settings.DEBUG,
    )
