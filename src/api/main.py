"""FastAPI application entry point"""

import logging

from fastapi import FastAPI

from src.api.config import settings
from src.api.dependencies import create_test_user
from src.api.middleware import setup_cors
from src.api.routes import auth, metrics, monitoring, network
from src.common.database import get_db
from src.common.kafka.producer import KafkaProducer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title=settings.PROJECT_NAME, version="0.1.0", docs_url="/docs", redoc_url="/redoc")

# Setup CORS middleware
setup_cors(app)

# Initialize Kafka producer
kafka_producer = KafkaProducer()


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting Device Metrics Receiver")
    await kafka_producer.connect()

    # Create test user for development
    db = next(get_db())
    create_test_user(db)
    db.close()


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Device Metrics Receiver")
    await kafka_producer.close()


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


# Include routers
app.include_router(auth.router)
app.include_router(metrics.router)
app.include_router(network.router)
app.include_router(monitoring.router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
