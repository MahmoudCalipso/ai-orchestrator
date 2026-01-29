from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

class ExecutionStatusEnum(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"

class OrchestrationResponseDTO(BaseModel):
    execution_id: str = Field(..., description="Unique execution identifier")
    status: ExecutionStatusEnum = Field(..., description="Current operational state of the task")
    message: str = Field(..., description="Status description or next steps")
    result_url: str = Field(..., description="URI to pull historical results")
    websocket_url: Optional[str] = Field(None, description="Live stream channel")
    estimated_duration_ms: int = Field(0, description="Expected time to completion")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
