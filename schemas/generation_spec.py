"""
Data models for enhanced application generation and migration
"""
from typing import Optional, Dict, Any, List, Union
from enum import Enum
from pydantic import BaseModel, Field

class ProjectType(str, Enum):
    """Project type enumeration"""
    WEB = "web"
    MOBILE = "mobile"
    DESKTOP = "desktop"
    API = "api"
    FULLSTACK = "fullstack"

class ArchitecturePattern(str, Enum):
    """Architecture pattern enumeration"""
    MVC = "mvc"
    MVVM = "mvvm"
    CLEAN_ARCHITECTURE = "clean_architecture"
    HEXAGONAL = "hexagonal"
    MICROSERVICES = "microservices"
    REPOSITORY_PATTERN = "repository_pattern"
    CQRS = "cqrs"

class DatabaseType(str, Enum):
    """Database type enumeration"""
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    SQLSERVER = "sqlserver"
    SQLITE = "sqlite"
    MONGODB = "mongodb"
    REDIS = "redis"
    DYNAMODB = "dynamodb"
    COSMOSDB = "cosmosdb"
    CASSANDRA = "cassandra"
    NONE = "none"

class FrameworkSpec(BaseModel):
    """Framework specification with version and architecture"""
    framework: str  # e.g., "Django", "FastAPI", "Spring Boot"
    version: str  # e.g., "5.0.1", "0.109.0"
    architecture: Optional[str] = None  # e.g., "MVP", "Clean Architecture"
    sdk: Optional[str] = None  # For .NET (e.g., "8.0.101")
    jdk: Optional[str] = None  # For Java (e.g., "17")


class LanguageConfig(BaseModel):
    """Enhanced language configuration for different components"""
    backend: Optional[Union[str, FrameworkSpec]] = Field(None, description="Backend stack (e.g. 'FastAPI', 'Spring Boot')")
    frontend: Optional[Union[str, FrameworkSpec]] = Field(None, description="Frontend stack (e.g. 'React', 'Vue')")
    mobile: Optional[str] = Field(None, description="Mobile framework (e.g. 'Flutter', 'React Native')")
    desktop: Optional[str] = Field(None, description="Desktop framework (e.g. 'Electron')")
    database_orm: Optional[str] = Field(None, description="ORM to use (e.g. 'SQLAlchemy', 'GORM')")

class TemplateSource(BaseModel):
    """Template source configuration"""
    url: Optional[str] = None       # Direct download URL or marketplace link
    git_repo: Optional[str] = None  # Git repository URL (preferred for purchased templates)
    local_path: Optional[str] = None # Path to local template
    figma_file: Optional[str] = None # Figma file ID or URL

class DatabaseConfig(BaseModel):
    """Database configuration"""
    type: DatabaseType
    connection_string: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    username: Optional[str] = None
    password: Optional[str] = None
    database_name: Optional[str] = None
    generate_from_schema: bool = False # If true, reverse engineer existing DB

class GitCredential(BaseModel):
    """Git credential configuration"""
    username: Optional[str] = None
    token: Optional[str] = None
    ssh_key: Optional[str] = None

class GitActionConfig(BaseModel):
    """Git action configuration"""
    provider: str = "github" # github, gitlab, bitbucket, azure
    repository_name: Optional[str] = None
    repository_owner: Optional[str] = None # Organization or user
    repository_url: Optional[str] = None # If using existing repo
    branch: str = "main"
    commit_message: str = "Initial commit by AI Orchestrator"
    create_repo: bool = True
    private: bool = True
    credentials: Optional[GitCredential] = None

class ValidationRule(BaseModel):
    """Validation rule for entity fields"""
    type: str # required, min, max, email, regex, unique, etc.
    value: Optional[Any] = None
    message: Optional[str] = None
    condition: Optional[str] = None # Conditional validation logic

class EntityField(BaseModel):
    """Entity field definition"""
    name: str
    type: str # string, integer, boolean, float, decimal, datetime, date, text, json, relation
    length: Optional[int] = None
    projected_name: Optional[str] = None # For DTO/API mapping
    description: Optional[str] = None
    nullable: bool = False
    unique: bool = False
    primary_key: bool = False
    auto_increment: bool = False
    foreign_key: Optional[str] = None # "Table.Column"
    default_value: Optional[Any] = None
    validations: List[ValidationRule] = Field(default_factory=list)

class EntityDefinition(BaseModel):
    """Entity definition for project generation"""
    name: str
    table_name: Optional[str] = None
    description: Optional[str] = None
    fields: List[EntityField]
    relationships: List[Dict[str, Any]] = Field(default_factory=list) # OneToMany, ManyToMany definitions
    features: List[str] = Field(default_factory=list) # audit, soft-delete, localization
    
class SecurityConfig(BaseModel):
    """Security configuration"""
    auth_provider: str = "jwt" # jwt, oauth2, auth0, firebase
    enable_rbac: bool = True
    enable_audit_logs: bool = True
    enable_rate_limiting: bool = True
    enable_cors: bool = True
    enable_ssl: bool = True
    scan_dependencies: bool = True

class KubernetesConfig(BaseModel):
    """Kubernetes configuration"""
    enabled: bool = False
    environment: str = "development" # development, staging, production
    namespace: str = "default"
    replicas: int = 1
    generate_helm_chart: bool = False
    ingress_domain: Optional[str] = None
    monitoring_enabled: bool = False

class GenerationRequest(BaseModel):
    """Enhanced application generation request"""
    project_name: str = Field(..., description="Name of the project to generate", example="MyAwesomeApp")
    description: Optional[str] = Field(None, description="Detailed description of the application")
    project_types: List[ProjectType] = Field(
        default_factory=lambda: [ProjectType.WEB],
        description="Types of projects to generate (Web, Mobile, etc.)"
    )
    languages: LanguageConfig = Field(..., description="Configuration for backend/frontend stacks")
    template: Optional[TemplateSource] = Field(None, description="Optional template source (Git, local, Figma)")
    database: Optional[DatabaseConfig] = Field(None, description="Database configuration and connection details")
    entities: List[EntityDefinition] = Field(default_factory=list, description="List of entity definitions for the project")
    git: Optional[GitActionConfig] = Field(None, description="Git repository creation and commit settings")
    security: Optional[SecurityConfig] = Field(default_factory=SecurityConfig, description="Security and auth configuration")
    kubernetes: Optional[KubernetesConfig] = Field(default_factory=KubernetesConfig, description="K8s deployment settings")
    requirements: Optional[str] = Field(None, description="Natural language requirements for the generation")

class FeatureAddRequest(BaseModel):
    """Request to add a feature to an existing project"""
    project_path: Optional[str] = None
    git_repo: Optional[str] = None
    feature_description: str
    entities: List[EntityDefinition] = Field(default_factory=list)
    languages: Optional[LanguageConfig] = None

class MigrationRequest(BaseModel):
    """Enhanced application migration request"""
    source_path: Optional[str] = Field(None, description="Local path to the source project")
    source_repo: Optional[str] = Field(None, description="Git repository URL of the source project")
    source_stack: str = Field(..., description="Source technology stack", example="Java 8 Spring Boot")
    target_stack: str = Field(..., description="Target technology stack", example="Go 1.22 Gin")
    target_architecture: ArchitecturePattern = Field(
        ArchitecturePattern.REPOSITORY_PATTERN,
        description="Target architecture pattern"
    )
    git: Optional[GitActionConfig] = Field(None, description="Git settings for the new project")
    entities_only: bool = Field(False, description="Whether to migrate only the data structures")
