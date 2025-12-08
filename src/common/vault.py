"""HashiCorp Vault integration for secrets management"""

import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class VaultClient:
    """HashiCorp Vault client for secrets management"""

    def __init__(self, vault_addr: str, vault_token: str, mount_point: str = "secret"):
        """Initialize Vault client"""
        self.vault_addr = vault_addr.rstrip("/")
        self.vault_token = vault_token
        self.mount_point = mount_point
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize the Vault client"""
        try:
            import hvac

            self.client = hvac.Client(url=self.vault_addr, token=self.vault_token)

            # Verify connection
            if self.client.is_authenticated():
                logger.info(f"Connected to Vault at {self.vault_addr}")
            else:
                logger.error("Failed to authenticate with Vault")
                self.client = None
        except ImportError:
            logger.warning("hvac not installed, Vault integration disabled")
            self.client = None
        except Exception as e:
            logger.error(f"Error initializing Vault client: {e}")
            self.client = None

    def get_secret(self, path: str) -> Optional[Dict]:
        """Retrieve a secret from Vault"""
        if not self.client:
            return None

        try:
            full_path = f"{self.mount_point}/data/{path}"
            response = self.client.secrets.kv.v2.read_secret_version(path=path)

            if response and "data" in response:
                return response["data"].get("data", {})

            return None
        except Exception as e:
            logger.error(f"Error retrieving secret from Vault: {e}")
            return None

    def set_secret(self, path: str, data: Dict) -> bool:
        """Store a secret in Vault"""
        if not self.client:
            return False

        try:
            self.client.secrets.kv.v2.create_or_update_secret(path=path, secret=data)
            logger.info(f"Stored secret in Vault: {path}")
            return True
        except Exception as e:
            logger.error(f"Error storing secret in Vault: {e}")
            return False

    def get_database_credentials(self) -> Optional[Dict]:
        """Get database credentials from Vault"""
        return self.get_secret("database/credentials")

    def get_api_keys(self) -> Optional[Dict]:
        """Get API keys from Vault"""
        return self.get_secret("api/keys")


class SecretsManager:
    """Service for managing secrets via Vault"""

    def __init__(self, vault_client: Optional[VaultClient] = None):
        """Initialize secrets manager"""
        self.vault_client = vault_client

    def get_secret(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get a secret value"""
        if not self.vault_client:
            return default

        # Try to get from Vault
        secrets = self.vault_client.get_secret("application/secrets")
        if secrets and key in secrets:
            return secrets[key]

        return default

    def refresh_credentials(self) -> bool:
        """Refresh credentials from Vault"""
        if not self.vault_client:
            return False

        try:
            db_creds = self.vault_client.get_database_credentials()
            api_keys = self.vault_client.get_api_keys()

            if db_creds:
                logger.info("Refreshed database credentials from Vault")

            if api_keys:
                logger.info("Refreshed API keys from Vault")

            return True
        except Exception as e:
            logger.error(f"Error refreshing credentials: {e}")
            return False
