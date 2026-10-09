"""Pytest configuration and test fixtures."""

from typing import Generator
import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture(scope="session")
def client() -> Generator[TestClient, None, None]:
    """Provide a TestClient instance managing app lifespan events."""
    with TestClient(app) as test_client:
        yield test_client
