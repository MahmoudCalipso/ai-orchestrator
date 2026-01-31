from typing import Optional, Dict, Any, List, Union
from pydantic import BaseModel, Field
from .enums import ProjectType, ArchitecturePattern, DatabaseType

class FrameworkSpec(BaseModel):
    """Framework specification with version and architecture"""
    framework: str
    version: str
    architecture: Optional[str] = None
    sdk: Optional[str] = None
    jdk: Optional[str] = None

class LanguageConfig(BaseModel):
    """Enhanced language configuration for different components"""
    backend: Optional[Union[str, FrameworkSpec]] = Field(None)
    frontend: Optional[Union[str, FrameworkSpec]] = Field(None)
    mobile: Optional[str] = Field(None)
    desktop: Optional[str] = Field(None)
    database_orm: Optional[str] = Field(None)

class TemplateSource(BaseModel):
    """Template source configuration"""
    url: Optional[str] = None
    git_repo: Optional[str] = None
    local_path: Optional[str] = None
    figma_file: Optional[str] = None

class DatabaseConfig(BaseModel):
    """Database configuration"""
    type: DatabaseType
    connection_string: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    username: Optional[str] = None
    password: Optional[str] = None
    database_name: Optional[str] = None
    generate_from_schema: bool = False

class GitCredential(BaseModel):
    """Git credential configuration"""
    username: Optional[str] = None
    token: Optional[str] = None
    ssh_key: Optional[str] = None

class GitActionConfig(BaseModel):
    """Git action configuration"""
    provider: str = "github"
    repository_name: Optional[str] = None
    repository_owner: Optional[str] = None
    repository_url: Optional[str] = None
    branch: str = "main"
    commit_message: str = "Initial commit by AI Orchestrator"
    create_repo: bool = True
    private: bool = True
    credentials: Optional[GitCredential] = None

class ValidationRule(BaseModel):
    """Validation rule for entity fields"""
    type: str
    value: Optional[Any] = None
    message: Optional[str] = None
    condition: Optional[str] = None

class EntityField(BaseModel):
    """Entity field definition"""
    name: str
    type: str
    length: Optional[int] = None
    projected_name: Optional[str] = None
    description: Optional[str] = None
    nullable: bool = False
    unique: bool = False
    primary_key: bool = False
    auto_increment: bool = False
    foreign_key: Optional[str] = None
    default_value: Optional[Any] = None
    validations: List[ValidationRule] = Field(default_factory=list)

class EntityDefinition(BaseModel):
    """Entity definition for project generation"""
    name: str
    table_name: Optional[str] = None
    description: Optional[str] = None
    fields: List[EntityField]
    relationships: List[Dict[str, Any]] = Field(default_factory=list)
    features: List[str] = Field(default_factory=list)

class SecurityConfig(BaseModel):
    """Security configuration"""
    auth_provider: str = "jwt"
    enable_rbac: bool = True
    enable_audit_logs: bool = True
    enable_rate_limiting: bool = True
    enable_cors: bool = True
    enable_ssl: bool = True
    scan_dependencies: bool = True

class KubernetesConfig(BaseModel):
    """Kubernetes configuration"""
    enabled: bool = False
    environment: str = "development"
    namespace: str = "default"
    replicas: int = 1
    generate_helm_chart: bool = False
    ingress_domain: Optional[str] = None
    monitoring_enabled: bool = False

class ArchitectureConfig(BaseModel):
    """Architecture configuration"""
    patterns: List[str] = Field(default_factory=list)
    microservices: bool = False
    api_first: bool = False
    event_driven: bool = False
    serverless: bool = False

class ScalabilityConfig(BaseModel):
    """Scalability configuration"""
    requirements: List[str] = Field(default_factory=list)
    enable_caching: bool = False
    enable_load_balancing: bool = False
    enable_cdn: bool = False
    enable_auto_scaling: bool = False
    enable_horizontal_scaling: bool = False

class IntegrationConfig(BaseModel):
    """Integration configuration"""
    required: List[str] = Field(default_factory=list)
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
    strategy: str = "docker-compose"
    generate_dockerfile: bool = True
    generate_docker_compose: bool = True
    generate_kubernetes: bool = False
    generate_ci_cd: bool = False

class StackComponents(BaseModel):
    """Additional stack components"""
    cache: Optional[str] = None
    message_queue: Optional[str] = None
    search_engine: Optional[str] = None

class LanguageFrameworkSpec(BaseModel):
    """Language and framework specification with version"""
    name: str
    framework: str
    version: str

class FrontendConfig(BaseModel):
    """Frontend configuration"""
    framework: str
    version: str
    ssr: bool = False
    typescript: bool = True
