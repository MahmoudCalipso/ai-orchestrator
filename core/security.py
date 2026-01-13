"""
Security Manager - Handles authentication and authorization
"""
import logging
import hashlib
import secrets
import os
from typing import Optional
from datetime import datetime, timedelta
from fastapi import HTTPException, Header

logger = logging.getLogger(__name__)


class SecurityManager:
    """Manages security, authentication, and authorization"""
    
    def __init__(self):
        self.api_keys = {}
        self.rate_limits = {}
        self.audit_log = []
        
        # Initialize with environment variable or require API key
        # IMPORTANT: Do NOT hardcode keys in source code
        # Use environment variables for initial setup
        default_key = os.getenv("DEFAULT_API_KEY", "")
        if default_key:
            self.api_keys[default_key] = {
                "user": "admin",
                "role": "admin",
                "created_at": datetime.now(),
                "rate_limit": 1000
            }
            logger.info("Default API key loaded from environment")
        else:
            logger.warning("No DEFAULT_API_KEY environment variable set. API key required for all requests.")

    # ...existing code...

    def verify_api_key(self, api_key: str) -> bool:
        """Verify an API key"""
        return api_key in self.api_keys
        
    # ...existing code...


# Dependency for FastAPI
async def verify_api_key(x_api_key: Optional[str] = Header(None)) -> str:
    """Verify API key from header"""
    
    # SECURITY FIX: Require API key in all cases
    # Do not allow requests without authentication
    if not x_api_key:
        raise HTTPException(
            status_code=401,
            detail="API key required. Provide X-API-Key header."
        )

    security_manager = SecurityManager()
    
    if not security_manager.verify_api_key(x_api_key):
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )
        
    if not security_manager.check_rate_limit(x_api_key):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded"
        )
        
    return x_api_key