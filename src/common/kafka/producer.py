"""Kafka producer for metrics"""

import json
import logging
from typing import Any, Dict

from confluent_kafka import Producer

from src.api.config import settings

logger = logging.getLogger(__name__)


class KafkaProducer:
    """Kafka producer for device metrics"""

    def __init__(self):
        """Initialize Kafka producer"""
        self.producer = None
        self.topic = settings.KAFKA_TOPIC_METRICS

    async def connect(self):
        """Initialize producer connection"""
        config = {
            "bootstrap.servers": settings.KAFKA_BOOTSTRAP_SERVERS,
            "client.id": "device-metrics-producer",
            "acks": "all",  # Wait for all replicas
            "retries": 3,
            "max.in.flight.requests.per.connection": 1,
        }
        self.producer = Producer(config)
        logger.info(f"Kafka producer connected to {settings.KAFKA_BOOTSTRAP_SERVERS}")

    async def send_metric(self, metric_data: Dict[str, Any]):
        """Send a metric to Kafka topic"""
        if not self.producer:
            await self.connect()

        try:
            # Serialize metric data
            message_value = json.dumps(metric_data, default=str)

            # Use device_id as key for partitioning
            key = metric_data.get("device_id", "unknown")

            # Produce message
            self.producer.produce(
                self.topic, key=key, value=message_value, callback=self._delivery_callback
            )

            # Poll to handle delivery callbacks
            self.producer.poll(0)

        except Exception as e:
            logger.error(f"Error producing message to Kafka: {e}")
            raise

    def _delivery_callback(self, err, msg):
        """Callback for message delivery"""
        if err:
            logger.error(f"Message delivery failed: {err}")
        else:
            logger.debug(
                f"Message delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}"
            )

    async def close(self):
        """Close producer connection"""
        if self.producer:
            # Wait for all messages to be delivered
            self.producer.flush(timeout=10)
            logger.info("Kafka producer closed")
