from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

class AgentStatusEnum(str, Enum):
    IDLE = "idle"
    INITIALIZING = "initializing"
    ACTIVE = "active"
    PAUSED = "paused"
    ERROR = "error"
    TERMINATED = "terminated"
    ARCHIVED = "archived"

class AgentResponseDTO(BaseModel):
    id: str = Field(..., description="Unique agent identifier")
    name: str = Field(..., description="Internal agent name")
    display_name: str = Field(..., description="Display name for users")
    description: Optional[str] = Field(None)
    agent_type: str = Field(..., description="Functional role")
    status: AgentStatusEnum = Field(..., description="Current operational state")
    model: str = Field(..., description="Associated LLM")
    temperature: float = Field(...)
    max_tokens: int = Field(...)
    tools: List[str] = Field(default_factory=list)
    created_at: datetime = Field(...)
    updated_at: datetime = Field(...)
    user_id: str = Field(...)
    session_count: int = Field(0)
    total_tokens_used: int = Field(0)
    last_active_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

class AgentInitializationResponseDTO(BaseModel):
    agent: AgentResponseDTO
    initialization_status: str = Field(..., description="Status of the background initialization process")
    websocket_url: Optional[str] = Field(None, description="Stream endpoint for real-time interaction")
