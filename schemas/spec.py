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
    temperature: Optional[float] = Field(default=0.7, ge=0.0, le=2.0, description="Sampling temperature (0.0 - 2.0)")
    top_p: Optional[float] = Field(default=0.9, ge=0.0, le=1.0, description="Nucleus sampling probability")
    top_k: Optional[int] = Field(default=40, ge=0, description="Sample from the top K tokens")
    max_tokens: Optional[int] = Field(default=2048, ge=1, description="Maximum tokens to generate")
    stop_sequences: Optional[List[str]] = Field(None, description="Sequences where generation stops")
    frequency_penalty: Optional[float] = Field(default=0.0, ge=-2.0, le=2.0, description="Penalty for repeating tokens")
    presence_penalty: Optional[float] = Field(default=0.0, ge=-2.0, le=2.0, description="Penalty for new topics")
    repetition_penalty: Optional[float] = Field(default=1.0, ge=0.0, le=2.0, description="Explicit repetition penalty")
    stream: Optional[bool] = Field(default=False, description="Whether to stream the response")


class InferenceRequest(BaseModel):
    """Inference request schema"""
    prompt: str = Field(..., min_length=1, description="The input prompt for the AI", example="Write a Python function to sort a list.")
    task_type: Optional[TaskType] = Field(TaskType.CHAT, description="Type of AI task")
    model: Optional[str] = Field(None, description="Specific model to use (optional)")
    parameters: Optional[InferenceParameters] = Field(default_factory=InferenceParameters, description="Generation parameters")
    context: Optional[Dict[str, Any]] = Field(None, description="Optional conversational context")
    system_prompt: Optional[str] = Field(None, description="Optional system-level instructions")


class InferenceResponse(BaseModel):
    """Inference response schema"""
    request_id: str = Field(..., description="Unique ID for the request")
    model: str = Field(..., description="Model used for generation")
    runtime: str = Field(..., description="Runtime used for execution")
    output: str = Field(..., description="Generated text content")
    tokens_used: int = Field(..., description="Total tokens consumed")
    processing_time: float = Field(..., description="Time taken in seconds")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional execution metadata")


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