"""Pytest configuration and fixtures"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from src.common.database import Base, get_db
from src.api.main import app
from src.api.config import settings

# Use in-memory SQLite for testing
TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def auth_token(client):
    """Get authentication token for tests"""
    # Create test user first
    from src.api.dependencies import create_test_user
    from src.models.user import User
    from src.common.auth import get_password_hash
    db = next(TestingSessionLocal())
    create_test_user(db)
    db.close()
    
    # Login
    response = client.post(
        "/api/v1/auth/token",
        data={"username": "testuser", "password": "testpassword"}
    )
    return response.json()["access_token"]


@pytest.fixture
def sample_metric():
    """Sample metric data"""
    return {
        "device_id": "device-001",
        "metric_type": "cpu_usage",
        "value": 75.5,
        "unit": "percent",
        "timestamp": "2024-01-01T12:00:00Z",
        "metadata": {"cpu_cores": 4}
    }
