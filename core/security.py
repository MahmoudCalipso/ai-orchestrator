"""
Security Manager - Handles authentication and authorization
"""
import logging
import hashlib
import secrets
import os
import time
from typing import Optional
from datetime import datetime, timedelta
from fastapi import HTTPException, Header, Depends
from dotenv import load_dotenv

# Load .env file
load_dotenv()
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from platform_core.auth.dependencies import get_db
from platform_core.auth.rbac import Role

logger = logging.getLogger(__name__)



import jwt
# Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "super-secret-key-2026")
JWT_ALGORITHM = "HS256"

class JWTManager:
    """Production JWT Manager for secure token operations"""
    def __init__(self):
        self.access_token_expire = 30 # minutes
        self.refresh_token_expire = 7 # days
        self.secret_key = JWT_SECRET_KEY

    def hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def verify_password(self, password: str, hashed: str) -> bool:
        return self.hash_password(password) == hashed

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        expire = datetime.utcnow() + (expires_delta or timedelta(minutes=self.access_token_expire))
        to_encode = data.copy()
        to_encode.update({
            "exp": expire.timestamp(),
            "type": "access",
            "iat": datetime.utcnow().timestamp()
        })
        return jwt.encode(to_encode, self.secret_key, algorithm=JWT_ALGORITHM)

    def create_refresh_token(self, user_id: str, tenant_id: str) -> str:
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire)
        to_encode = {
            "sub": user_id,
            "tenant_id": tenant_id,
            "exp": expire.timestamp(),
            "type": "refresh",
            "iat": datetime.utcnow().timestamp()
        }
        return jwt.encode(to_encode, self.secret_key, algorithm=JWT_ALGORITHM)

    def generate_api_key(self) -> str:
        return f"ak_{secrets.token_hex(24)}"

    def hash_api_key(self, api_key: str) -> str:
        return hashlib.sha256(api_key.encode()).hexdigest()

    def revoke_token(self, token: str):
        # Implementation for token blacklisting in Redis would go here
        pass

    def verify_token(self, token: str, token_type: str = "access") -> Optional[dict]:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[JWT_ALGORITHM])
            if payload.get("type") != token_type:
                return None
            if payload.get("exp") < datetime.utcnow().timestamp():
                return None
            return payload
        except Exception:
            return None

# Global instances for optimization
_security_manager = None

def get_security_manager():
    global _security_manager
    if _security_manager is None:
        _security_manager = SecurityManager()
    return _security_manager

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

    async def get_user_info(self, api_key: str, db: Optional[AsyncSession] = None) -> Optional[dict]:
        """Get user info associated with an API key (Local cache or DB)"""
        # 1. Check local cache (Admin/Env keys)
        if api_key in self.api_keys:
            return self.api_keys[api_key]
            
        # 2. Check Database
        if db:
            from platform_core.auth.models import APIKey
            
            key_hash = self.hash_api_key(api_key)
            
            result = await db.execute(
                select(APIKey).where(
                    APIKey.key_hash == key_hash, 
                    APIKey.is_active == True
                )
            )
            record = result.scalar_one_or_none()
            
            if record:
                # Return standardized user info dict
                return {
                    "user_id": record.user_id,
                    "username": record.user.email,
                    "email": record.user.email,
                    "role": record.user.role,
                    "tenant_id": record.user.tenant_id,
                    "source": "database"
                }

        return None

    async def is_superuser(self, api_key: str, db: Optional[AsyncSession] = None) -> bool:
        """Check if the user is a SuperUser"""
        user_info = await self.get_user_info(api_key, db)
        return user_info and user_info.get("role") == Role.ADMIN.value

    async def verify_api_key(self, api_key: str, db: Optional[AsyncSession] = None) -> bool:
        """
        Verify an API key. 
        Checks local cache (env keys) first, then database if provided.
        """
        # 1. Check legacy/env keys
        if api_key in self.api_keys:
            return True
            
        # 2. Check Database if available
        if db:
            from platform_core.auth.models import APIKey
            
            key_hash = self.hash_api_key(api_key)
            
            result = await db.execute(
                select(APIKey).where(
                    APIKey.key_hash == key_hash,
                    APIKey.is_active == True
                )
            )
            api_key_record = result.scalar_one_or_none()
            
            if api_key_record:
                if api_key_record.expires_at and api_key_record.expires_at < datetime.utcnow():
                    return False
                return True
                
        return False

    async def check_rate_limit(self, api_key: str, limit: int = 1000, window_seconds: int = 3600) -> bool:
        """
        Check if request is within rate limits using a sliding window algorithm in Redis.
        Default: 1000 requests per hour.
        """
        if not unified_db.redis:
            logger.warning("Redis not available for rate limiting. Bypassing check.")
            return True

        try:
            # Get user info for custom limits
            user_info = self.api_keys.get(api_key)
            if user_info:
                limit = user_info.get("rate_limit", limit)

            key = f"rate_limit:{api_key}"
            now = time.time()
            
            async with unified_db.redis.pipeline(transaction=True) as pipe:
                # Remove older records outside the window
                pipe.zremrangebyscore(key, 0, now - window_seconds)
                # Count remaining records
                pipe.zcard(key)
                # Add current request
                pipe.zadd(key, {str(now): now})
                # Set expiration to clean up the set eventually
                pipe.expire(key, window_seconds)
                
                results = await pipe.execute()
                current_count = results[1]

            return current_count < limit

        except Exception as e:
            logger.error(f"Rate limiting check failed: {e}")
            return True # Fail-open in production for continuity
        

# Dependency for FastAPI
async def verify_api_key(
    x_api_key: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db)
) -> str:
    """Verify API key from header, supporting both ENV and DB keys"""
    if not x_api_key:
        raise HTTPException(
            status_code=401,
            detail="API key required. Provide X-API-Key header."
        )

    security_manager = get_security_manager()
    
    if not await security_manager.verify_api_key(x_api_key, db=db):
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired API key"
        )
        
    return x_api_key


# RBAC System

def require_role(allowed_roles: list[Role]):
    """
    Dependency to enforce role-based access control.
    SuperUser (Admin) always has access.
    Returns user_info dict.
    """
    async def _check_role(
        api_key: str = Depends(verify_api_key),
        db: AsyncSession = Depends(get_db)
    ):
        security_manager = get_security_manager()
        user_info = await security_manager.get_user_info(api_key, db)
        
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