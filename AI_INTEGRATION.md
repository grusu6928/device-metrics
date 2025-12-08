# AI Integration Guide

This document describes the AI/ML integration features in the Device Metrics Microservice.

## Overview

The system integrates four major AI capabilities:

1. **Embeddings for Anomaly Similarity Detection**
2. **AI-Powered Classification & Anomaly Scoring**
3. **Natural-Language Summaries of Device Health** (LLM Inference)
4. **AI-Assisted Remediation Suggestions** (LLM + Rule Chain)

## 1. Embeddings for Anomaly Similarity Detection

### Architecture

- **Model**: `sentence-transformers/all-MiniLM-L6-v2` (384-dimensional embeddings)
- **Vector Database**: Qdrant (cosine similarity search)
- **Process**:
  1. Each metric is converted to a structured text representation
  2. Text is embedded using the transformer model
  3. Embedding is indexed in Qdrant with metadata
  4. Similar anomalies are found via vector similarity search

### Implementation

```python
from src.services.embeddings import EmbeddingService

service = EmbeddingService()

# Generate embedding
embedding = service.generate_embedding(
    device_id="device-001",
    metric_type="cpu_usage",
    value=95.5,
    metadata={"cpu_cores": 4}
)

# Index in vector DB
service.index_metric(metric_id=123, ...)

# Find similar anomalies
similar = service.find_similar_anomalies(
    device_id="device-001",
    metric_type="cpu_usage",
    value=95.0,
    limit=5,
    score_threshold=0.85
)
```

### Benefits

- **Pattern Recognition**: Identifies similar anomaly patterns across devices
- **Historical Context**: Learns from past incidents
- **Scalable**: Vector search is efficient even with millions of metrics
- **No Training Required**: Works immediately with pre-trained models

### Configuration

```python
# src/api/config.py
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
ANOMALY_THRESHOLD = 0.85  # Similarity threshold
QDRANT_COLLECTION = "device_metrics_embeddings"
```

## 2. AI-Powered Classification & Anomaly Scoring

### Architecture

- **ML Model**: Isolation Forest (unsupervised anomaly detection)
- **Features**: Metric value, metadata fields, metric type encoding
- **Scoring**: Combines similarity score (60%) + ML score (40%)

### Implementation

```python
from src.services.anomaly_detector import AnomalyDetector
from src.services.embeddings import EmbeddingService

embedding_service = EmbeddingService()
detector = AnomalyDetector(embedding_service)

# Add training samples (auto-trains at 100 samples)
detector.add_training_sample("cpu_usage", 75.0, {})

# Detect anomaly
result = detector.detect_anomaly(
    device_id="device-001",
    metric_type="cpu_usage",
    value=95.5,
    metadata={}
)

# Result structure:
# {
#     "is_anomaly": True,
#     "anomaly_score": 0.87,
#     "similarity_score": 0.92,
#     "ml_score": 0.78,
#     "classification": "value_spike"
# }
```

### Classification Types

- **value_spike**: Sudden increase in metric value
- **value_drop**: Sudden decrease in metric value
- **statistical_outlier**: Deviates from normal distribution
- **known_pattern**: Similar to historical anomalies
- **unknown_anomaly**: Doesn't match any pattern

### Benefits

- **Hybrid Approach**: Combines rule-based, similarity-based, and ML-based detection
- **Adaptive**: Learns normal patterns from incoming data
- **Interpretable**: Provides classification and reasoning

## 3. Natural-Language Device Health Summaries

### Architecture

- **Primary**: OpenAI GPT-4 (when API key is provided)
- **Fallback**: Rule-based summarization (always available)
- **Input**: Recent metrics, anomalies, key statistics
- **Output**: 2-3 sentence natural language summary

### Implementation

```python
from src.services.health_summarizer import HealthSummarizer
from sqlalchemy.orm import Session

summarizer = HealthSummarizer()

summary = summarizer.summarize_device_health(
    device_id="device-001",
    db=db_session,
    recent_hours=24
)

# Returns:
# {
#     "summary": "Device device-001 shows healthy operation...",
#     "overall_health": "healthy",  # healthy, degraded, critical
#     "key_metrics": {...},
#     "anomalies_detected": 2,
#     "generated_at": datetime(...)
# }
```

### LLM Prompt Structure

The system generates prompts like:

```
Generate a concise, natural-language health summary for device device-001.

Recent Metrics:
- cpu_usage: 75.5 percent at 2024-01-01T12:00:00
- memory_usage: 60.2 percent at 2024-01-01T12:00:00

Anomalies Detected:
- value_spike (score: 0.92) at 2024-01-01T11:30:00

Key Statistics:
cpu_usage: current=75.50, avg=72.30, range=[45.00-95.00]

Provide a 2-3 sentence summary that:
1. Describes the overall device health status
2. Highlights any concerning patterns or anomalies
3. Mentions key metrics that stand out
```

### Benefits

