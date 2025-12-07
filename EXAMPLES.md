# Usage Examples

## Quick Start

1. Start infrastructure services:
```bash
docker-compose up -d
```

2. Run database migrations:
```bash
alembic upgrade head
```

3. Start the receiver service:
```bash
uvicorn src.api.main:app --reload
```

4. Start the consumer service (in another terminal):
```bash
python -m src.consumer.main
```

## API Usage

### 1. Authenticate

```bash
curl -X POST "http://localhost:8000/api/v1/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=testpassword"
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

### 2. Ingest Metrics

```bash
curl -X POST "http://localhost:8000/api/v1/metrics" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "metrics": [
      {
        "device_id": "device-001",
        "metric_type": "cpu_usage",
        "value": 75.5,
        "unit": "percent",
        "timestamp": "2024-01-01T12:00:00Z",
        "metadata": {
          "cpu_cores": 4,
          "os": "linux"
        }
      },
      {
        "device_id": "device-001",
        "metric_type": "memory_usage",
        "value": 60.2,
        "unit": "percent",
        "timestamp": "2024-01-01T12:00:00Z",
        "metadata": {
          "total_memory_gb": 16
        }
      }
    ]
  }'
```

### 3. Get Device Health Summary

```bash
curl -X GET "http://localhost:8000/api/v1/metrics/health/device-001" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

Response:
```json
{
  "device_id": "device-001",
  "summary": "Device device-001 shows healthy operation with normal CPU and memory usage...",
  "overall_health": "healthy",
  "key_metrics": {
    "cpu_usage": {
      "current": 75.5,
      "average": 72.3,
      "min": 45.0,
      "max": 95.0,
      "count": 100
    }
  },
  "anomalies_detected": 2,
  "generated_at": "2024-01-01T13:00:00Z"
}
```

## AI Integration Examples

### Anomaly Detection

The system automatically:
1. Generates embeddings for each metric
2. Indexes in vector database (Qdrant)
3. Detects anomalies using:
   - Similarity search against known anomalies
   - ML-based outlier detection (Isolation Forest)
   - Rule-based classification

### Health Summaries

The health summary service:
- Fetches recent metrics and anomalies
- Generates natural language summaries using LLM (if OpenAI API key is set)
- Falls back to rule-based summaries if LLM is unavailable
- Provides actionable insights

### Remediation Suggestions

When an anomaly is detected:
1. System generates AI-powered remediation suggestions
2. Suggestions include reasoning and priority
3. Can be integrated with incident management systems

## Python Client Example

```python
import requests
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"

# Authenticate
response = requests.post(
    f"{BASE_URL}/auth/token",
    data={"username": "testuser", "password": "testpassword"}
)
token = response.json()["access_token"]

headers = {"Authorization": f"Bearer {token}"}

# Send metrics
metrics_data = {
    "metrics": [
        {
            "device_id": "device-001",
            "metric_type": "cpu_usage",
            "value": 85.5,
            "unit": "percent",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "metadata": {"cpu_cores": 4}
        }
    ]
}

response = requests.post(
    f"{BASE_URL}/metrics",
    json=metrics_data,
    headers=headers
)
print(response.json())

# Get health summary
response = requests.get(
    f"{BASE_URL}/metrics/health/device-001",
    headers=headers
)
print(response.json())
```

## Kubernetes Deployment

### Using Helm

```bash
# Install the chart
helm install device-metrics ./helm/device-metrics

# Update configuration
helm upgrade device-metrics ./helm/device-metrics \
  --set config.env.OPENAI_API_KEY=your-key-here

# View status
kubectl get pods -l app.kubernetes.io/name=device-metrics
```

## Configuration

### Environment Variables

Key configuration options:

- `OPENAI_API_KEY`: Enable LLM-powered summaries and remediation (optional)
- `ANOMALY_THRESHOLD`: Similarity threshold for anomaly detection (default: 0.85)
- `KAFKA_BOOTSTRAP_SERVERS`: Kafka broker addresses
- `DATABASE_URL`: PostgreSQL connection string
- `QDRANT_HOST`: Qdrant vector database host

### AI Models

- **Embeddings**: `sentence-transformers/all-MiniLM-L6-v2` (default, can be changed)
- **LLM**: `gpt-4-turbo-preview` (requires OpenAI API key)

## Monitoring

### Health Checks

- Receiver: `GET /health`
- Consumer: Process-based health check

### Metrics

The system tracks:
- Metrics ingested per device
- Anomalies detected
- Processing latency
- Vector DB indexing status

## Troubleshooting

### Consumer not processing messages

1. Check Kafka connectivity:
```bash
docker-compose exec kafka kafka-console-consumer --bootstrap-server localhost:9092 --topic device-metrics --from-beginning
```

2. Check consumer logs:
```bash
python -m app.consumer.main
```

### Vector DB connection issues

1. Verify Qdrant is running:
```bash
curl http://localhost:6333/health
```

2. Check collection exists:
```python
from src.services.embeddings import EmbeddingService
service = EmbeddingService()
# Collection will be created automatically
```


