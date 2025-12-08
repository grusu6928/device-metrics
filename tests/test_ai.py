"""Tests for AI components"""

from unittest.mock import MagicMock, Mock, patch

import numpy as np
import pytest

from src.services.anomaly_detector import AnomalyDetector
from src.services.embeddings import EmbeddingService
from src.services.health_summarizer import HealthSummarizer
from src.services.remediation_engine import RemediationEngine


def test_embedding_service():
    """Test embedding generation"""
    with patch("src.services.embeddings.QdrantClient") as mock_qdrant:
        # Mock Qdrant client
        mock_client = MagicMock()
        mock_client.get_collections.return_value.collections = []
        mock_qdrant.return_value = mock_client

        service = EmbeddingService()

        # Test embedding generation
        embedding = service.generate_embedding("device-001", "cpu_usage", 75.5, {"cpu_cores": 4})

        assert isinstance(embedding, np.ndarray)
        assert len(embedding) > 0


def test_anomaly_detector():
    """Test anomaly detection"""
    with patch("src.services.embeddings.QdrantClient") as mock_qdrant:
        mock_client = MagicMock()
        mock_client.get_collections.return_value.collections = []
        mock_client.search.return_value = []
        mock_qdrant.return_value = mock_client

        embedding_service = EmbeddingService()
        detector = AnomalyDetector(embedding_service)

        # Test anomaly detection
        result = detector.detect_anomaly("device-001", "cpu_usage", 95.0, {})  # High value

        assert "is_anomaly" in result
        assert "anomaly_score" in result
        assert "classification" in result


def test_health_summarizer():
    """Test health summarization"""
    summarizer = HealthSummarizer()

    # Mock database session
    mock_db = Mock()
    mock_query = Mock()
    mock_filter = Mock()

    mock_db.query.return_value = mock_query
    mock_query.filter.return_value = mock_filter
    mock_filter.order_by.return_value.limit.return_value.all.return_value = []

    summary = summarizer.summarize_device_health("device-001", mock_db)

    assert "summary" in summary
    assert "overall_health" in summary
    assert "key_metrics" in summary


def test_remediation_engine():
    """Test remediation generation"""
    engine = RemediationEngine()

    # Mock anomaly and metric
    mock_anomaly = Mock()
    mock_anomaly.classification = "value_spike"
    mock_anomaly.anomaly_score = 0.9

    mock_metric = Mock()
    mock_metric.device_id = "device-001"
    mock_metric.metric_type = "cpu_usage"
    mock_metric.value = 95.0
    mock_metric.unit = "percent"
    mock_metric.metric_metadata = {}

    remediation = engine.generate_remediation(mock_anomaly, mock_metric)

    assert "suggestion" in remediation
    assert "reasoning" in remediation
    assert "priority" in remediation
    assert remediation["priority"] in ["high", "medium", "low"]
