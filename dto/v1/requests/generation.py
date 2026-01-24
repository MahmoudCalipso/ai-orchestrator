from typing import Optional, Dict, Any, List, Union
from pydantic import BaseModel, Field
from schemas.generation_spec import (
    LanguageConfig, EntityDefinition, GitActionConfig, 
    DatabaseType, ProjectType, ArchitecturePattern,
    TemplateSource, DatabaseConfig, SecurityConfig,
    ArchitectureConfig, ScalabilityConfig, IntegrationConfig,
    DeploymentConfig, StackComponents, FrontendConfig,
    LanguageFrameworkSpec
)

class WorkbenchCreateRequest(BaseModel):
    """Request to create a workbench"""
    stack: str = Field(..., description="Flash stack name (e.g. react, nodejs, python)")
    project_name: str = Field(..., description="Name of the project")

class MigrationStartRequest(BaseModel):
    """Request to start a workbench-based migration"""
    source_stack: str
    target_stack: str
    project_path: Optional[str] = None

class FigmaAnalyzeRequest(BaseModel):
    """Request to analyze a Figma design"""
    file_key: str = Field(..., description="Figma file key")
    token: str = Field(..., description="Figma API token")

class SecurityScanRequest(BaseModel):
    """Request for a security scan"""
    project_path: str
    language: str = "python"
    type: str = "all"  # code, dependencies, all

class GenerationRequest(BaseModel):
    """Enhanced application generation request"""
    project_name: str = Field(..., description="Name of the project to generate")
    description: Optional[str] = None
    project_type: Optional[str] = None
    languages: Optional[Union[List[str], List[LanguageFrameworkSpec], LanguageConfig]] = None
    frontend: Optional[FrontendConfig] = None
    template: Optional[TemplateSource] = None
    database: Optional[DatabaseConfig] = None
    entities: List[EntityDefinition] = Field(default_factory=list)
    security: Optional[SecurityConfig] = None
    architecture: Optional[ArchitectureConfig] = None
    scalability: Optional[ScalabilityConfig] = None
    integrations: Optional[IntegrationConfig] = None
    deployment: Optional[DeploymentConfig] = None
    stack_components: Optional[StackComponents] = None
    features: List[str] = Field(default_factory=list)
    technical_requirements: List[str] = Field(default_factory=list)
    git: Optional[GitActionConfig] = None
    requirements: Optional[str] = None

class DescriptionAnalysisRequest(BaseModel):
    """Request for description analysis"""
    description: str
    project_name: Optional[str] = "Generated Project"

class FeatureAddRequest(BaseModel):
    """Request to add a feature to an existing project"""
    project_path: Optional[str] = None
    git_repo: Optional[str] = None
    feature_description: str
    entities: List[EntityDefinition] = Field(default_factory=list)
    languages: Optional[LanguageConfig] = None

class MigrationRequest(BaseModel):
    """Enhanced application migration request"""
    source_path: Optional[str] = None
    source_repo: Optional[str] = None
    source_stack: str
    target_stack: str
    target_architecture: ArchitecturePattern = ArchitecturePattern.REPOSITORY_PATTERN
    git: Optional[GitActionConfig] = None
    entities_only: bool = False
