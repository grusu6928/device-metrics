"""Kafka consumer service"""
from src.consumer.consumer import MetricsConsumer
from src.consumer.main import main

__all__ = ["MetricsConsumer", "main"]

