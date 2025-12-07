#!/usr/bin/env python3
"""Initialize database with tables"""
from src.common.database import engine, Base
from src.models.device_metric import DeviceMetric, Anomaly, Alert, Remediation
from src.models.user import User

def init_db():
    """Create all database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    init_db()
