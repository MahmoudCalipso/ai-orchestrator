"""Agent DTOs and Schemas."""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from ..validators import InputValidators

# ENUMS (duplicated from Part 4 for self-containment)
class AgentStatusEnum(str, Enum):
    IDLE = "idle"
    INITIALIZING = "initializing"
    ACTIVE = "active"
    PAUSED = "paused"
    ERROR = "error"
    TERMINATED = "terminated"
    ARCHIVED = "archived"

class AgentTypeEnum(str, Enum):
    ORCHESTRATOR = "orchestrator"
    CODE_GENERATOR = "code_generator"
    CODE_REVIEWER = "code_reviewer"
    DEBUGGER = "debugger"
    DOCUMENTATION = "documentation"
    ANALYZER = "analyzer"
    SECURITY = "security"
    OPTIMIZER = "optimizer"
    CUSTOM = "custom"

# BASE MODELS
class BaseResponse(BaseModel):
    success: bool = True
    request_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class PaginationResponse(BaseModel):
    page: int
    limit: int
    total: int
    total_pages: int
    has_next: bool
    has_prev: bool

# AGENT DTOs
class AgentDTO(BaseModel):
    id: str
    name: str
    display_name: str
    description: Optional[str]
    agent_type: AgentTypeEnum
    status: AgentStatusEnum
    model: str
    temperature: float
    max_tokens: int
    tools: List[str] = []
    created_at: datetime
    updated_at: datetime
    user_id: str
    session_count: int = 0
    total_tokens_used: int = 0
    last_active_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True

class CreateAgentRequest(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    display_name: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    agent_type: AgentTypeEnum
    model: str = Field(default="gpt-4o")
    system_prompt: Optional[str] = Field(None, max_length=10000)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=2000, ge=100, le=8000)
    tools: List[str] = []
    metadata: Optional[Dict[str, Any]] = None

    # Apply advanced validators
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        return InputValidators.validate_project_name(v)
    
    @field_validator('system_prompt')
    @classmethod
    def validate_prompt(cls, v):
        if v:
            return InputValidators.sanitize_code(v)
        return v

class CreateAgentResponse(BaseResponse):
    agent: AgentDTO
    initialization_status: str
    websocket_url: Optional[str] = None

class UpdateAgentRequest(BaseModel):
    display_name: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    system_prompt: Optional[str] = Field(None, max_length=10000)
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(None, ge=100, le=8000)
    tools: Optional[List[str]] = None
    status: Optional[AgentStatusEnum] = None
    metadata: Optional[Dict[str, Any]] = None

    @field_validator('system_prompt')
    @classmethod
    def validate_prompt(cls, v):
        if v:
            return InputValidators.sanitize_code(v)
        return v

class ListAgentsResponse(BaseResponse):
    data: List[AgentDTO]
    pagination: PaginationResponse
