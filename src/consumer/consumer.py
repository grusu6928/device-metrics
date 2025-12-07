"""Kafka consumer for processing metrics"""
import json
import asyncio
from typing import Dict, Any
from kafka import KafkaConsumer
from sqlalchemy.orm import Session
from datetime import datetime

from src.api.config import settings
from src.common.database import SessionLocal
from src.models.device_metric import DeviceMetric, Anomaly, Alert, Remediation
from src.services.embeddings import EmbeddingService
from src.services.anomaly_detector import AnomalyDetector
from src.services.remediation_engine import RemediationEngine
from src.repositories.metric_repository import MetricRepository, AnomalyRepository
import logging

logger = logging.getLogger(__name__)


class MetricsConsumer:
    """Kafka consumer for processing device metrics"""
    
    def __init__(self):
        """Initialize consumer"""
        self.consumer = None
        self.embedding_service = EmbeddingService()
        self.anomaly_detector = AnomalyDetector(self.embedding_service)
        self.remediation_engine = RemediationEngine()
        self.running = False
    
    async def start(self):
        """Start consuming messages"""
        self.consumer = KafkaConsumer(
            settings.KAFKA_TOPIC_METRICS,
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            group_id=settings.KAFKA_GROUP_ID,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            key_deserializer=lambda m: m.decode('utf-8') if m else None,
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            auto_commit_interval_ms=1000,
        )
        
        logger.info(f"Consumer started, listening to topic: {settings.KAFKA_TOPIC_METRICS}")
        self.running = True
        
        # Start consuming in background
        asyncio.create_task(self._consume_loop())
    
    async def _consume_loop(self):
        """Main consumption loop"""
        while self.running:
            try:
                # Poll for messages (non-blocking)
                message_pack = self.consumer.poll(timeout_ms=1000)
                
                for topic_partition, messages in message_pack.items():
                    for message in messages:
                        await self._process_message(message.value)
                
                # Small sleep to prevent busy waiting
                await asyncio.sleep(0.1)
            
            except Exception as e:
                logger.error(f"Error in consume loop: {e}")
                await asyncio.sleep(1)
    
    async def _process_message(self, metric_data: Dict[str, Any]):
        """Process a single metric message"""
        db = SessionLocal()
        
        try:
            logger.debug(f"Processing metric: {metric_data.get('device_id')} - {metric_data.get('metric_type')}")
            
            # Initialize repositories
            metric_repo = MetricRepository(db)
            anomaly_repo = AnomalyRepository(db)
            
            # 1. Save metric to Postgres
            metric = metric_repo.create_metric({
                'device_id': metric_data['device_id'],
                'metric_type': metric_data['metric_type'],
                'value': metric_data['value'],
                'unit': metric_data.get('unit'),
                'timestamp': datetime.fromisoformat(metric_data['timestamp'].replace('Z', '+00:00')),
                'metadata': metric_data.get('metadata', {})
            })
            
            logger.debug(f"Saved metric to database: {metric.id}")
            
            # 2. Generate embedding and index in vector DB
            embedding = self.embedding_service.generate_embedding(
                metric.device_id,
                metric.metric_type,
                metric.value,
                metric.metadata
            )
            
            self.embedding_service.index_metric(
                metric.id,
                metric.device_id,
                metric.metric_type,
                metric.value,
                metric.metadata,
                embedding
            )
            
            logger.debug(f"Indexed metric in vector DB: {metric.id}")
            
            # 3. Detect anomalies using AI
            anomaly_result = self.anomaly_detector.detect_anomaly(
                metric.device_id,
                metric.metric_type,
                metric.value,
                metric.metadata
            )
            
            # 4. Add training sample for ML model
            self.anomaly_detector.add_training_sample(
                metric.metric_type,
                metric.value,
                metric.metadata
            )
            
            # 5. If anomaly detected, save and process
            if anomaly_result['is_anomaly']:
                logger.warning(
                    f"Anomaly detected for metric {metric.id}: "
                    f"score={anomaly_result['anomaly_score']:.2f}, "
                    f"classification={anomaly_result['classification']}"
                )
                
                # Create anomaly record
                anomaly = anomaly_repo.create_anomaly({
                    'metric_id': metric.id,
                    'anomaly_score': anomaly_result['anomaly_score'],
                    'similarity_score': anomaly_result.get('similarity_score'),
                    'classification': anomaly_result.get('classification'),
                    'detected_at': datetime.utcnow()
                })
                
                # Generate alert
                severity = self._determine_severity(anomaly_result['anomaly_score'])
                alert = anomaly_repo.create_alert({
                    'anomaly_id': anomaly.id,
                    'severity': severity,
                    'message': self._generate_alert_message(metric, anomaly_result),
                    'status': 'open'
                })
                
                # Generate remediation suggestion
                remediation_data = self.remediation_engine.generate_remediation(anomaly, metric)
                remediation = anomaly_repo.create_remediation({
                    'anomaly_id': anomaly.id,
                    'suggestion': remediation_data['suggestion'],
                    'reasoning': remediation_data.get('reasoning'),
                    'priority': remediation_data.get('priority', 'medium')
                })
                
                logger.info(
                    f"Created anomaly {anomaly.id} with alert and remediation for metric {metric.id}"
                )
        
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            db.rollback()
        finally:
            db.close()
    
    def _determine_severity(self, anomaly_score: float) -> str:
        """Determine alert severity based on anomaly score"""
        if anomaly_score >= 0.9:
            return "critical"
        elif anomaly_score >= 0.7:
            return "warning"
        else:
            return "info"
    
    def _generate_alert_message(self, metric: DeviceMetric, anomaly_result: Dict) -> str:
        """Generate alert message"""
        classification = anomaly_result.get('classification', 'unknown')
        score = anomaly_result['anomaly_score']
        
        return (
            f"Anomaly detected: {classification} for device {metric.device_id}, "
            f"metric {metric.metric_type} with value {metric.value} "
            f"(score: {score:.2f})"
        )
    
    async def stop(self):
        """Stop consumer"""
        logger.info("Stopping consumer...")
        self.running = False
        
        if self.consumer:
            self.consumer.close()
            logger.info("Consumer stopped")

