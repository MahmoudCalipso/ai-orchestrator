"""Orchestration DTOs and Schemas."""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from ..validators import InputValidators

class ExecutionStatusEnum(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"
    RATE_LIMITED = "rate_limited"

class AgentSelectionMode(str, Enum):
    AUTO = "auto"
    MANUAL = "manual"
    SEMI_AUTO = "semi_auto"

class ExecutionModeEnum(str, Enum):
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    ADAPTIVE = "adaptive"

class FileContext(BaseModel):
    filename: str = Field(..., max_length=255)
    language: str
    content: str = Field(..., max_length=100000)
    encoding: str = "utf-8"

class MessageDTO(BaseModel):
    role: str
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = None

class OrchestrationContext(BaseModel):
    code: Optional[str] = Field(None, max_length=50000)
    files: Optional[List[FileContext]] = None
    conversation_history: Optional[List[MessageDTO]] = None
    external_context: Optional[Dict[str, Any]] = None

class OrchestrationRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=10000)
    context: Optional[OrchestrationContext] = None
    agent_selection: AgentSelectionMode = "auto"
    specific_agents: Optional[List[str]] = None
    execution_mode: ExecutionModeEnum = "sequential"
    stream: bool = True
    max_iterations: int = Field(default=10, ge=1, le=50)
    budget_limit: Optional[int] = None
    require_approval: bool = False
    metadata: Optional[Dict[str, Any]] = None

    @field_validator('prompt')
    @classmethod
    def validate_prompt(cls, v):
        return InputValidators.sanitize_code(v)

class TokenUsageDTO(BaseModel):
    input: int
    output: int
    total: int

class OrchestrationResultDTO(BaseModel):
    final_output: str
    agent_outputs: List[Dict[str, Any]]
    chain_of_thought: Optional[str] = None
    artifacts: List[Dict[str, Any]] = []
    metrics: Dict[str, Any]

class ExecutionDTO(BaseModel):
    id: str
    status: ExecutionStatusEnum
    prompt: str
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_ms: Optional[int] = None
    agents_involved: List[str] = []
    iteration_count: int = 0
    total_tokens: TokenUsageDTO
    estimated_cost_usd: float
    metadata: Optional[Dict] = None

class OrchestrationResponse(BaseModel):
    success: bool = True
    request_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    execution_id: str
    status: ExecutionStatusEnum
    message: str
    result_url: str
    websocket_url: Optional[str] = None
    estimated_duration_ms: int
