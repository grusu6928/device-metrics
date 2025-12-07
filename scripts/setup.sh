#!/bin/bash
# Setup script for device-metrics project

set -e

echo "Setting up Device Metrics Microservice..."

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Install pre-commit hooks
echo "Installing pre-commit hooks..."
pre-commit install
pre-commit install --hook-type commit-msg
echo "Pre-commit hooks installed!"

# Copy .env.example to .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "Please update .env with your configuration values"
fi

# Start infrastructure with Docker Compose
echo "Starting infrastructure services (Postgres, Kafka, Qdrant)..."
docker-compose up -d

# Wait for services to be ready
echo "Waiting for services to be ready..."
sleep 10

# Run database migrations
echo "Running database migrations..."
alembic upgrade head

echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Update .env file with your configuration"
echo "2. Start the receiver: uvicorn app.receiver.main:app --reload"
echo "3. Start the consumer: python -m app.consumer.main"


