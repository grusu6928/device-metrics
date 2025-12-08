"""Device metric database models"""

from sqlalchemy import JSON, Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.common.database import Base


class DeviceMetric(Base):
    """Device metric model"""

    __tablename__ = "device_metrics"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(255), nullable=False, index=True)
    metric_type = Column(String(100), nullable=False, index=True)
    value = Column(Float, nullable=False)
    unit = Column(String(50))
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    metric_metadata = Column("metadata", JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    anomalies = relationship("Anomaly", back_populates="metric")

    def __repr__(self):
        return f"<DeviceMetric(id={self.id}, device_id={self.device_id}, metric_type={self.metric_type})>"


class Anomaly(Base):
    """Anomaly detection result"""

    __tablename__ = "anomalies"

    id = Column(Integer, primary_key=True, index=True)
    metric_id = Column(Integer, ForeignKey("device_metrics.id"), nullable=False)
    anomaly_score = Column(Float, nullable=False)
    similarity_score = Column(Float)  # Similarity to known anomalies
    classification = Column(String(100))  # AI classification
    is_confirmed = Column(Boolean, default=False)
    detected_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relationships
    metric = relationship("DeviceMetric", back_populates="anomalies")
    alerts = relationship("Alert", back_populates="anomaly")
    remediations = relationship("Remediation", back_populates="anomaly")

    def __repr__(self):
        return f"<Anomaly(id={self.id}, metric_id={self.metric_id}, score={self.anomaly_score})>"


class Alert(Base):
    """Alert generated from anomaly"""

    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    anomaly_id = Column(Integer, ForeignKey("anomalies.id"), nullable=False)
    severity = Column(String(50), nullable=False, index=True)  # critical, warning, info
    message = Column(Text, nullable=False)
    status = Column(String(50), default="open", index=True)  # open, acknowledged, resolved
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    anomaly = relationship("Anomaly", back_populates="alerts")

    def __repr__(self):
        return f"<Alert(id={self.id}, anomaly_id={self.anomaly_id}, severity={self.severity})>"


class Remediation(Base):
    """AI-generated remediation suggestions"""

    __tablename__ = "remediations"

    id = Column(Integer, primary_key=True, index=True)
    anomaly_id = Column(Integer, ForeignKey("anomalies.id"), nullable=False)
    suggestion = Column(Text, nullable=False)
    reasoning = Column(Text)  # AI reasoning for the suggestion
    priority = Column(String(50), default="medium")  # high, medium, low
    applied = Column(Boolean, default=False)
    applied_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    anomaly = relationship("Anomaly", back_populates="remediations")

    def __repr__(self):
        return (
            f"<Remediation(id={self.id}, anomaly_id={self.anomaly_id}, priority={self.priority})>"
        )
