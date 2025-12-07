"""Object storage integration for metric archives"""
from typing import Optional, List, Dict
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class ObjectStorageClient:
    """Abstract interface for object storage (S3/MinIO compatible)"""
    
    def __init__(self, endpoint: str, access_key: str, secret_key: str, 
                 bucket: str, use_ssl: bool = True):
        """Initialize object storage client"""
        self.endpoint = endpoint
        self.access_key = access_key
        self.secret_key = secret_key
        self.bucket = bucket
        self.use_ssl = use_ssl
        self.client = None
    
    def _initialize_client(self):
        """Initialize the storage client (S3-compatible)"""
        try:
            import boto3
            from botocore.client import Config
            
            self.client = boto3.client(
                's3',
                endpoint_url=self.endpoint,
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                use_ssl=self.use_ssl,
                config=Config(signature_version='s3v4')
            )
            logger.info(f"Initialized object storage client: {self.endpoint}")
        except ImportError:
            logger.warning("boto3 not installed, object storage disabled")
            self.client = None
        except Exception as e:
            logger.error(f"Error initializing object storage: {e}")
            self.client = None
    
    def archive_metrics(self, device_id: str, metrics_data: bytes, 
                       timestamp: str) -> Optional[str]:
        """Archive metrics data to object storage"""
        if not self.client:
            self._initialize_client()
        
        if not self.client:
            return None
        
        try:
            key = f"metrics/{device_id}/{timestamp}.json.gz"
            self.client.put_object(
                Bucket=self.bucket,
                Key=key,
                Body=metrics_data,
                ContentType='application/gzip'
            )
            logger.info(f"Archived metrics to {key}")
            return key
        except Exception as e:
            logger.error(f"Error archiving metrics: {e}")
            return None
    
    def retrieve_archived_metrics(self, key: str) -> Optional[bytes]:
        """Retrieve archived metrics from object storage"""
        if not self.client:
            self._initialize_client()
        
        if not self.client:
            return None
        
        try:
            response = self.client.get_object(Bucket=self.bucket, Key=key)
            return response['Body'].read()
        except Exception as e:
            logger.error(f"Error retrieving archived metrics: {e}")
            return None
    
    def list_archives(self, device_id: Optional[str] = None, 
                     prefix: Optional[str] = None) -> list:
        """List archived metric files"""
        if not self.client:
            self._initialize_client()
        
        if not self.client:
            return []
        
        try:
            search_prefix = prefix or f"metrics/{device_id}/" if device_id else "metrics/"
            response = self.client.list_objects_v2(
                Bucket=self.bucket,
                Prefix=search_prefix
            )
            
            keys = [obj['Key'] for obj in response.get('Contents', [])]
            return keys
        except Exception as e:
            logger.error(f"Error listing archives: {e}")
            return []


class StorageService:
    """Service for managing metric archives in object storage"""
    
    def __init__(self, storage_client: Optional[ObjectStorageClient] = None):
        """Initialize storage service"""
        self.storage_client = storage_client
    
    def archive_old_metrics(self, device_id: str, metrics: list, 
                           retention_days: int = 90) -> Optional[str]:
        """Archive metrics older than retention period"""
        if not self.storage_client:
            return None
        
        try:
            import json
            import gzip
            from datetime import datetime
            
            # Filter old metrics
            cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
            old_metrics = [
                m for m in metrics 
                if datetime.fromisoformat(m['timestamp'].replace('Z', '+00:00')) < cutoff_date
            ]
            
            if not old_metrics:
                return None
            
            # Compress and archive
            data = json.dumps(old_metrics).encode('utf-8')
            compressed = gzip.compress(data)
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            
            key = self.storage_client.archive_metrics(
                device_id, compressed, timestamp
            )
            return key
        except Exception as e:
            logger.error(f"Error archiving old metrics: {e}")
            return None

