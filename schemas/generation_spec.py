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

class ArchitectureConfig(BaseModel):
    """Architecture configuration"""
    patterns: List[str] = Field(default_factory=list, description="Architecture patterns (microservices, api-first, event-driven)")
    microservices: bool = False
    api_first: bool = False
    event_driven: bool = False
    serverless: bool = False

class ScalabilityConfig(BaseModel):
    """Scalability configuration"""
    requirements: List[str] = Field(default_factory=list, description="Scalability requirements")
    enable_caching: bool = False
    enable_load_balancing: bool = False
    enable_cdn: bool = False
    enable_auto_scaling: bool = False
    enable_horizontal_scaling: bool = False

class IntegrationConfig(BaseModel):
    """Integration configuration"""
    required: List[str] = Field(default_factory=list, description="Required integrations")
    payment_gateway: bool = False
    email_service: bool = False
    sms_service: bool = False
    analytics: bool = False
    erp: bool = False
    crm: bool = False
    logistics: bool = False
    social_media: bool = False

class DeploymentConfig(BaseModel):
    """Deployment configuration"""
    strategy: str = "docker-compose"  # docker-compose, kubernetes, serverless, cloud-native
    generate_dockerfile: bool = True
    generate_docker_compose: bool = True
    generate_kubernetes: bool = False
    generate_ci_cd: bool = False

class StackComponents(BaseModel):
    """Additional stack components"""
    cache: Optional[str] = None  # redis, memcached
    message_queue: Optional[str] = None  # rabbitmq, kafka, redis
    search_engine: Optional[str] = None  # elasticsearch, algolia

class LanguageFrameworkSpec(BaseModel):
    """Language and framework specification with version"""
    name: str = Field(..., description="Language name (python, javascript, java, etc.)")
    framework: str = Field(..., description="Framework name (FastAPI, React, Spring Boot, etc.)")
    version: str = Field(..., description="Framework version (0.128.0, 19.0.0, etc.)")

class FrontendConfig(BaseModel):
    """Frontend configuration"""
    framework: str = Field(..., description="Frontend framework (React, Next.js, Vue.js, Angular)")
    version: str = Field(..., description="Framework version")
    ssr: bool = False  # Server-side rendering
    typescript: bool = True

class GenerationRequest(BaseModel):
    """Enhanced application generation request with full auto-configuration support"""
    
    # Basic project info
    project_name: str = Field(..., description="Name of the project to generate", json_schema_extra={"example": "MyAwesomeApp"})
    description: Optional[str] = Field(None, description="Detailed description of the application (used for auto-analysis)")
    project_type: Optional[str] = Field(None, description="Project type (e-commerce, saas, cms, api, mobile, etc.)")
    
    # Languages and frameworks (auto-configured from description if not provided)
    languages: Optional[Union[List[str], List[LanguageFrameworkSpec], LanguageConfig]] = Field(
        None, 
        description="Languages/frameworks to use. Can be simple list ['python', 'react'] or detailed specs with versions"
    )
    frontend: Optional[FrontendConfig] = Field(None, description="Frontend configuration with framework and version")
    
    # Template and design
    template: Optional[TemplateSource] = Field(None, description="Optional template source (Git, local, Figma)")
    
    # Database (auto-configured if not provided)
    database: Optional[DatabaseConfig] = Field(None, description="Database configuration and connection details")
    
    # Entities and data model
    entities: List[EntityDefinition] = Field(default_factory=list, description="List of entity definitions for the project")
    
    # Security (auto-configured from description)
    security: Optional[SecurityConfig] = Field(None, description="Security and auth configuration")
    
    # Architecture (auto-detected from description)
    architecture: Optional[ArchitectureConfig] = Field(None, description="Architecture patterns and configuration")
    
    # Scalability (auto-detected from description)
    scalability: Optional[ScalabilityConfig] = Field(None, description="Scalability requirements and configuration")
    
    # Integrations (auto-detected from description)
    integrations: Optional[IntegrationConfig] = Field(None, description="External service integrations")
    
    # Deployment (auto-configured)
    deployment: Optional[DeploymentConfig] = Field(None, description="Deployment strategy and configuration")
    
    # Stack components (auto-configured)
    stack_components: Optional[StackComponents] = Field(None, description="Additional stack components (cache, queue, search)")
    
    # Features (auto-detected from description)
    features: List[str] = Field(default_factory=list, description="Core features (authentication, payment, analytics, etc.)")
    
    # Technical requirements (auto-detected)
    technical_requirements: List[str] = Field(
        default_factory=list, 
        description="Technical requirements (high-traffic-support, real-time-capabilities, etc.)"
    )
    
    # Complexity estimation (auto-calculated)
    estimated_complexity: Optional[str] = Field(None, description="Estimated complexity (low, medium, high, enterprise)")
    
    # Git integration
    git: Optional[GitActionConfig] = Field(None, description="Git repository creation and commit settings")
    
    # Kubernetes (legacy, use deployment instead)
    kubernetes: Optional[KubernetesConfig] = Field(None, description="K8s deployment settings (deprecated, use deployment)")
    
    # Natural language requirements
    requirements: Optional[str] = Field(None, description="Natural language requirements for the generation")
    
    # Analysis metadata (populated by analyzer)
    analysis: Optional[Dict[str, Any]] = Field(None, description="Analysis metadata from description analyzer")

class DescriptionAnalysisRequest(BaseModel):
    """Request for description analysis and config preview"""
    description: str = Field(..., description="Project description to analyze")
    project_name: Optional[str] = Field("Generated Project", description="Optional project name")
    
class DescriptionAnalysisResponse(BaseModel):
    """Response with full auto-generated configuration"""
    analysis: Dict[str, Any] = Field(..., description="Detailed analysis of the description")
    generated_config: Dict[str, Any] = Field(..., description="Complete auto-generated configuration ready for /api/generate")
    summary: str = Field(..., description="Human-readable summary of the analysis")


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
    source_stack: str = Field(..., description="Source technology stack", json_schema_extra={"example": "Java 8 Spring Boot"})
    target_stack: str = Field(..., description="Target technology stack", json_schema_extra={"example": "Go 1.22 Gin"})
    target_architecture: ArchitecturePattern = Field(
        ArchitecturePattern.REPOSITORY_PATTERN,
        description="Target architecture pattern"
    )
    git: Optional[GitActionConfig] = Field(None, description="Git settings for the new project")
    entities_only: bool = Field(False, description="Whether to migrate only the data structures")
