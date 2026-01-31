from enum import Enum

class TaskType(str, Enum):
    """Task type enumeration"""
    CODE_GENERATION = "code_generation"
    CODE_REVIEW = "code_review"
    REASONING = "reasoning"
    QUICK_QUERY = "quick_query"
    CREATIVE_WRITING = "creative_writing"
    DATA_ANALYSIS = "data_analysis"
    DOCUMENTATION = "documentation"
    CHAT = "chat"
    EMBEDDING = "embedding"

class RuntimeType(str, Enum):
    """Runtime type enumeration"""
    OLLAMA = "ollama"
    VLLM = "vllm"
    TRANSFORMERS = "transformers"
    LLAMACPP = "llamacpp"

class ModelStatus(str, Enum):
    """Model status enumeration"""
    AVAILABLE = "available"
    LOADING = "loading"
    LOADED = "loaded"
    UNLOADING = "unloading"
    ERROR = "error"
    UNAVAILABLE = "unavailable"

class ProjectStatus(str, Enum):
    """Project lifecycle status"""
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"
    BUILDING = "building"
    RUNNING = "running"

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

class BuildStatus(str, Enum):
    """Project build status"""
    PENDING = "pending"
    BUILDING = "building"
    SUCCESS = "success"
    FAILED = "failed"

class RunStatus(str, Enum):
    """Project runtime status"""
    STOPPED = "stopped"
    RUNNING = "running"
    CRASHED = "crashed"
    STARTING = "starting"

class WorkflowStatus(str, Enum):
    """Workflow execution status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
