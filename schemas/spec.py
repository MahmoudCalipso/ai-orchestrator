"""
Data models and schemas for the AI Orchestrator
"""
from typing import Optional, Dict, Any, List
from enum import Enum
from pydantic import BaseModel, Field


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


class InferenceParameters(BaseModel):
    """Inference parameters"""
    temperature: Optional[float] = Field(default=0.7, ge=0.0, le=2.0)
    top_p: Optional[float] = Field(default=0.9, ge=0.0, le=1.0)
    top_k: Optional[int] = Field(default=40, ge=0)
    max_tokens: Optional[int] = Field(default=2048, ge=1)
    stop_sequences: Optional[List[str]] = None
    frequency_penalty: Optional[float] = Field(default=0.0, ge=-2.0, le=2.0)
    presence_penalty: Optional[float] = Field(default=0.0, ge=-2.0, le=2.0)
    repetition_penalty: Optional[float] = Field(default=1.0, ge=0.0, le=2.0)
    stream: Optional[bool] = False


class InferenceRequest(BaseModel):
    """Inference request schema"""
    prompt: str = Field(..., min_length=1)
    task_type: Optional[TaskType] = TaskType.CHAT
    model: Optional[str] = None
    parameters: Optional[InferenceParameters] = InferenceParameters()
    context: Optional[Dict[str, Any]] = None
    system_prompt: Optional[str] = None


class InferenceResponse(BaseModel):
    """Inference response schema"""
    request_id: str
    model: str
    runtime: str
    output: str
    tokens_used: int
    processing_time: float
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ModelInfo(BaseModel):
    """Model information schema"""
    name: str
    family: str
    size: str
    context_length: int
    capabilities: List[str]
    specialization: str
    memory_requirement: str
    recommended_runtime: List[str]
    status: ModelStatus
    quantization: Optional[List[str]] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    uptime: float
    models_loaded: int
    runtimes_available: List[str]


class SystemStatus(BaseModel):
    """Detailed system status"""
    status: str
    uptime: float
    models: Dict[str, ModelStatus]
    runtimes: Dict[str, Dict[str, Any]]
    resources: Dict[str, Any]
    metrics: Dict[str, Any]


class MigrationRequest(BaseModel):
    """Task migration request"""
    task_id: str
    target_model: Optional[str] = None
    target_runtime: Optional[RuntimeType] = None
    preserve_state: bool = True


class AuditLog(BaseModel):
    """Audit log entry"""
    timestamp: float
    user: str
    action: str
    resource: str
    details: Dict[str, Any]
    status: str