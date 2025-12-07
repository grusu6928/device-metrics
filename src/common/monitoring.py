"""Performance monitoring and metrics collection"""
from prometheus_client import Counter, Histogram, Gauge
import time
import logging

logger = logging.getLogger(__name__)

# Prometheus metrics
metrics_ingested_total = Counter(
    'device_metrics_ingested_total',
    'Total number of metrics ingested',
    ['device_id', 'metric_type']
)

metrics_processed_duration = Histogram(
    'device_metrics_processed_duration_seconds',
    'Time spent processing metrics',
    ['operation']
)

anomalies_detected_total = Counter(
    'device_anomalies_detected_total',
    'Total number of anomalies detected',
    ['device_id', 'classification']
)

active_connections = Gauge(
    'device_metrics_active_connections',
    'Number of active database connections'
)

kafka_messages_produced = Counter(
    'kafka_messages_produced_total',
    'Total number of Kafka messages produced',
    ['topic']
)

kafka_messages_consumed = Counter(
    'kafka_messages_consumed_total',
    'Total number of Kafka messages consumed',
    ['topic', 'status']
)


class PerformanceMonitor:
    """Performance monitoring service"""
    
    def __init__(self):
        """Initialize performance monitor"""
        self.metrics = {}
    
    def record_metric_ingestion(self, device_id: str, metric_type: str):
        """Record metric ingestion"""
        metrics_ingested_total.labels(
            device_id=device_id,
            metric_type=metric_type
        ).inc()
    
    def record_processing_time(self, operation: str, duration: float):
        """Record processing time"""
        metrics_processed_duration.labels(operation=operation).observe(duration)
    
    def record_anomaly(self, device_id: str, classification: str):
        """Record anomaly detection"""
        anomalies_detected_total.labels(
            device_id=device_id,
            classification=classification
        ).inc()
    
    def update_connections(self, count: int):
        """Update active connections gauge"""
        active_connections.set(count)
    
    def record_kafka_produce(self, topic: str):
        """Record Kafka message production"""
        kafka_messages_produced.labels(topic=topic).inc()
    
    def record_kafka_consume(self, topic: str, status: str):
        """Record Kafka message consumption"""
        kafka_messages_consumed.labels(topic=topic, status=status).inc()


class PerformanceOptimizer:
    """Performance optimization utilities"""
    
    @staticmethod
    def batch_process(items: list, batch_size: int = 100):
        """Process items in batches for better performance"""
        for i in range(0, len(items), batch_size):
            yield items[i:i + batch_size]
    
    @staticmethod
    def cache_key(device_id: str, metric_type: str, timestamp: str) -> str:
        """Generate cache key for metrics"""
        return f"{device_id}:{metric_type}:{timestamp}"
    
    @staticmethod
    def optimize_query_filters(filters: dict) -> dict:
        """Optimize database query filters"""
        # Remove None values
        return {k: v for k, v in filters.items() if v is not None}
    
    @staticmethod
    def should_archive_metric(timestamp: str, retention_days: int = 90) -> bool:
        """Determine if metric should be archived"""
        from datetime import datetime, timedelta
        
        try:
            metric_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            cutoff = datetime.utcnow() - timedelta(days=retention_days)
            return metric_time < cutoff
        except Exception:
            return False

