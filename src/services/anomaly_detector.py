"""AI-powered anomaly detection and classification"""

import logging
from typing import Dict, Optional, Tuple

import numpy as np
from sklearn.ensemble import IsolationForest

from src.api.config import settings
from src.services.embeddings import EmbeddingService

logger = logging.getLogger(__name__)


class AnomalyDetector:
    """AI-powered anomaly detection service"""

    def __init__(self, embedding_service: EmbeddingService):
        """Initialize anomaly detector"""
        self.embedding_service = embedding_service
        self.isolation_forest = IsolationForest(
            contamination=0.1, random_state=42, n_estimators=100  # Expect 10% anomalies
        )
        self.is_trained = False
        self._metric_buffer = []  # Buffer for training

    def _extract_features(self, metric_type: str, value: float, metadata: dict) -> np.ndarray:
        """Extract features from metric for ML model"""
        # Create feature vector from metric
        features = [value]

        # Add metadata features if present
        if metadata:
            # Common metadata fields
            for key in ["cpu_cores", "memory_gb", "disk_gb", "network_speed"]:
                if key in metadata:
                    features.append(float(metadata[key]))
                else:
                    features.append(0.0)
        else:
            features.extend([0.0] * 4)

        # Add metric type encoding (simple hash)
        type_hash = hash(metric_type) % 1000 / 1000.0
        features.append(type_hash)

        return np.array(features)

    def add_training_sample(self, metric_type: str, value: float, metadata: dict):
        """Add a sample to training buffer"""
        features = self._extract_features(metric_type, value, metadata)
        self._metric_buffer.append(features)

        # Auto-train when buffer reaches threshold
        if len(self._metric_buffer) >= 100 and not self.is_trained:
            self.train()

    def train(self):
        """Train the anomaly detection model"""
        if len(self._metric_buffer) < 50:
            logger.warning("Not enough samples for training, skipping")
            return

        try:
            X = np.array(self._metric_buffer)
            self.isolation_forest.fit(X)
            self.is_trained = True
            logger.info(f"Anomaly detector trained on {len(self._metric_buffer)} samples")
        except Exception as e:
            logger.error(f"Error training anomaly detector: {e}")

    def detect_anomaly(
        self, device_id: str, metric_type: str, value: float, metadata: dict = None
    ) -> Dict:
        """
        Detect if a metric is anomalous

        Returns:
            Dict with anomaly detection results
        """
        metadata = metadata or {}

        # 1. Check similarity to known anomalies using embeddings
        (
            is_similar,
            similarity_score,
            similar_anomaly,
        ) = self.embedding_service.is_similar_to_anomaly(device_id, metric_type, value, metadata)

        # 2. Use ML model for anomaly scoring
        ml_score = 0.5  # Default neutral score
        if self.is_trained:
            try:
                features = self._extract_features(metric_type, value, metadata)
                # IsolationForest returns -1 for anomaly, 1 for normal
                prediction = self.isolation_forest.predict([features])[0]
                anomaly_score_raw = self.isolation_forest.score_samples([features])[0]

                # Convert to 0-1 scale where 1 is more anomalous
                ml_score = 1 - ((anomaly_score_raw + 1) / 2)
            except Exception as e:
                logger.error(f"Error in ML anomaly detection: {e}")

        # 3. Combine similarity and ML scores
        # Weight: 60% similarity, 40% ML score
        combined_score = (similarity_score * 0.6) + (ml_score * 0.4)

        # 4. Classify anomaly type
        classification = self._classify_anomaly(
            metric_type, value, metadata, similarity_score, ml_score
        )

        is_anomaly = combined_score >= 0.7 or is_similar

        return {
            "is_anomaly": is_anomaly,
            "anomaly_score": float(combined_score),
            "similarity_score": float(similarity_score) if is_similar else None,
            "ml_score": float(ml_score),
            "classification": classification,
            "similar_anomaly": similar_anomaly,
        }

    def _classify_anomaly(
        self,
        metric_type: str,
        value: float,
        metadata: dict,
        similarity_score: float,
        ml_score: float,
    ) -> str:
        """Classify the type of anomaly"""
        # Rule-based classification with AI enhancement
        classification_rules = {
            "spike": value > 90,  # High value spike
            "drop": value < 10,  # Low value drop
            "outlier": ml_score > 0.8,  # Statistical outlier
            "similar_anomaly": similarity_score > 0.85,  # Similar to known anomaly
        }

        # Determine classification based on rules
        if classification_rules.get("similar_anomaly"):
            return "known_pattern"
        elif classification_rules.get("spike"):
            return "value_spike"
        elif classification_rules.get("drop"):
            return "value_drop"
        elif classification_rules.get("outlier"):
            return "statistical_outlier"
        else:
            return "unknown_anomaly"
