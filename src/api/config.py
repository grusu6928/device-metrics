"""API configuration"""

from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""

    # API
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Device Metrics API"

    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Database
    DATABASE_URL: str = (
        "postgresql://device_metrics:device_metrics_password@localhost:5432/device_metrics"
    )

    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_TOPIC_METRICS: str = "device-metrics"
    KAFKA_GROUP_ID: str = "device-metrics-consumer"

    # Vector DB (Qdrant)
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_COLLECTION: str = "device_metrics_embeddings"

    # AI/ML
    OPENAI_API_KEY: Optional[str] = None
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    ANOMALY_THRESHOLD: float = 0.85  # Similarity threshold for anomaly detection

    # Model configs
    LLM_MODEL: str = "gpt-4-turbo-preview"
    MAX_ANOMALIES_FOR_SUMMARY: int = 10

    # Object Storage (S3/MinIO)
    OBJECT_STORAGE_ENABLED: bool = False
    OBJECT_STORAGE_ENDPOINT: Optional[str] = None
    OBJECT_STORAGE_ACCESS_KEY: Optional[str] = None
    OBJECT_STORAGE_SECRET_KEY: Optional[str] = None
    OBJECT_STORAGE_BUCKET: str = "device-metrics-archive"
    OBJECT_STORAGE_USE_SSL: bool = True

    # HashiCorp Vault
    VAULT_ENABLED: bool = False
    VAULT_ADDR: Optional[str] = None
    VAULT_TOKEN: Optional[str] = None
    VAULT_MOUNT_POINT: str = "secret"

    # Cloud Platform
    CLOUD_PLATFORM: Optional[str] = None  # aws, azure, gcp
    AWS_REGION: Optional[str] = None
    AZURE_SUBSCRIPTION_ID: Optional[str] = None
    GCP_PROJECT_ID: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
