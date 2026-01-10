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
    backend: Optional[Union[str, FrameworkSpec]] = None  # Legacy string or new FrameworkSpec
    frontend: Optional[Union[str, FrameworkSpec]] = None
    mobile: Optional[str] = None   # e.g., "Flutter 3.16", "React Native"
    desktop: Optional[str] = None  # e.g., "Tauri", "Electron"
    database_orm: Optional[str] = None # e.g., "Diesel", "GORM", "SQLAlchemy"

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
    project_name: str
    description: Optional[str] = None
    project_types: List[ProjectType] = Field(default_factory=lambda: [ProjectType.WEB])
    languages: LanguageConfig
    template: Optional[TemplateSource] = None
    database: Optional[DatabaseConfig] = None
    entities: List[EntityDefinition] = Field(default_factory=list)
    git: Optional[GitActionConfig] = None
    security: Optional[SecurityConfig] = Field(default_factory=SecurityConfig)
    kubernetes: Optional[KubernetesConfig] = Field(default_factory=KubernetesConfig)
    requirements: Optional[str] = None # Natural language requirements

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
    source_stack: str # e.g. "Java 8 Spring Boot"
    target_stack: str # e.g. "Go 1.22 Gin"
    target_architecture: ArchitecturePattern = ArchitecturePattern.REPOSITORY_PATTERN
    git: Optional[GitActionConfig] = None
    entities_only: bool = False # If true, only migrates data structures
