from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime

class ProjectResponseDTO(BaseModel):
    """Detailed representation of a managed project"""
    id: str = Field(..., description="Unique UUID of the project", example="550e8400-e29b-41d4-a716-446655440000")
    project_name: str = Field(..., description="Project display name", example="AI Orchestrator v2")
    description: Optional[str] = Field(None, description="Project overview")
    status: str = Field(..., description="Current lifecycle status", example="active")
    language: str = Field(..., description="Primary programming language", example="python")
    framework: str = Field(..., description="Primary technical framework", example="FastAPI")
    git_repo_url: Optional[str] = Field(None, description="Linked Git repository URL")
    git_branch: str = Field("main", description="Target Git branch")
    local_path: str = Field(..., description="Absolute local path on the server")
    created_at: datetime = Field(..., description="Project creation timestamp")
    updated_at: datetime = Field(..., description="Last project update timestamp")
    last_opened_at: Optional[datetime] = Field(None, description="Most recent IDE session timestamp")
    build_status: Optional[str] = Field(None, description="Most recent build result")
    run_status: Optional[str] = Field(None, description="Current runtime state")
    extra_metadata: Dict[str, Any] = Field(default_factory=dict, description="Extension metadata")

    class Config:
        from_attributes = True

class ProjectListResponseDTO(BaseModel):
    """Paginated collection of projects"""
    projects: List[ProjectResponseDTO] = Field(..., description="List of projects for the current page")
    total: int = Field(..., description="Total number of projects matching filters")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of results per page")
