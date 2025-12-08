"""AI-related schemas"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


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
