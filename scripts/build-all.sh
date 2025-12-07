#!/bin/bash
# Build all Docker images

set -e

echo "Building Docker images..."

# Build backend
echo "Building backend image..."
docker build -t device-metrics-api:latest .

# Build frontend
echo "Building frontend image..."
cd frontend
docker build -t device-metrics-frontend:latest .
cd ..

echo "All images built successfully!"
echo "Backend: device-metrics-api:latest"
echo "Frontend: device-metrics-frontend:latest"

