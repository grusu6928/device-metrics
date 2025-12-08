"""Integration tests for API endpoints"""

import pytest
from fastapi.testclient import TestClient

from src.api.main import app


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


def test_health_endpoint(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_api_documentation(client):
    """Test API documentation endpoints"""
    response = client.get("/docs")
    assert response.status_code == 200

    response = client.get("/redoc")
    assert response.status_code == 200


def test_metrics_endpoint_requires_auth(client):
    """Test that metrics endpoint requires authentication"""
    response = client.get("/api/v1/metrics/health/device-001")
    assert response.status_code == 401
