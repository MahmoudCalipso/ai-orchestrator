from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class WorkspaceResponseDTO(BaseModel):
    id: str = Field(..., description="Unique workspace identifier")
    name: str = Field(..., description="Organization or team name")
    owner_id: str = Field(..., description="User ID of the workspace owner")
    settings: Dict[str, Any] = Field(default_factory=dict, description="Workspace-specific configurations")
    created_at: datetime = Field(..., description="ISO timestamp of creation")
    updated_at: datetime = Field(..., description="ISO timestamp of last update")

    class Config:
        from_attributes = True

class WorkspaceListResponseDTO(BaseModel):
    workspaces: List[WorkspaceResponseDTO] = Field(..., description="List of workspaces matching criteria")
    total: int = Field(..., description="Total count of workspaces for the user")
