from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

class ProjectAnalyzeRequest(BaseModel):
    """Request to initiate a deep structural and quality analysis of a project"""
    project_path: str = Field(..., description="Local absolute path to the project root", example="/storage/projects/my-awesome-app")

class ProjectAddFeatureRequest(BaseModel):
    """Request to add a new feature or component to an existing project via AI"""
    project_path: str = Field(..., description="Local absolute path to the project root", example="/storage/projects/my-awesome-app")
    feature_description: str = Field(..., description="Detailed description of the feature to be implemented", example="Add a JWT-based authentication system with Role-Based Access Control")

class ProjectSearchRequest(BaseModel):
    """Refined search and filtration parameters for project discovery"""
    query: Optional[str] = Field(None, description="General search query for name or description", example="orchestrator")
    language: Optional[str] = Field(None, description="Filter by primary programming language", example="python")
    status: Optional[str] = Field(None, description="Filter by project lifecycle status", example="active")
    page: int = Field(1, ge=1, description="Pagination page number")
    limit: int = Field(20, ge=1, le=100, description="Number of results per page")

class ProjectCreateRequest(BaseModel):
    """Request to initialize a new managed project"""
    project_name: str = Field(..., min_length=1, max_length=100, description="Unique display name for the project", example="AI Orchestrator v2")
    description: Optional[str] = Field(None, max_length=500, description="Brief overview of the project's purpose", example="Enterprise-grade AI agent management platform")
    framework: Optional[str] = Field(None, description="Primary technical framework", example="FastAPI")
    language: Optional[str] = Field(None, description="Primary programming language", example="python")
    git_repo_url: Optional[str] = Field(None, description="Optional remote Git repository URL to link")

class ProjectUpdateRequest(BaseModel):
    """Request to patch an existing project's metadata or configuration"""
    description: Optional[str] = Field(None, max_length=500, description="Updated project overview")
    status: Optional[str] = Field(None, description="Transition project lifecycle state", example="archived")
    config: Optional[Dict[str, Any]] = Field(None, description="Extended configuration parameters")
