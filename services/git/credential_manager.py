"""
Git Credential Manager
Securely manages Git credentials for GitHub, GitLab, Bitbucket, etc.
"""
import os
import yaml
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from cryptography.fernet import Fernet
import base64

logger = logging.getLogger(__name__)

class GitCredentialManager:
    """
    Manages Git credentials securely
    Supports: GitHub, GitLab, Bitbucket, Azure DevOps
    """
    
    def __init__(self, config_path: str = "config/git_config.yaml"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.encryption_key = self._get_encryption_key()
        self.cipher = Fernet(self.encryption_key) if self.encryption_key else None
        
        # Auto-sync from environment variables
        self.sync_from_env()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load Git configuration from YAML file"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    config = yaml.safe_load(f)
                    logger.info(f"Loaded Git config from {self.config_path}")
                    return config
            else:
                logger.warning(f"Git config not found at {self.config_path}, using defaults")
                return self._get_default_config()
        except Exception as e:
            logger.error(f"Error loading Git config: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "github": {"enabled": True, "auth_type": "token"},
            "gitlab": {"enabled": True, "auth_type": "token"},
            "bitbucket": {"enabled": True, "auth_type": "token"},
            "git": {
                "default_branch": "main",
                "user": {
                    "name": "AI Orchestrator",
                    "email": "ai-orchestrator@example.com"
                }
            }
        }
    
    def _get_encryption_key(self) -> Optional[bytes]:
        """Get encryption key from environment"""
        key_env = self.config.get("security", {}).get("encryption_key_env", "GIT_ENCRYPTION_KEY")
        key = os.getenv(key_env)
        
        if key:
            # Pad or truncate to 32 bytes for Fernet-compatible key generation via base64
            # Actually Fernet needs exactly 32 bytes URL-safe base64 encoded.
            # If the user provides a raw string, we process it.
            try:
                # Check if it's already a valid Fernet key
                base64.urlsafe_b64decode(key.encode())
                if len(base64.urlsafe_b64decode(key.encode())) == 32:
                    return key.encode()
            except:
                pass
            
            # If not a valid Fernet key, derive one
            return base64.urlsafe_b64encode(key.encode().ljust(32)[:32])
        
        if self.config.get("security", {}).get("encrypt_credentials", True):
            logger.warning("No encryption key found in environment (GIT_ENCRYPTION_KEY). Encryption will be disabled.")
        
        return None
    
    def get_credentials(self, provider: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get credentials for a Git provider
        
        Args:
            provider: github, gitlab, bitbucket, azure_devops
            user_id: Optional user ID to check database for connected account
        
        Returns:
            Dictionary with credentials
        """
        # 1. Try to get from database if user_id is provided
        if user_id:
            try:
                from platform_core.auth.models import ExternalAccount
                from platform_core.auth.encryption import encryption_service
                from platform_core.database import SessionLocal
                
                with SessionLocal() as db:
                    account = db.query(ExternalAccount).filter(
                        ExternalAccount.user_id == user_id,
                        ExternalAccount.provider == provider
                    ).first()
                    
                    if account:
                        decrypted_token = encryption_service.decrypt(account.access_token)
                        return {
                            "type": "token",
                            "token": decrypted_token,
                            "username": account.username,
                            "api_url": self._get_default_api_url(provider)
                        }
            except Exception as e:
                logger.error(f"Failed to fetch credentials from DB for user {user_id}: {e}")

        # 2. Fallback to config and environment variables
        provider_config = self.config.get(provider, {})
        
        if not provider_config.get("enabled", False):
            raise ValueError(f"Provider {provider} is not enabled")
        
        auth_type = provider_config.get("auth_type", "token")
        credentials = provider_config.get("credentials", {})
        
        # Try to get credentials from environment variables first
        if provider == "github":
            token = os.getenv("GITHUB_TOKEN") or credentials.get("token", "")
            return {
                "type": auth_type,
                "token": token,
                "api_url": provider_config.get("api_url", "https://api.github.com")
            }
        
        elif provider == "gitlab":
            token = os.getenv("GITLAB_TOKEN") or credentials.get("token", "")
            return {
                "type": auth_type,
                "token": token,
                "api_url": provider_config.get("api_url", "https://gitlab.com/api/v4")
            }
        
        elif provider == "bitbucket":
            username = credentials.get("username", "")
            app_password = os.getenv("BITBUCKET_TOKEN") or os.getenv("BITBUCKET_APP_PASSWORD") or credentials.get("app_password", "")
            return {
                "type": auth_type,
                "username": username,
                "app_password": app_password,
                "api_url": provider_config.get("api_url", "https://api.bitbucket.org/2.0")
            }
        
        elif provider == "azure_devops":
            token = os.getenv("AZURE_DEVOPS_TOKEN") or credentials.get("personal_access_token", "")
            return {
                "type": auth_type,
                "token": token,
                "organization": provider_config.get("organization", ""),
                "api_url": provider_config.get("api_url", "https://dev.azure.com")
            }
        
        else:
            raise ValueError(f"Unknown provider: {provider}")
    
    def sync_from_env(self):
        """Sync credentials from environment variables to config file"""
        env_map = {
            "github": {
                "token": "GITHUB_TOKEN",
                "username": "GITHUB_USERNAME"
            },
            "gitlab": {
                "token": "GITLAB_TOKEN",
                "username": "GITLAB_USERNAME"
            },
            "bitbucket": {
                "app_password": ["BITBUCKET_TOKEN", "BITBUCKET_APP_PASSWORD"],
                "username": "BITBUCKET_USERNAME"
            }
        }
        
        changed = False
        for provider, mapping in env_map.items():
            if provider not in self.config:
                self.config[provider] = {"enabled": True, "auth_type": "token", "credentials": {}}
            
            if "credentials" not in self.config[provider]:
                self.config[provider]["credentials"] = {}
            
            for config_key, env_key in mapping.items():
                env_vals = []
                if isinstance(env_key, list):
                    for k in env_key:
                        val = os.getenv(k)
                        if val: env_vals.append(val)
                else:
                    val = os.getenv(env_key)
                    if val: env_vals.append(val)
                
                if env_vals:
                    # Sensitive values should be encrypted
                    val_to_store = env_vals[0]
                    
                    # Check if it needs encryption
                    should_encrypt = self.config.get("security", {}).get("encrypt_credentials", True)
                    sensitive_fields = ["token", "app_password", "client_secret", "ssh_passphrase", "personal_access_token"]
                    
                    if should_encrypt and config_key in sensitive_fields and self.cipher:
                        encrypted_val = self.cipher.encrypt(val_to_store.encode()).decode()
                        if self.config[provider]["credentials"].get(config_key) != encrypted_val:
                            # Also check if the current value in config is the decrypted version of what we have
                            current_encrypted = self.config[provider]["credentials"].get(config_key)
                            already_correct = False
                            if current_encrypted:
                                try:
                                    if self.cipher.decrypt(current_encrypted.encode()).decode() == val_to_store:
                                        already_correct = True
                                except:
                                    pass
                            
                            if not already_correct:
                                self.config[provider]["credentials"][config_key] = encrypted_val
                                changed = True
                    else:
                        if self.config[provider]["credentials"].get(config_key) != val_to_store:
                            self.config[provider]["credentials"][config_key] = val_to_store
                            changed = True
        
        if changed:
            logger.info("Syncing Git credentials from environment to config")
            self._save_config()
    
    def set_credentials(self, provider: str, credentials: Dict[str, Any]) -> bool:
        """
        Set credentials for a Git provider
        
        Args:
            provider: github, gitlab, bitbucket, azure_devops
            credentials: Dictionary with credentials
        
        Returns:
            True if successful
        """
        try:
            if provider not in self.config:
                self.config[provider] = {}
            
            # Encrypt sensitive data if enabled
            if self.cipher and self.config.get("security", {}).get("encrypt_credentials", True):
                credentials = self._encrypt_credentials(credentials)
            
            self.config[provider]["credentials"] = credentials
            self._save_config()
            
            logger.info(f"Credentials set for {provider}")
            return True
        
        except Exception as e:
            logger.error(f"Error setting credentials for {provider}: {e}")
            return False
    
    def _encrypt_credentials(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """Encrypt sensitive credential fields"""
        encrypted = {}
        sensitive_fields = ["token", "app_password", "client_secret", "ssh_passphrase", "personal_access_token"]
        
        for key, value in credentials.items():
            if key in sensitive_fields and value:
                encrypted[key] = self.cipher.encrypt(value.encode()).decode()
            else:
                encrypted[key] = value
        
        return encrypted
    
    def _decrypt_credentials(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """Decrypt sensitive credential fields"""
        decrypted = {}
        sensitive_fields = ["token", "app_password", "client_secret", "ssh_passphrase", "personal_access_token"]
        
        for key, value in credentials.items():
            if key in sensitive_fields and value:
                try:
                    decrypted[key] = self.cipher.decrypt(value.encode()).decode()
                except:
                    decrypted[key] = value  # Already decrypted or invalid
            else:
                decrypted[key] = value
        
        return decrypted
    
    def _save_config(self):
        """Save configuration to file"""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False)
            logger.info(f"Saved Git config to {self.config_path}")
        except Exception as e:
            logger.error(f"Error saving Git config: {e}")
    
    def validate_credentials(self, provider: str) -> bool:
        """
        Validate credentials for a provider
        
        Args:
            provider: github, gitlab, bitbucket, azure_devops
        
        Returns:
            True if credentials are valid
        """
        try:
            credentials = self.get_credentials(provider)
            
            # Basic validation
            if provider == "github":
                return bool(credentials.get("token"))
            elif provider == "gitlab":
                return bool(credentials.get("token"))
            elif provider == "bitbucket":
                return bool(credentials.get("username") and credentials.get("app_password"))
            elif provider == "azure_devops":
                return bool(credentials.get("token") and credentials.get("organization"))
            
            return False
        
        except Exception as e:
            logger.error(f"Error validating credentials for {provider}: {e}")
            return False
    
    def list_providers(self) -> Dict[str, bool]:
        """List all providers and their status"""
        providers = {}
        
        for provider in ["github", "gitlab", "bitbucket", "azure_devops"]:
            providers[provider] = {
                "enabled": self.config.get(provider, {}).get("enabled", False),
                "configured": self.validate_credentials(provider)
            }
        
    def get_git_config(self) -> Dict[str, Any]:
        """Get general Git configuration"""
        return self.config.get("git", {
            "default_branch": "main",
            "user": {
                "name": "AI Orchestrator",
                "email": "ai-orchestrator@example.com"
            }
        })

    def _get_default_api_url(self, provider: str) -> str:
        """Helper to get default API URL for provider"""
        urls = {
            "github": "https://api.github.com",
            "gitlab": "https://gitlab.com/api/v4",
            "bitbucket": "https://api.bitbucket.org/2.0",
            "azure_devops": "https://dev.azure.com"
        }
        return urls.get(provider, "")
