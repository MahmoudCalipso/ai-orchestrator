from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

class TokenResponseDTO(BaseModel):
    """Payload containing authentication and refresh tokens"""
    access_token: str = Field(..., description="JWT access token for API authorization")
    refresh_token: str = Field(..., description="Refresh token used to obtain new access tokens")
    token_type: str = Field("bearer", description="Type of token (always 'bearer')")
    expires_in: int = Field(..., description="Access token expiration in seconds", example=1800)

class UserResponseDTO(BaseModel):
    """Safe representation of a user account"""
    id: str = Field(..., description="Unique platform user UUID", example="550e8400-e29b-41d4-a716-446655440000")
    email: str = Field(..., description="Registered email address", example="developer@company.com")
    full_name: Optional[str] = Field(None, description="Legal full name", example="Ammar Mahmoud")
    role: str = Field(..., description="Account role", example="developer")
    tenant_id: str = Field(..., description="Associated tenant UUID", example="770e8400-e29b-41d4-a716-446655447777")
    is_active: bool = Field(True, description="Account status")
    is_verified: bool = Field(False, description="Email verification status")
    created_at: datetime = Field(..., description="Account creation timestamp")
    
    class Config:
        from_attributes = True

class TenantResponseDTO(BaseModel):
    """Representation of an organization/workspace tenant"""
    id: str = Field(..., description="Unique tenant UUID")
    name: str = Field(..., description="Tenant display name", example="Mahmoud Enterprises")
    plan: str = Field(..., description="Subscription plan", example="developer")
    storage_quota_gb: int = Field(..., description="Total storage allowance in GB")
    storage_used_gb: float = Field(..., description="Current storage usage in GB")
    storage_usage_percent: float = Field(..., description="Storage usage percentage")
    workbench_quota: int = Field(..., description="Max number of concurrent workbenches")
    api_rate_limit: int = Field(..., description="Requests per minute allowance")
    is_active: bool = Field(True, description="Tenant status")
    created_at: datetime = Field(..., description="Tenant creation timestamp")
    
    class Config:
        from_attributes = True

class APIKeyResponseDTO(BaseModel):
    """Payload containing API key details (key is only shown once upon creation)"""
    id: str = Field(..., description="Unique ID of the API key")
    name: str = Field(..., description="Friendly name given to the key")
    key: Optional[str] = Field(None, description="The actual API key (Only provided once during creation)")
    created_at: datetime = Field(..., description="Key creation timestamp")
    expires_at: Optional[datetime] = Field(None, description="Optional expiration date")
    last_used: Optional[datetime] = Field(None, description="Timestamp of most recent use")
    usage_count: int = Field(0, description="Total number of successful requests made with this key")
    is_active: bool = Field(True, description="Whether the key is currently active")
    
    class Config:
        from_attributes = True

class ExternalAccountResponseDTO(BaseModel):
    """Representation of an linked external account (Git provider, etc.)"""
    id: str = Field(..., description="Unique connection ID")
    provider: str = Field(..., description="Provider name (e.g., github, gitlab)")
    username: Optional[str] = Field(None, description="Provider-specific username")
    email: Optional[str] = Field(None, description="Linked account email")
    avatar_url: Optional[str] = Field(None, description="User avatar URL from provider")
    scopes: Optional[str] = Field(None, description="JSON string of granted permissions")
    created_at: datetime = Field(..., description="Connection timestamp")
    
    class Config:
        from_attributes = True

class MeResponseDTO(BaseModel):
    """Comprehensive user context returned for the '/me' endpoint"""
    user: UserResponseDTO = Field(..., description="Core user account details")
    tenant: TenantResponseDTO = Field(..., description="Associated tenant workspace details")
    permissions: List[str] = Field(..., description="Flattened list of all effective permissions", example=["projects.create", "api_keys.manage"])
    external_accounts: List[ExternalAccountResponseDTO] = Field(..., description="List of all linked external provider accounts")
