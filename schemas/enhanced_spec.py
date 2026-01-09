"""
Enhanced schemas matching exact user API specification
"""
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from .generation_spec import (
    LanguageConfig, DatabaseConfig, GitActionConfig, 
    EntityDefinition, SecurityConfig, KubernetesConfig,
    ArchitecturePattern
)

class TemplateOfApp(BaseModel):
    """Template configuration for web or mobile app"""
    linkPath: Optional[str] = Field(None, description="ThemeForest or marketplace link")
    figmaFile: Optional[str] = Field(None, description="Figma file ID or URL")

class EnhancedGenerationRequest(BaseModel):
    """
    Enhanced generation request matching user's exact API specification
    POST /api/generate
    """
    languages: LanguageConfig = Field(..., description="Backend, frontend, mobile, desktop languages")
    templateOfAppWeb: Optional[TemplateOfApp] = Field(None, description="Web app template configuration")
    templateOfAppMobile: Optional[TemplateOfApp] = Field(None, description="Mobile app template configuration")
    typeOfProject: List[str] = Field(default_factory=list, description="Project types: web, mobile, desktop, api")
    database: Optional[str] = Field(None, description="Database type: SQL, NoSQL, etc.")
    gitAction: Optional[GitActionConfig] = Field(None, description="Git repository configuration")
    requirements: Optional[str] = Field(None, description="Natural language requirements")
    
    # Additional fields for advanced features
    entities: List[EntityDefinition] = Field(default_factory=list, description="Entity definitions")
    security: Optional[SecurityConfig] = Field(None, description="Security configuration")
    kubernetes: Optional[KubernetesConfig] = Field(None, description="Kubernetes configuration")
    ar_enabled: bool = Field(False, description="Enable AR features")
    ar_config: Optional[Dict[str, Any]] = Field(None, description="AR configuration")

class EnhancedMigrationRequest(BaseModel):
    """
    Enhanced migration request matching user's exact API specification
    POST /api/migrate
    """
    sourceCode: str = Field(..., description="Source code or Git repository link")
    sourceStack: str = Field(..., description="Source technology stack (e.g., 'Java 8 Spring Boot')")
    targetStack: str = Field(..., description="Target technology stack (e.g., 'Go 1.22 Gin')")
    appArchitectureForTargetStack: str = Field(..., description="Target architecture pattern")
    
    # Additional fields
    gitAction: Optional[GitActionConfig] = Field(None, description="Git repository configuration for migrated code")
    entities: List[EntityDefinition] = Field(default_factory=list, description="Entity definitions to preserve")

class GenerationResponse(BaseModel):
    """Response for /api/generate endpoint"""
    status: str
    type: str
    generated_files: Dict[str, str] = Field(default_factory=dict)
    documentation: str = ""
    dockerfile: str = ""
    kubernetes_manifests: Dict[str, str] = Field(default_factory=dict)
    git_repository: Optional[Dict[str, Any]] = None
    template_processed: bool = False
    output_directory: Optional[str] = None

class MigrationResponse(BaseModel):
    """Response for /api/migrate endpoint"""
    status: str
    type: str
    migrated_files: Dict[str, str] = Field(default_factory=dict)
    documentation: str = ""
    new_repository: Optional[Dict[str, Any]] = None
    source_analysis: Optional[Dict[str, Any]] = None
