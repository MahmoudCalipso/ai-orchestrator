from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator
from enum import Enum
from app.schemas.validators import InputValidators

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

class CreateAgentRequest(BaseModel):
    name: str = Field(..., min_length=3, max_length=100, description="Slug-friendly agent name")
    display_name: str = Field(..., min_length=3, max_length=200, description="Public display name")
    description: Optional[str] = Field(None, max_length=1000, description="Detailed agent purpose")
    agent_type: AgentTypeEnum = Field(..., description="Functional role of the agent")
    model: str = Field(default="qwen2.5-coder:7b", description="LLM identifier")
    system_prompt: Optional[str] = Field(None, max_length=10000, description="Base instructions for the AI")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Sampling temperature")
    max_tokens: int = Field(default=2000, ge=100, le=8000, description="Output length limit")
    tools: List[str] = Field(default_factory=list, description="Enabled toolset identifiers")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Arbitrary agent metadata")

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

class UpdateAgentRequest(BaseModel):
    display_name: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    system_prompt: Optional[str] = Field(None, max_length=10000)
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(None, ge=100, le=8000)
    tools: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

    @field_validator('system_prompt')
    @classmethod
    def validate_prompt(cls, v):
        if v:
            return InputValidators.sanitize_code(v)
        return v
