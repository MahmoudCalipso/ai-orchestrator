"""
Security Manager - Handles authentication and authorization
"""
import logging
import hashlib
import secrets
import os
from typing import Optional
from datetime import datetime, timedelta
from fastapi import HTTPException, Header, Depends
from sqlalchemy.orm import Session
from platform_core.auth.dependencies import get_db

logger = logging.getLogger(__name__)



class JWTManager:
    """Mock JWT Manager for schema extraction"""
    def __init__(self):
        self.access_token_expire = 30
    def hash_password(self, p): return "hash"
    def verify_password(self, p, h): return True
    def create_access_token(self, d): return "token"
    def create_refresh_token(self, u, t): return "refresh"
    def generate_api_key(self): return "key"
    def hash_api_key(self, k): return "hash"
    def revoke_token(self, t): pass
    def verify_token(self, t, type): return {"sub": "user", "tenant_id": "tenant"}

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
                "user_id": "admin-001",
                "username": "admin",
                "role": "admin", # SuperUser
                "created_at": datetime.now(),
                "rate_limit": 10000
            }
            logger.info("Default Admin API key loaded from environment")
        else:
            logger.warning("No DEFAULT_API_KEY environment variable set. API key required for all requests.")

    def get_user_info(self, api_key: str, db: Optional[Session] = None) -> Optional[dict]:
        """Get user info associated with an API key (Local cache or DB)"""
        # 1. Check local cache (Admin/Env keys)
        if api_key in self.api_keys:
            return self.api_keys[api_key]
            
        # 2. Check Database
        if db:
            from platform_core.auth.models import APIKey
            from platform_core.auth.jwt_manager import JWTManager
            
            # This is hash based lookup - optimization: cache this
            jwt_mgr = JWTManager()
            key_hash = jwt_mgr.hash_api_key(api_key)
            
            record = db.query(APIKey).filter(
                APIKey.key_hash == key_hash, 
                APIKey.is_active == True
            ).first()
            
            if record:
                # Return standardized user info dict
                return {
                    "user_id": record.user.id,
                    "username": record.user.email,
                    "email": record.user.email,
                    "role": record.user.role,
                    "org_id": record.user.tenant_id, # Using tenant_id as org_id
                    "tenant_id": record.user.tenant_id,
                    "source": "database"
                }

        return None

    def is_superuser(self, api_key: str, db: Optional[Session] = None) -> bool:
        """Check if the user is a SuperUser"""
        user_info = self.get_user_info(api_key, db)
        return user_info and user_info.get("role") == Role.ADMIN.value

    def verify_api_key(self, api_key: str, db: Optional[Session] = None) -> bool:
        """
        Verify an API key. 
        Checks local cache (env keys) first, then database if provided.
        """
        # 1. Check legacy/env keys
        if api_key in self.api_keys:
            return True
            
        # 2. Check Database if available
        if db:
            from platform_core.auth.jwt_manager import JWTManager
            from platform_core.auth.models import APIKey
            
            jwt_manager = JWTManager()
            key_hash = jwt_manager.hash_api_key(api_key)
            
            api_key_record = db.query(APIKey).filter(
                APIKey.key_hash == key_hash,
                APIKey.is_active == True
            ).first()
            
            if api_key_record:
                if api_key_record.expires_at and api_key_record.expires_at < datetime.now():
                    return False
                return True
                
        return False

    def check_rate_limit(self, api_key: str) -> bool:
        """Check if request is within rate limits"""
        # Placeholder implementation
        return True
        

# Dependency for FastAPI
async def verify_api_key(
    x_api_key: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> str:
    """Verify API key from header, supporting both ENV and DB keys"""
    if not x_api_key:
        raise HTTPException(
            status_code=401,
            detail="API key required. Provide X-API-Key header."
        )

    security_manager = SecurityManager()
    
    if not security_manager.verify_api_key(x_api_key, db=db):
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired API key"
        )
        
    return x_api_key


# RBAC System
from enum import Enum

class Role(str, Enum):
    ADMIN = "admin"
    ENTERPRISE = "enterprises"
    DEVELOPER = "developer"

def require_role(allowed_roles: list[Role]):
    """
    Dependency to enforce role-based access control.
    SuperUser (Admin) always has access.
    Returns user_info dict.
    """
    def _check_role(
        api_key: str = Depends(verify_api_key),
        db: Session = Depends(get_db)
    ):
        security_manager = SecurityManager()
        user_info = security_manager.get_user_info(api_key, db)
        
        if not user_info:
             raise HTTPException(status_code=401, detail="User not found")
             
        user_role = user_info.get("role")
        
        # Super Admin Bypass
        if user_role == Role.ADMIN.value:
            return user_info
            
        # Check permissions
        if user_role not in [r.value for r in allowed_roles]:
             raise HTTPException(
                 status_code=403, 
                 detail=f"Insufficient permissions. Required: {[r.value for r in allowed_roles]}"
             )
             
        return user_info
        
    return _check_role