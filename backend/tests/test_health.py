"""Automated tests for health check, application startup, and basic routing."""

from fastapi.testclient import TestClient
from app.core.config import get_settings


def test_root_health_endpoint(client: TestClient) -> None:
    """Verify that GET /health returns HTTP 200 and standard health payload."""
    response = client.get("/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "healthy"
    assert "environment" in data
    assert "version" in data
    assert "app_name" in data


def test_api_v1_health_endpoint(client: TestClient) -> None:
    """Verify that GET /api/v1/health returns HTTP 200 and matches root health check."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "healthy"
    assert data["app_name"] == get_settings().PROJECT_NAME


def test_root_index_endpoint(client: TestClient) -> None:
    """Verify that GET / returns platform metadata and documentation endpoints."""
    response = client.get("/")
    assert response.status_code == 200

    data = response.json()
    assert "name" in data
    assert "version" in data
    assert data["docs_url"] == "/docs"
    assert data["health_url"] == "/health"


def test_cors_headers_on_health(client: TestClient) -> None:
    """Verify CORS middleware adds Access-Control-Allow-Origin for permitted origins."""
    test_origin = "http://localhost:3000"
    response = client.get("/health", headers={"Origin": test_origin})
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == test_origin


def test_cors_headers_rejected_origin(client: TestClient) -> None:
    """Verify CORS middleware does not reflect untrusted origins."""
    untrusted_origin = "http://malicious-site.example.com"
    response = client.get("/health", headers={"Origin": untrusted_origin})
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") is None
