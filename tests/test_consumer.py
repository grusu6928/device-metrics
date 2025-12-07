"""Tests for Kafka consumer"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from src.consumer.consumer import MetricsConsumer


@pytest.mark.asyncio
async def test_process_message():
    """Test message processing"""
    with patch('src.consumer.consumer.SessionLocal') as mock_session, \
         patch('src.services.embeddings.QdrantClient') as mock_qdrant:
        
        # Mock database
        mock_db = Mock()
        mock_db.add = Mock()
        mock_db.commit = Mock()
        mock_db.refresh = Mock()
        mock_session.return_value = mock_db
        
        # Mock Qdrant
        mock_client = MagicMock()
        mock_client.get_collections.return_value.collections = []
        mock_qdrant.return_value = mock_client
        
        consumer = MetricsConsumer()
        
        metric_data = {
            "device_id": "device-001",
            "metric_type": "cpu_usage",
            "value": 75.5,
            "unit": "percent",
            "timestamp": "2024-01-01T12:00:00Z",
            "metadata": {}
        }
        
        await consumer._process_message(metric_data)
        
        # Verify metric was saved
        assert mock_db.add.called
        assert mock_db.commit.called
