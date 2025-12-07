"""AI-related schemas"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class AnomalyDetectionResponse(BaseModel):
    """Anomaly detection response"""
    is_anomaly: bool
    anomaly_score: float
    similarity_score: Optional[float] = None
    classification: Optional[str] = None
    similar_anomalies: Optional[List[dict]] = None


class HealthSummaryResponse(BaseModel):
    """Device health summary response"""
    device_id: str
    summary: str
    overall_health: str  # healthy, degraded, critical
    key_metrics: dict
    anomalies_detected: int
    generated_at: datetime


class RemediationSuggestion(BaseModel):
    """Remediation suggestion response"""
    suggestion: str
    reasoning: str
    priority: str  # high, medium, low
    estimated_impact: Optional[str] = None

