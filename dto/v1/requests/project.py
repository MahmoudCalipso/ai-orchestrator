from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

class ProjectAnalyzeRequest(BaseModel):
    """Request to analyze a whole project"""
    project_path: str = Field(..., description="Local path to the project")

class ProjectAddFeatureRequest(BaseModel):
    """Request to add a feature to a project"""
    project_path: str = Field(..., description="Local path to the project")
    feature_description: str = Field(..., description="Description of the feature to add")

class ProjectSearchRequest(BaseModel):
    """schema for project search"""
    query: Optional[str] = None
    language: Optional[str] = None
    status: Optional[str] = None
    page: int = 1
    limit: int = 20

class ProjectCreateRequest(BaseModel):
    """Request to create a project"""
    project_name: str
    description: Optional[str] = None
    framework: Optional[str] = None

class ProjectUpdateRequest(BaseModel):
    """Request to update a project"""
    description: Optional[str] = None
    status: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
