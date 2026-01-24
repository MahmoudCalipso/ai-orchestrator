from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

class TokenResponseDTO(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class UserResponseDTO(BaseModel):
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

class TenantResponseDTO(BaseModel):
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

class APIKeyResponseDTO(BaseModel):
    id: str
    name: str
    key: Optional[str] = None
    created_at: datetime
    expires_at: Optional[datetime]
    last_used: Optional[datetime]
    usage_count: int
    is_active: bool
    
    class Config:
        from_attributes = True

class ExternalAccountResponseDTO(BaseModel):
    id: str
    provider: str
    username: Optional[str]
    email: Optional[str]
    avatar_url: Optional[str]
    scopes: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class MeResponseDTO(BaseModel):
    user: UserResponseDTO
    tenant: TenantResponseDTO
    permissions: List[str]
    external_accounts: List[ExternalAccountResponseDTO]
