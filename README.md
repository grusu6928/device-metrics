# Device Metrics Microservice

A production-ready microservice for ingesting, processing, and analyzing device metrics with AI-powered anomaly detection and remediation. Supports network automation, full-stack development, and cloud-native deployment.

## Features

- **Full-Stack Application**: FastAPI backend with Angular/TypeScript frontend dashboard
- **Network Automation**: Network device monitoring, automation scripts, and remediation
- **FastAPI Receiver**: RESTful API with JWT authentication for device metric ingestion
- **Kafka Integration**: Producer/consumer pattern for async metric processing
- **PostgreSQL Storage**: Persistent storage for device metrics and metadata
- **Vector Database**: Embeddings-based similarity search for anomaly detection
- **AI-Powered Analysis**:
  - Embedding-based anomaly similarity detection
  - AI-powered anomaly classification and scoring
  - Natural-language device health summaries
  - AI-assisted remediation suggestions
- **Cloud Deployment**: Terraform/Bicep configs for AWS, Azure, and GCP
- **Secrets Management**: HashiCorp Vault integration
- **Object Storage**: S3/MinIO integration for metric archives
- **Kubernetes Deployment**: Helm chart with liveness/readiness probes and resource limits
- **Performance Monitoring**: Prometheus metrics and performance optimization
- **Testing**: Comprehensive unit, integration, and performance tests
- **CI/CD**: Enhanced GitHub Actions pipeline with multiple stages

## Architecture

```
Device → FastAPI (JWT Auth) → Kafka Producer → Kafka Topic
                                               ↓
                    Kafka Consumer → Postgres + Vector DB → AI Analysis
```

## Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Kubernetes cluster (for deployment)
- Helm 3.x

### Local Development

1. Start infrastructure:
```bash
docker-compose up -d
```

2. Run migrations:
```bash
alembic upgrade head
```

3. Start services:
```bash
# FastAPI receiver
uvicorn src.api.main:app --reload

# Kafka consumer
python -m src.consumer.main
```

## Project Structure

```
device-metrics/
├── src/                   # Source code
│   ├── api/              # FastAPI application
│   │   └── routes/       # API route handlers (auth, metrics, network, monitoring)
│   ├── consumer/         # Kafka consumer service
│   ├── services/         # Business logic services (AI, network automation)
│   ├── models/           # Database models
│   ├── schemas/          # Pydantic schemas
│   ├── repositories/     # Data access layer
│   └── common/           # Shared utilities (auth, database, kafka, vault, storage)
├── frontend/             # Angular/TypeScript dashboard
├── cloud/                # Cloud deployment configs
│   ├── aws/             # AWS Terraform configs
│   ├── azure/           # Azure Bicep configs
│   └── gcp/             # GCP Terraform configs
├── helm/                 # Helm chart for Kubernetes
├── tests/                # Test suite (unit, integration, performance)
├── scripts/              # Utility scripts
├── .github/workflows/    # CI/CD pipelines
├── docker-compose.yml    # Local development stack
├── Dockerfile            # Container image definition
└── alembic/             # Database migrations
```

## AI Integration Features

This project emphasizes AI/ML integration with four key capabilities:

### 1. Embeddings for Anomaly Similarity Detection

- Uses `sentence-transformers` to generate embeddings for each metric
- Stores embeddings in Qdrant vector database
- Finds similar anomalies via cosine similarity search
- No training required - works immediately

See [AI_INTEGRATION.md](AI_INTEGRATION.md) for detailed documentation.

### 2. AI-Powered Classification & Anomaly Scoring

- Combines similarity search (60%) + ML-based outlier detection (40%)
- Uses Isolation Forest for statistical anomaly detection
- Auto-trains on incoming metrics
- Classifies anomalies (spike, drop, outlier, known pattern)

### 3. Natural-Language Device Health Summaries

- Generates human-readable summaries using GPT-4 (when API key provided)
- Falls back to rule-based summaries when LLM unavailable
- Considers recent metrics, anomalies, and patterns
- Provides actionable insights

### 4. AI-Assisted Remediation Suggestions

- LLM-generated remediation steps with reasoning
- Rule-based knowledge base as fallback
- Prioritized suggestions (high/medium/low)
- Context-aware recommendations

## Documentation

- [Deployment Guide](DEPLOYMENT.md) - Complete deployment instructions
- [AI Integration Guide](AI_INTEGRATION.md) - Detailed AI/ML features
- [Usage Examples](EXAMPLES.md) - API examples and usage patterns

## Development

### Setup

```bash
# Use the setup script
make setup

# Or manually:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
docker-compose up -d
alembic upgrade head
```

### Running Tests

```bash
make test
# or
pytest tests/ -v --cov=src
```

### Code Quality

```bash
make lint      # Check code style
make format    # Auto-format code
```

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for comprehensive deployment guide including:
- Quick start options (Docker Compose, Kubernetes)
- Deployment structure explanation
- Cloud-specific deployments (AWS, Azure, GCP)
- Environment configuration
- Troubleshooting

## Configuration

Key environment variables:

- `OPENAI_API_KEY` - Enable LLM features (optional)
- `ANOMALY_THRESHOLD` - Similarity threshold (default: 0.85)
- `DATABASE_URL` - PostgreSQL connection string
- `KAFKA_BOOTSTRAP_SERVERS` - Kafka broker addresses
- `QDRANT_HOST` - Vector database host
- `VAULT_ENABLED` - Enable HashiCorp Vault (default: false)
- `VAULT_ADDR` - Vault server address
- `OBJECT_STORAGE_ENABLED` - Enable S3/MinIO (default: false)
- `OBJECT_STORAGE_ENDPOINT` - Object storage endpoint
- `CLOUD_PLATFORM` - Cloud platform (aws, azure, gcp)

See `.env.example` for all configuration options.

## Technologies & Skills Demonstrated

### Backend & API
- Python 3.11+, FastAPI, RESTful API design
- SQL/PostgreSQL, SQLAlchemy ORM, Alembic migrations
- Pytest for testing
- JWT authentication and API security

### Microservices & Event-Driven Architecture
- Microservices architecture with clear separation of concerns
- Apache Kafka for event-driven messaging
- Real-time data pipelines
- Service-to-service communication patterns

### AI/ML Integration
- AI-assisted features (anomaly detection, health summaries, remediation)
- Machine learning models (Isolation Forest)
- Vector embeddings and similarity search
- LLM integration with graceful degradation

### Network Automation
- Network device monitoring and management
- Network-specific metric validation
- Automation script generation
- Network health assessment

### Cloud & DevOps
- Kubernetes (K8s) clusters and containerization
- Cloud platforms: AWS, Azure, GCP (Terraform/Bicep)
- CI/CD pipelines (GitHub Actions)
- Docker containerization
- Helm charts for K8s deployment

### Security & Secrets Management
- HashiCorp Vault integration
- Secrets management best practices
- API security and authentication

### Storage & Data
- Object storage (S3/MinIO) for metric archives
- Hierarchical and relational data modeling
- Performance optimization

### Frontend
- Angular and TypeScript
- JavaScript for client-side logic
- Dashboard and visualization

### Testing & Quality
- Unit testing with pytest
- Integration testing
- Performance testing
- Code quality tools (flake8, black, isort, mypy)

## License

MIT License

