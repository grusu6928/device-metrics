"""Device metric schemas"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any


class DeviceMetricCreate(BaseModel):
    """Schema for creating a device metric"""
    device_id: str = Field(..., description="Unique device identifier")
    metric_type: str = Field(..., description="Type of metric (e.g., cpu_usage, memory_usage)")
    value: float = Field(..., description="Metric value")
    unit: Optional[str] = Field(None, description="Unit of measurement")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Metric timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class DeviceMetricResponse(BaseModel):
    """Schema for device metric response"""
    id: int
    device_id: str
    metric_type: str
    value: float
    unit: Optional[str]
    timestamp: datetime
    metadata: Dict[str, Any]
    created_at: datetime
    
    class Config:
        from_attributes = True


class MetricIngestRequest(BaseModel):
    """Schema for metric ingestion request"""
    metrics: list[DeviceMetricCreate] = Field(..., description="List of metrics to ingest")


class MetricIngestResponse(BaseModel):
    """Schema for metric ingestion response"""
    ingested: int = Field(..., description="Number of metrics successfully ingested")
    failed: int = Field(default=0, description="Number of metrics that failed to ingest")
    message: str = Field(..., description="Status message")

