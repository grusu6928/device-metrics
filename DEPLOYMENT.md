# Deployment Guide

Complete guide for deploying the Device Metrics microservice and frontend dashboard.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Deployment Structure](#deployment-structure)
3. [Local Development](#local-development)
4. [Docker Deployment](#docker-deployment)
5. [Kubernetes Deployment](#kubernetes-deployment)
6. [Cloud-Specific Deployments](#cloud-specific-deployments)
7. [Frontend Deployment](#frontend-deployment)
8. [Environment Variables](#environment-variables)
9. [Troubleshooting](#troubleshooting)

## Quick Start

### Docker Compose (Easiest)

```bash
# Start everything
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f api
docker-compose logs -f consumer
docker-compose logs -f frontend

# Access services
# Backend API: http://localhost:8000
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/docs
```

### Kubernetes with Helm

```bash
# Install all components
helm install device-metrics ./helm/device-metrics \
  --namespace device-metrics \
  --create-namespace

# Check pods
kubectl get pods -n device-metrics

# Port forward to access locally
kubectl port-forward svc/device-metrics-receiver 8000:8000 -n device-metrics
kubectl port-forward svc/device-metrics-frontend 3000:80 -n device-metrics
```

## Deployment Structure

### `cloud/` - Infrastructure as Code (IaC)
**Purpose**: Creates the cloud infrastructure that Kubernetes runs on.

- Creates Kubernetes clusters (EKS, AKS, GKE)
- Sets up managed databases (RDS, Azure Database, Cloud SQL)
- Configures message queues (MSK, Event Hubs, Pub/Sub)
- Creates storage buckets (S3, Blob Storage, Cloud Storage)

**Usage**:
```bash
# AWS
cd cloud/aws/terraform && terraform apply

# Azure
az deployment group create --template-file cloud/azure/main.bicep

# GCP
cd cloud/gcp && terraform apply
```

### `helm/` - Helm Charts
**Purpose**: Deploys the application to an existing Kubernetes cluster.

- Templates Kubernetes manifests
- Parameterization via `values.yaml`
- Manages application lifecycle (install, upgrade, rollback)

**Usage**:
```bash
helm install device-metrics ./helm/device-metrics
helm upgrade device-metrics ./helm/device-metrics
helm uninstall device-metrics
```

**View generated manifests**:
```bash
helm template device-metrics ./helm/device-metrics
```

## Local Development

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- PostgreSQL, Kafka, Qdrant (via Docker Compose)

### Backend Setup

```bash
# 1. Start infrastructure services
docker-compose up -d

# 2. Set up Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Run database migrations
alembic upgrade head

# 4. Start backend API
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# 5. Start Kafka consumer (separate terminal)
python -m src.consumer.main
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend will be available at `http://localhost:3000` and proxies to backend at `http://localhost:8000`.

## Docker Deployment

### Build Images

```bash
# Build backend image
docker build -t device-metrics-api:latest .

# Build frontend image
cd frontend
docker build -t device-metrics-frontend:latest .
```

### Run with Docker Compose

Update `docker-compose.yml` to include frontend service, then:

```bash
docker-compose up -d
```

### Manual Docker Run

```bash
# Backend
docker run -d \
  -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:pass@host:5432/db \
  -e KAFKA_BOOTSTRAP_SERVERS=kafka:9092 \
  device-metrics-api:latest

# Frontend
docker run -d \
  -p 3000:80 \
  -e REACT_APP_API_URL=http://api-host:8000 \
  device-metrics-frontend:latest
```

## Kubernetes Deployment

### Using Helm

```bash
# Install all components
helm install device-metrics ./helm/device-metrics

# Check status
kubectl get pods -l app.kubernetes.io/name=device-metrics

# View logs
kubectl logs -f deployment/device-metrics-receiver
kubectl logs -f deployment/device-metrics-consumer
kubectl logs -f deployment/device-metrics-frontend
```

### View Generated Manifests

If you need to see the raw Kubernetes manifests that Helm generates:

```bash
# Generate manifests without installing
helm template device-metrics ./helm/device-metrics

# Save to file
helm template device-metrics ./helm/device-metrics > manifests.yaml
```

## Cloud-Specific Deployments

### AWS (EKS)

```bash
cd cloud/aws/terraform

# Initialize and deploy infrastructure
terraform init
terraform plan
terraform apply

# Configure kubectl
aws eks update-kubeconfig --name device-metrics-cluster --region us-east-1

# Deploy application
helm install device-metrics ./helm/device-metrics \
  --namespace device-metrics \
  --create-namespace \
  --set config.env.DATABASE_URL=$RDS_ENDPOINT \
  --set config.env.KAFKA_BOOTSTRAP_SERVERS=$MSK_BROKERS
```

### Azure (AKS)

```bash
cd cloud/azure

# Login and create resource group
az login
az group create --name device-metrics-rg --location eastus

# Deploy infrastructure
az deployment group create \
  --resource-group device-metrics-rg \
  --template-file main.bicep

# Configure kubectl and deploy
az aks get-credentials --resource-group device-metrics-rg --name device-metrics-aks
helm install device-metrics ./helm/device-metrics \
  --namespace device-metrics \
  --create-namespace
```

### GCP (GKE)

```bash
cd cloud/gcp

# Set project and deploy infrastructure
gcloud config set project YOUR_PROJECT_ID
terraform init
terraform apply

# Configure kubectl and deploy
gcloud container clusters get-credentials device-metrics-gke --region us-central1
helm install device-metrics ./helm/device-metrics \
  --namespace device-metrics \
  --create-namespace
```

## Frontend Deployment

### Static Hosting (Recommended)

Build the frontend as static files and serve via:

- **AWS S3 + CloudFront**
- **Azure Blob Storage + CDN**
- **GCP Cloud Storage + CDN**
- **Netlify/Vercel**

### Build for Production

```bash
cd frontend
npm run build
```

This creates `dist/` directory with static files.

### Nginx Deployment

```bash
# Copy build files
cp -r frontend/dist/* /var/www/html/

# Nginx config
server {
    listen 80;
    server_name your-domain.com;
    root /var/www/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Environment Variables

### Backend

```bash
DATABASE_URL=postgresql://user:pass@host:5432/db
KAFKA_BOOTSTRAP_SERVERS=kafka:9092
QDRANT_HOST=qdrant
QDRANT_PORT=6333
SECRET_KEY=your-secret-key
OPENAI_API_KEY=optional-openai-key
VAULT_ENABLED=false
VAULT_ADDR=http://vault:8200
OBJECT_STORAGE_ENABLED=false
OBJECT_STORAGE_ENDPOINT=s3.amazonaws.com
```

### Frontend

```bash
REACT_APP_API_URL=http://api-host:8000
```

## Health Checks

### Backend

```bash
curl http://localhost:8000/health
```

### Frontend

```bash
curl http://localhost:3000
```

## Monitoring

### Prometheus Metrics

```bash
curl http://localhost:8000/api/v1/metrics/prometheus
```

### Logs

```bash
# Kubernetes
kubectl logs -f deployment/device-metrics-receiver
kubectl logs -f deployment/device-metrics-consumer

# Docker
docker logs device-metrics-api
docker logs device-metrics-consumer
```

## Troubleshooting

### Backend not starting

1. Check database connection
2. Verify Kafka is accessible
3. Check environment variables
4. Review logs for errors

### Frontend not connecting

1. Verify `REACT_APP_API_URL` is set correctly
2. Check CORS settings in backend
3. Verify backend is running and accessible
4. Check browser console for errors

### Consumer not processing

1. Verify Kafka topic exists
2. Check consumer group configuration
3. Review consumer logs
4. Verify database connection
