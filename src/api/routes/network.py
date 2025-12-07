"""Network automation and device management routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Annotated, List
import logging

from src.api.config import settings
from src.common.database import get_db
from src.api.dependencies import get_current_user
from src.services.network_automation import NetworkDeviceManager, NetworkAutomationService
from src.repositories.metric_repository import MetricRepository

logger = logging.getLogger(__name__)

router = APIRouter(prefix=settings.API_V1_PREFIX, tags=["network"])

# Initialize network services
device_manager = NetworkDeviceManager()
automation_service = NetworkAutomationService(device_manager)


@router.get("/network/devices/{device_id}/summary")
async def get_network_device_summary(
    device_id: str,
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    """Get network device summary with health status"""
    metric_repo = MetricRepository(db)
    metrics = metric_repo.get_metrics_by_device(device_id, limit=100)
    
    if not metrics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No metrics found for device {device_id}"
        )
    
    # Convert to dict format
    metrics_data = [
        {
            "metric_type": m.metric_type,
            "value": m.value,
            "metadata": m.metadata or {}
        }
        for m in metrics
    ]
    
    summary = device_manager.get_network_device_summary(device_id, metrics_data)
    return summary


@router.get("/network/devices/{device_id}/issues")
async def get_network_issues(
    device_id: str,
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    """Get critical network issues for a device"""
    metric_repo = MetricRepository(db)
    metrics = metric_repo.get_metrics_by_device(device_id, limit=100)
    
    metrics_data = [
        {
            "metric_type": m.metric_type,
            "value": m.value,
            "metadata": m.metadata or {}
        }
        for m in metrics
    ]
    
    summary = device_manager.get_network_device_summary(device_id, metrics_data)
    return {
        "device_id": device_id,
        "critical_issues": summary.get("critical_alerts", []),
        "network_health": summary.get("network_health", "unknown")
    }


@router.post("/network/devices/{device_id}/remediation")
async def generate_network_remediation(
    device_id: str,
    issue: dict,
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    """Generate network-specific remediation steps and automation scripts"""
    remediation = automation_service.generate_network_remediation(device_id, issue)
    return remediation


@router.get("/network/devices")
async def list_network_devices(
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Session = Depends(get_db),
    device_type: str = None
):
    """List all network devices with their health status"""
    # This would typically query a devices table
    # For now, return available device types
    return {
        "device_types": device_manager.DEVICE_TYPES,
        "supported_metrics": device_manager.NETWORK_METRICS
    }

