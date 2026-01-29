from typing import Optional
from pydantic import BaseModel, EmailStr, Field, validator

class UserRegisterRequest(BaseModel):
    """User registration request for new tenants"""
    email: EmailStr = Field(..., description="Valid work email address", example="developer@company.com")
    password: str = Field(
        ..., 
        min_length=8, 
        max_length=100, 
        description="Strong password (min 8 chars, must contain upper, lower, and digit)",
        example="StrongP@ss123"
    )
    full_name: Optional[str] = Field(None, description="Legal full name", example="Ammar Mahmoud")
    tenant_name: str = Field(
        ..., 
        min_length=1, 
        max_length=100, 
        description="Name of the organization or personal workspace",
        example="Mahmoud Enterprises"
    )
    
    @validator('password')
    def password_strength(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v

class UserLoginRequest(BaseModel):
    """User login request with credentials"""
    email: EmailStr = Field(..., description="Registered user email", example="developer@company.com")
    password: str = Field(..., description="User password", example="StrongP@ss123")

class TokenRefreshRequest(BaseModel):
    """Request to exchange a refresh token for a new access token"""
    refresh_token: str = Field(..., description="Valid refresh token obtained during login")

class APIKeyCreateRequest(BaseModel):
    """Request to generate a new programmatic access key"""
    name: str = Field(..., min_length=1, max_length=100, description="Friendly name for the key", example="CI/CD Pipeline Key")
    expires_in_days: Optional[int] = Field(None, ge=1, le=365, description="Optional key expiration in days", example=30)

class PasswordChangeRequest(BaseModel):
    """Request to update user password while logged in"""
    current_password: str = Field(..., description="Current valid password", example="OldP@ss123")
    new_password: str = Field(
        ..., 
        min_length=8, 
        max_length=100, 
        description="New strong password",
        example="NewStr0ngP@ss!"
    )
    
    @validator('new_password')
    def password_strength(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v

class ForgotPasswordRequest(BaseModel):
    """Request to initiate the password recovery process via email"""
    email: EmailStr = Field(..., description="Email address associated with the account", example="developer@company.com")

class PasswordResetRequest(BaseModel):
    """Request to set a new password using a reset token"""
    token: str = Field(..., description="Secure reset token received via email")
    new_password: str = Field(
        ..., 
        min_length=8, 
        max_length=100, 
        description="New strong password",
        example="ResetStr0ngP@ss!"
    )
    
    @validator('new_password')
    def password_strength(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v

class OAuthConnectRequest(BaseModel):
    """Request context for initiating an external provider connection"""
    redirect_uri: Optional[str] = Field(None, description="Optional custom redirect URI after authentication", example="https://app.orchestrator.com/callback")
