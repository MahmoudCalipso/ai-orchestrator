from typing import List, Optional
from pydantic import BaseModel, Field

class CreateOrgUserRequest(BaseModel):
    """Add a user to the organization"""
    email: str
    full_name: str
    password: str
    role: str = "developer"

class ProjectProtectionRequest(BaseModel):
    """Enable/Disable project protection"""
    enabled: bool
    allowed_users: Optional[List[str]] = None
