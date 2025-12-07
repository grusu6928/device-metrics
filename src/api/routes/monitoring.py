"""Monitoring and performance metrics routes"""
from fastapi import APIRouter, Depends
from typing import Annotated
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response

from src.api.config import settings
from src.api.dependencies import get_current_user

router = APIRouter(prefix=settings.API_V1_PREFIX, tags=["monitoring"])


@router.get("/metrics/prometheus")
async def prometheus_metrics(
    current_user: Annotated[dict, Depends(get_current_user)]
):
    """Prometheus metrics endpoint"""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


@router.get("/metrics/performance")
async def performance_metrics(
    current_user: Annotated[dict, Depends(get_current_user)]
):
    """Get performance metrics summary"""
    # This would aggregate metrics from Prometheus
    return {
        "metrics_ingested": "N/A",
        "avg_processing_time": "N/A",
        "anomalies_detected": "N/A",
        "active_connections": "N/A"
    }

