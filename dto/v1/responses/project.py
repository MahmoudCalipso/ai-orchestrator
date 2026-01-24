from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime

class ProjectResponseDTO(BaseModel):
    id: str
    project_name: str
    description: Optional[str] = None
    project_type: str
    status: str
    language: str
    framework: str
    repo_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    owner_id: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        from_attributes = True

class ProjectListResponseDTO(BaseModel):
    projects: List[ProjectResponseDTO]
    total: int
    page: int
    page_size: int
