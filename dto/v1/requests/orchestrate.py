from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator
from enum import Enum
from app.schemas.validators import InputValidators

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

class MessageDTO(BaseModel):
    role: str
    content: str
    metadata: Optional[Dict[str, Any]] = None

class OrchestrationContext(BaseModel):
    code: Optional[str] = Field(None, max_length=50000)
    files: Optional[List[FileContext]] = None
    conversation_history: Optional[List[MessageDTO]] = None
    external_context: Optional[Dict[str, Any]] = None

class OrchestrationRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=10000, description="Task description for the agent swarm")
    context: Optional[OrchestrationContext] = None
    agent_selection: AgentSelectionMode = Field(default=AgentSelectionMode.AUTO)
    specific_agents: Optional[List[str]] = Field(None, description="Identifiers of agents to include if mode is MANUAL")
    execution_mode: ExecutionModeEnum = Field(default=ExecutionModeEnum.SEQUENTIAL)
    stream: bool = Field(default=True)
    max_iterations: int = Field(default=10, ge=1, le=50)

    @field_validator('prompt')
    @classmethod
    def validate_prompt(cls, v):
        return InputValidators.sanitize_code(v)
