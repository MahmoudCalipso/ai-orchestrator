from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from .enums import TaskType

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
    stream: Optional[bool] = Field(default=False)

class InferenceRequest(BaseModel):
    """Inference request schema"""
    prompt: str = Field(..., min_length=1)
    task_type: Optional[TaskType] = TaskType.CHAT
    model: Optional[str] = None
    parameters: Optional[InferenceParameters] = Field(default_factory=InferenceParameters)
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
