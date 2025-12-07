"""Embedding service for similarity detection"""
import json
import numpy as np
from typing import List, Dict, Optional, Tuple
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from src.api.config import settings
import logging

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating embeddings and similarity search"""
    
    def __init__(self):
        """Initialize embedding service"""
        logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL}")
        self.model = SentenceTransformer(settings.EMBEDDING_MODEL)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        
        # Initialize Qdrant client
        self.qdrant_client = QdrantClient(
            host=settings.QDRANT_HOST,
            port=settings.QDRANT_PORT
        )
        
        # Ensure collection exists
        self._ensure_collection()
    
    def _ensure_collection(self):
        """Ensure Qdrant collection exists"""
        try:
            collections = self.qdrant_client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if settings.QDRANT_COLLECTION not in collection_names:
                logger.info(f"Creating Qdrant collection: {settings.QDRANT_COLLECTION}")
                self.qdrant_client.create_collection(
                    collection_name=settings.QDRANT_COLLECTION,
                    vectors_config=VectorParams(
                        size=self.embedding_dim,
                        distance=Distance.COSINE
                    )
                )
        except Exception as e:
            logger.error(f"Error ensuring collection exists: {e}")
            raise
    
    def _create_metric_text(self, device_id: str, metric_type: str, value: float, 
                           metadata: dict) -> str:
        """Create a text representation of a metric for embedding"""
        # Create a structured text representation
        text_parts = [
            f"device: {device_id}",
            f"metric_type: {metric_type}",
            f"value: {value}",
        ]
        
        # Add metadata if present
        if metadata:
            for key, val in metadata.items():
                text_parts.append(f"{key}: {val}")
        
        return " | ".join(text_parts)
    
    def generate_embedding(self, device_id: str, metric_type: str, value: float,
                          metadata: dict = None) -> np.ndarray:
        """Generate embedding for a metric"""
        text = self._create_metric_text(device_id, metric_type, value, metadata or {})
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding
    
    def index_metric(self, metric_id: int, device_id: str, metric_type: str,
                    value: float, metadata: dict = None, embedding: np.ndarray = None):
        """Index a metric in the vector database"""
        if embedding is None:
            embedding = self.generate_embedding(device_id, metric_type, value, metadata)
        
        payload = {
            "metric_id": metric_id,
            "device_id": device_id,
            "metric_type": metric_type,
            "value": float(value),
            "metadata": metadata or {}
        }
        
        try:
            self.qdrant_client.upsert(
                collection_name=settings.QDRANT_COLLECTION,
                points=[
                    PointStruct(
                        id=metric_id,
                        vector=embedding.tolist(),
                        payload=payload
                    )
                ]
            )
            logger.debug(f"Indexed metric {metric_id} in vector DB")
        except Exception as e:
            logger.error(f"Error indexing metric {metric_id}: {e}")
            raise
    
    def find_similar_anomalies(self, device_id: str, metric_type: str, value: float,
                               metadata: dict = None, limit: int = 5,
                               score_threshold: float = None) -> List[Tuple[Dict, float]]:
        """
        Find similar anomalies using vector similarity search
        
        Returns:
            List of tuples: (metric_data, similarity_score)
        """
        # Generate query embedding
        query_embedding = self.generate_embedding(device_id, metric_type, value, metadata)
        
        # Search for similar vectors
        try:
            search_results = self.qdrant_client.search(
                collection_name=settings.QDRANT_COLLECTION,
                query_vector=query_embedding.tolist(),
                limit=limit,
                score_threshold=score_threshold or settings.ANOMALY_THRESHOLD
            )
            
            similar_metrics = []
            for result in search_results:
                similar_metrics.append((
                    result.payload,
                    1 - result.score  # Convert distance to similarity (cosine distance)
                ))
            
            return similar_metrics
        except Exception as e:
            logger.error(f"Error searching for similar anomalies: {e}")
            return []
    
    def is_similar_to_anomaly(self, device_id: str, metric_type: str, value: float,
                              metadata: dict = None) -> Tuple[bool, float, Optional[Dict]]:
        """
        Check if a metric is similar to known anomalies
        
        Returns:
            Tuple of (is_similar, similarity_score, most_similar_anomaly)
        """
        similar = self.find_similar_anomalies(
            device_id, metric_type, value, metadata, limit=1
        )
        
        if not similar:
            return False, 0.0, None
        
        metric_data, similarity_score = similar[0]
        is_similar = similarity_score >= settings.ANOMALY_THRESHOLD
        
        return is_similar, similarity_score, metric_data

