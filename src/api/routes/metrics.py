"""Metrics routes"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import Annotated
import logging

from src.api.config import settings
from src.common.database import get_db
from src.common.kafka.producer import KafkaProducer
from src.api.dependencies import get_current_user
from src.schemas.device_metric import MetricIngestRequest, MetricIngestResponse
from src.services.health_summarizer import HealthSummarizer

logger = logging.getLogger(__name__)

router = APIRouter(prefix=settings.API_V1_PREFIX, tags=["metrics"])

# Initialize Kafka producer (singleton)
kafka_producer = KafkaProducer()


@router.post(
    "/metrics",
    response_model=MetricIngestResponse,
    status_code=status.HTTP_202_ACCEPTED
)
async def ingest_metrics(
    request: MetricIngestRequest,
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    """
    Ingest device metrics
    
    Accepts metrics and publishes them to Kafka for async processing
    """
    ingested = 0
    failed = 0
    
    for metric in request.metrics:
        try:
            # Publish to Kafka
            await kafka_producer.send_metric(metric.dict())
            ingested += 1
        except Exception as e:
            logger.error(f"Failed to send metric to Kafka: {e}")
            failed += 1
    
    return MetricIngestResponse(
        ingested=ingested,
        failed=failed,
        message=f"Successfully queued {ingested} metric(s) for processing"
    )


@router.get("/metrics/health/{device_id}")
async def get_device_health(
    device_id: str,
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    """Get device health summary (requires AI services)"""
    summarizer = HealthSummarizer()
    summary = summarizer.summarize_device_health(device_id, db)
    
    return summary

