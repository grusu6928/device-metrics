"""Tests for FastAPI receiver"""
import pytest
from datetime import datetime
from unittest.mock import patch, AsyncMock


def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_login(client):
    """Test authentication"""
    response = client.post(
        "/api/v1/auth/token",
        data={"username": "testuser", "password": "testpassword"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials(client):
    """Test authentication with invalid credentials"""
    response = client.post(
        "/api/v1/auth/token",
        data={"username": "testuser", "password": "wrongpassword"}
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_ingest_metrics(client, auth_token, sample_metric):
    """Test metric ingestion"""
    with patch('src.api.routes.metrics.kafka_producer.send_metric', new_callable=AsyncMock) as mock_send:
        mock_send.return_value = None
        
        response = client.post(
            "/api/v1/metrics",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "metrics": [sample_metric]
            }
        )
        
        assert response.status_code == 202
        data = response.json()
        assert data["ingested"] == 1
        assert data["failed"] == 0
        mock_send.assert_called_once()


def test_ingest_metrics_unauthorized(client, sample_metric):
    """Test metric ingestion without authentication"""
    response = client.post(
        "/api/v1/metrics",
        json={"metrics": [sample_metric]}
    )
    assert response.status_code == 401


def test_ingest_multiple_metrics(client, auth_token, sample_metric):
    """Test ingesting multiple metrics"""
    with patch('src.api.routes.metrics.kafka_producer.send_metric', new_callable=AsyncMock) as mock_send:
        mock_send.return_value = None
        
        metrics = [
            {**sample_metric, "value": 50.0},
            {**sample_metric, "value": 80.0, "metric_type": "memory_usage"},
        ]
        
        response = client.post(
            "/api/v1/metrics",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"metrics": metrics}
        )
        
        assert response.status_code == 202
        data = response.json()
        assert data["ingested"] == 2
        assert mock_send.call_count == 2
