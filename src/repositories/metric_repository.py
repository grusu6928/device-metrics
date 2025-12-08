"""Repository for device metrics data access"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from src.models.device_metric import Alert, Anomaly, DeviceMetric, Remediation


class MetricRepository:
    """Repository for device metrics"""

    def __init__(self, db: Session):
        """Initialize repository with database session"""
        self.db = db

    def create_metric(self, metric_data: dict) -> DeviceMetric:
        """Create a new device metric"""
        # Map 'metadata' key to 'metric_metadata' attribute
        metric_dict = metric_data.copy()
        if "metadata" in metric_dict:
            metric_dict["metric_metadata"] = metric_dict.pop("metadata")
        metric = DeviceMetric(**metric_dict)
        self.db.add(metric)
        self.db.commit()
        self.db.refresh(metric)
        return metric

    def get_metric_by_id(self, metric_id: int) -> Optional[DeviceMetric]:
        """Get metric by ID"""
        return self.db.query(DeviceMetric).filter(DeviceMetric.id == metric_id).first()

    def get_metrics_by_device(self, device_id: str, limit: int = 100) -> List[DeviceMetric]:
        """Get recent metrics for a device"""
        return (
            self.db.query(DeviceMetric)
            .filter(DeviceMetric.device_id == device_id)
            .order_by(DeviceMetric.timestamp.desc())
            .limit(limit)
            .all()
        )

    def get_metrics_since(
        self, device_id: str, since: datetime, limit: int = 100
    ) -> List[DeviceMetric]:
        """Get metrics for a device since a timestamp"""
        return (
            self.db.query(DeviceMetric)
            .filter(DeviceMetric.device_id == device_id, DeviceMetric.timestamp >= since)
            .order_by(DeviceMetric.timestamp.desc())
            .limit(limit)
            .all()
        )


class AnomalyRepository:
    """Repository for anomalies"""

    def __init__(self, db: Session):
        """Initialize repository with database session"""
        self.db = db

    def create_anomaly(self, anomaly_data: dict) -> Anomaly:
        """Create a new anomaly record"""
        anomaly = Anomaly(**anomaly_data)
        self.db.add(anomaly)
        self.db.commit()
        self.db.refresh(anomaly)
        return anomaly

    def get_anomalies_by_device(
        self, device_id: str, since: datetime, limit: int = 10
    ) -> List[Anomaly]:
        """Get anomalies for a device since a timestamp"""
        return (
            self.db.query(Anomaly)
            .join(DeviceMetric)
            .filter(DeviceMetric.device_id == device_id, Anomaly.detected_at >= since)
            .order_by(Anomaly.detected_at.desc())
            .limit(limit)
            .all()
        )

    def create_alert(self, alert_data: dict) -> Alert:
        """Create a new alert"""
        alert = Alert(**alert_data)
        self.db.add(alert)
        self.db.commit()
        self.db.refresh(alert)
        return alert

    def create_remediation(self, remediation_data: dict) -> Remediation:
        """Create a new remediation"""
        remediation = Remediation(**remediation_data)
        self.db.add(remediation)
        self.db.commit()
        self.db.refresh(remediation)
        return remediation
