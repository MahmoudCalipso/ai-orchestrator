"""JWT Authentication Middleware."""
import logging
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import Request, HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import os
from core.utils.logging import user_id_var

logger = logging.getLogger(__name__)

# Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "super-secret-key-2026")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

class TokenPayload(BaseModel):
    sub: str  # user_id
    exp: int
    type: str  # 'access' or 'refresh'
    scopes: list = []

class JWTBearer(HTTPBearer):
    """Dependency for validating JWT tokens in routes."""
    
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)
    
    async def __call__(self, request: Request) -> Optional[Dict[str, Any]]:
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        if credentials:
            payload = self.verify_jwt(credentials.credentials)
            if not payload:
                raise HTTPException(status_code=403, detail="Invalid or expired token")
            if payload.get("type") != "access":
                raise HTTPException(status_code=403, detail="Invalid token type")
            
            # Inject payload into request state
            request.state.user = payload
            user_id_var.set(payload.get("sub"))
            return payload
        else:
            raise HTTPException(status_code=403, detail="Authorization required")
    
    @staticmethod
    def verify_jwt(token: str) -> Optional[Dict[str, Any]]:
        try:
            payload = jwt.decode(
                token, 
                JWT_SECRET_KEY, 
                algorithms=[JWT_ALGORITHM]
            )
            # Check expiration
            if payload.get("exp") < datetime.utcnow().timestamp():
                return None
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.error(f"Invalid token: {e}")
            return None

class TokenService:
    """Service for creating and refreshing tokens."""
    
    @staticmethod
    def create_access_token(user_id: str, expires_delta: Optional[timedelta] = None) -> str:
        expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        to_encode = {
            "sub": user_id,
            "exp": expire.timestamp(),
            "type": "access",
            "iat": datetime.utcnow().timestamp()
        }
        return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    
    @staticmethod
    def create_refresh_token(user_id: str) -> str:
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode = {
            "sub": user_id,
            "exp": expire.timestamp(),
            "type": "refresh",
            "iat": datetime.utcnow().timestamp()
        }
        return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

# Dependency shorthand
require_auth = JWTBearer()
