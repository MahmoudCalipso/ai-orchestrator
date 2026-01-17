"""
JWT Token Manager
Handle JWT token generation, validation, and refresh
"""

import os
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
import redis
import secrets


class JWTManager:
    """Production-grade JWT authentication manager"""
    
    def __init__(self):
        self.secret_key = os.getenv("JWT_SECRET_KEY")
        if not self.secret_key:
            raise ValueError("JWT_SECRET_KEY environment variable is required")
        
        self.algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        self.access_token_expire = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
        self.refresh_token_expire = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
        
        # Password hashing
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        # Redis for refresh token storage
        redis_host = os.getenv("REDIS_HOST", "localhost")
        redis_port = int(os.getenv("REDIS_PORT", "6379"))
        redis_db = int(os.getenv("REDIS_DB_AUTH", "0"))
        
        self.redis_client = redis.Redis(
            host=redis_host,
            port=redis_port,
            db=redis_db,
            decode_responses=True
        )
    
    def create_access_token(self, data: Dict[str, Any]) -> str:
        """
        Create JWT access token
        
        Args:
            data: Token payload (should include 'sub' for user_id)
            
        Returns:
            Encoded JWT token
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire)
        to_encode.update({
            "exp": expire,
            "type": "access",
            "iat": datetime.utcnow()
        })
        
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    def create_refresh_token(self, user_id: str, tenant_id: str) -> str:
        """
        Create JWT refresh token and store in Redis
        
        Args:
            user_id: User ID
            tenant_id: Tenant ID
            
        Returns:
            Encoded JWT refresh token
        """
        to_encode = {
            "sub": user_id,
            "tenant_id": tenant_id,
            "type": "refresh",
            "jti": secrets.token_urlsafe(32)  # Unique token ID
        }
        
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire)
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow()
        })
        
        token = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        
        # Store refresh token in Redis with expiration
        redis_key = f"refresh_token:{user_id}:{to_encode['jti']}"
        self.redis_client.setex(
            redis_key,
            timedelta(days=self.refresh_token_expire),
            token
        )
        
        return token
    
    def verify_token(self, token: str, token_type: str = "access") -> Dict[str, Any]:
        """
        Verify and decode JWT token
        
        Args:
            token: JWT token to verify
            token_type: Expected token type ('access' or 'refresh')
            
        Returns:
            Decoded token payload
            
        Raises:
            JWTError: If token is invalid or expired
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Verify token type
            if payload.get("type") != token_type:
                raise JWTError(f"Invalid token type. Expected {token_type}")
            
            # For refresh tokens, verify it exists in Redis
            if token_type == "refresh":
                user_id = payload.get("sub")
                jti = payload.get("jti")
                redis_key = f"refresh_token:{user_id}:{jti}"
                
                if not self.redis_client.exists(redis_key):
                    raise JWTError("Refresh token has been revoked")
            
            return payload
            
        except JWTError as e:
            raise JWTError(f"Token validation failed: {str(e)}")
    
    def revoke_token(self, user_id: str, jti: Optional[str] = None):
        """
        Revoke refresh token(s) for a user
        
        Args:
            user_id: User ID
            jti: Optional specific token ID to revoke. If None, revokes all user tokens
        """
        if jti:
            # Revoke specific token
            redis_key = f"refresh_token:{user_id}:{jti}"
            self.redis_client.delete(redis_key)
        else:
            # Revoke all tokens for user
            pattern = f"refresh_token:{user_id}:*"
            for key in self.redis_client.scan_iter(match=pattern):
                self.redis_client.delete(key)
    
    def hash_password(self, password: str) -> str:
        """
        Hash a password using bcrypt
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password
        """
        return self.pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash
        
        Args:
            plain_password: Plain text password
            hashed_password: Hashed password to compare against
            
        Returns:
            True if password matches, False otherwise
        """
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def hash_api_key(self, api_key: str) -> str:
        """
        Hash an API key for secure storage
        
        Args:
            api_key: Plain API key
            
        Returns:
            SHA-256 hash of the API key
        """
        return hashlib.sha256(api_key.encode()).hexdigest()
    
    def generate_api_key(self) -> str:
        """
        Generate a secure random API key
        
        Returns:
            Random API key string
        """
        return f"aio_{secrets.token_urlsafe(32)}"
    
    def verify_api_key(self, api_key: str, stored_hash: str) -> bool:
        """
        Verify an API key against its stored hash
        
        Args:
            api_key: Plain API key
            stored_hash: Stored hash to compare against
            
        Returns:
            True if API key matches, False otherwise
        """
        return self.hash_api_key(api_key) == stored_hash