- **Human-Readable**: Summaries are easy to understand
- **Actionable**: Highlights key concerns
- **Contextual**: Considers recent history and patterns
- **Graceful Degradation**: Works without LLM API

### Configuration

```python
OPENAI_API_KEY = "your-key-here"  # Optional
LLM_MODEL = "gpt-4-turbo-preview"
MAX_ANOMALIES_FOR_SUMMARY = 10
```

## 4. AI-Assisted Remediation Suggestions

### Architecture

- **Primary**: OpenAI GPT-4 with structured prompts
- **Fallback**: Rule-based knowledge base
- **Input**: Anomaly details, metric context, classification
- **Output**: Actionable remediation steps with reasoning

### Implementation

```python
from src.services.remediation_engine import RemediationEngine
from src.models.device_metric import Anomaly, DeviceMetric

engine = RemediationEngine()

remediation = engine.generate_remediation(
    anomaly=anomaly_obj,
    metric=metric_obj
)

# Returns:
# {
#     "suggestion": "Check for runaway processes using 'top'...",
#     "reasoning": "High CPU usage often indicates...",
#     "priority": "high",  # high, medium, low
#     "estimated_impact": "Medium - requires investigation"
# }
```

### LLM Prompt Structure

```
As a DevOps engineer, provide a remediation suggestion for the following anomaly:

Device ID: device-001
Metric Type: cpu_usage
Metric Value: 95.5 percent
Anomaly Classification: value_spike
Anomaly Score: 0.92

Provide:
1. A specific, actionable remediation step (1-2 sentences)
2. Brief reasoning for why this remediation is appropriate
3. Priority level (high, medium, low)
4. Estimated impact of applying this remediation
```

### Rule-Based Knowledge Base

When LLM is unavailable, the system uses a knowledge base:

```python
remediation_rules = {
    "value_spike": {
        "cpu_usage": [
            "Check for runaway processes using 'top' or 'htop'",
            "Review recent deployments or configuration changes",
            "Consider horizontal scaling or resource limits"
        ],
        "memory_usage": [
            "Check for memory leaks in applications",
            "Review cache settings and memory allocation",
            "Consider increasing available memory or optimizing usage"
        ],
        # ... more rules
    }
}
```

### Benefits

- **Actionable**: Provides specific steps to resolve issues
- **Context-Aware**: Considers anomaly type and device context
- **Prioritized**: Helps teams focus on critical issues first
- **Learning**: Can improve with feedback loop

## Integration Flow

```
1. Metric Received → FastAPI Receiver
2. Published to Kafka
3. Consumer Processes:
   a. Save to Postgres
   b. Generate embedding → Index in Qdrant
   c. Detect anomaly (similarity + ML)
   d. If anomaly:
      - Create Anomaly record
      - Generate Alert
      - Generate Remediation (LLM + rules)
4. Health Summary Endpoint:
   - Fetch recent metrics/anomalies
   - Generate LLM summary (or rule-based)
   - Return structured response
```

## Configuration Options

### Environment Variables

```bash
# AI Model Configuration
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
ANOMALY_THRESHOLD=0.85
LLM_MODEL=gpt-4-turbo-preview
OPENAI_API_KEY=your-key-here  # Optional

# Vector Database
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION=device_metrics_embeddings

# Analysis Limits
MAX_ANOMALIES_FOR_SUMMARY=10
```

### Customization

**Change Embedding Model**:
```python
# app/config.py
EMBEDDING_MODEL = "sentence-transformers/all-mpnet-base-v2"  # Larger, more accurate
```

**Adjust Anomaly Threshold**:
```python
ANOMALY_THRESHOLD = 0.90  # More strict (fewer false positives)
ANOMALY_THRESHOLD = 0.75  # More sensitive (more detections)
```

**Use Different LLM**:
```python
LLM_MODEL = "gpt-3.5-turbo"  # Faster, cheaper
```

## Performance Considerations

- **Embeddings**: ~50ms per metric (CPU-bound)
- **Vector Search**: ~10ms for similarity search (even with millions of vectors)
- **LLM Calls**: ~2-3 seconds per summary/remediation (network-bound)
- **ML Training**: One-time cost, runs in background

## Future Enhancements

1. **Fine-tuned Embeddings**: Train on domain-specific device data
2. **Feedback Loop**: Learn from user actions on remediations
3. **Multi-Model Ensemble**: Combine multiple anomaly detection approaches
4. **Real-time Streaming**: Process anomalies as they occur
5. **Custom LLM Prompts**: Allow domain-specific prompt templates
6. **Cost Optimization**: Cache LLM responses, batch requests

## Cost Estimation

- **Embeddings**: Free (local inference)
- **Vector DB**: Minimal (self-hosted Qdrant)
- **LLM**: ~$0.03-0.10 per health summary (GPT-4)
- **Remediation**: ~$0.01-0.03 per anomaly (GPT-4)

For 1000 devices, 100 summaries/day: ~$3-10/day in LLM costs
