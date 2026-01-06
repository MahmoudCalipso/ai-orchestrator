"""
Security Manager - Handles authentication and authorization
"""
import logging
import hashlib
import secrets
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
        
        # Generate default API key for development
        self.api_keys["dev-key-12345"] = {
            "user": "admin",
            "role": "admin",
            "created_at": datetime.now(),
            "rate_limit": 1000
        }
        
    def generate_api_key(self, user: str, role: str = "user") -> str:
        """Generate a new API key"""
        
        key = f"sk-{secrets.token_urlsafe(32)}"
        
        self.api_keys[key] = {
            "user": user,
            "role": role,
            "created_at": datetime.now(),
            "rate_limit": 100 if role == "user" else 1000
        }
        
        return key
        
    def verify_api_key(self, api_key: str) -> bool:
        """Verify an API key"""
        return api_key in self.api_keys
        
    def get_user_info(self, api_key: str) -> Optional[dict]:
        """Get user information from API key"""
        return self.api_keys.get(api_key)
        
    def check_rate_limit(self, api_key: str) -> bool:
        """Check if user is within rate limit"""
        
        if api_key not in self.api_keys:
            return False
            
        user_info = self.api_keys[api_key]
        rate_limit = user_info.get("rate_limit", 100)
        
        # Get current request count
        current_count = self.rate_limits.get(api_key, {}).get("count", 0)
        reset_time = self.rate_limits.get(api_key, {}).get("reset_time")
        
        # Reset if needed
        if not reset_time or datetime.now() > reset_time:
            self.rate_limits[api_key] = {
                "count": 0,
                "reset_time": datetime.now() + timedelta(minutes=1)
            }
            current_count = 0
            
        # Check limit
        if current_count >= rate_limit:
            return False
            
        # Increment count
        self.rate_limits[api_key]["count"] = current_count + 1
        return True
        
    def log_audit_event(
        self,
        user: str,
        action: str,
        resource: str,
        status: str,
        details: dict = None
    ):
        """Log an audit event"""
        
        event = {
            "timestamp": datetime.now().isoformat(),
            "user": user,
            "action": action,
            "resource": resource,
            "status": status,
            "details": details or {}
        }
        
        self.audit_log.append(event)
        
        # Keep only last 1000 events
        if len(self.audit_log) > 1000:
            self.audit_log = self.audit_log[-1000:]
            
    def get_audit_log(self, limit: int = 100) -> list:
        """Get recent audit log entries"""
        return self.audit_log[-limit:]
        
    def hash_sensitive_data(self, data: str) -> str:
        """Hash sensitive data"""
        return hashlib.sha256(data.encode()).hexdigest()


# Dependency for FastAPI
async def verify_api_key(x_api_key: Optional[str] = Header(None)) -> str:
    """Verify API key from header"""
    
    # For development, allow requests without API key
    if not x_api_key:
        x_api_key = "dev-key-12345"
        
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