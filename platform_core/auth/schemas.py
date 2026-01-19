"""
Authentication API Schemas
Pydantic models for request/response validation
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, validator


# Request Schemas

class UserRegister(BaseModel):
    """User registration request"""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    full_name: Optional[str] = None
    tenant_name: str = Field(..., min_length=1, max_length=100)
    
    @validator('password')
    def password_strength(cls, v):
        """Validate password strength"""
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserLogin(BaseModel):
    """User login request"""
    email: EmailStr
    password: str


class TokenRefresh(BaseModel):
    """Token refresh request"""
    refresh_token: str


class APIKeyCreate(BaseModel):
    """API key creation request"""
    name: str = Field(..., min_length=1, max_length=100)
    expires_in_days: Optional[int] = Field(None, ge=1, le=365)


class PasswordChange(BaseModel):
    """Password change request"""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)
    
    @validator('new_password')
    def password_strength(cls, v):
        """Validate password strength"""
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class ForgotPasswordRequest(BaseModel):
    """Request to initiate password reset"""
    email: EmailStr


class PasswordReset(BaseModel):
    """Actual password reset with token"""
    token: str
    new_password: str = Field(..., min_length=8, max_length=100)
    
    @validator('new_password')
    def password_strength(cls, v):
        """Validate password strength"""
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


# Response Schemas

class TokenResponse(BaseModel):
    """Token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class UserResponse(BaseModel):
    """User response"""
    id: str
    email: str
    full_name: Optional[str]
    role: str
    tenant_id: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class TenantResponse(BaseModel):
    """Tenant response"""
    id: str
    name: str
    plan: str
    storage_quota_gb: int
    storage_used_gb: float
    storage_usage_percent: float
    workbench_quota: int
    api_rate_limit: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class APIKeyResponse(BaseModel):
    """API key response"""
    id: str
    name: str
    key: Optional[str] = None  # Only returned on creation
    created_at: datetime
    expires_at: Optional[datetime]
    last_used: Optional[datetime]
    usage_count: int
    is_active: bool
    
    class Config:
        from_attributes = True


class ExternalAccountResponse(BaseModel):
    """External account response"""
    id: str
    provider: str
    username: Optional[str]
    email: Optional[str]
    avatar_url: Optional[str]
    scopes: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class OAuthConnectRequest(BaseModel):
    """OAuth connection initiation"""
    redirect_uri: Optional[str] = None


class MeResponse(BaseModel):
    """Current user info response"""
    user: UserResponse
    tenant: TenantResponse
    permissions: list[str]
    external_accounts: list[ExternalAccountResponse]
