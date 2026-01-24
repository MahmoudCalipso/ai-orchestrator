from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from schemas.spec import ModelStatus

class InferenceResponseDTO(BaseModel):
    request_id: str
    model: str
    runtime: str
    output: str
    tokens_used: int
    processing_time: float
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ModelInfoDTO(BaseModel):
    name: str
    family: str
    size: str
    context_length: int
    capabilities: List[str]
    specialization: str
    status: ModelStatus
    quantization: Optional[List[str]] = None

class SwarmResponseDTO(BaseModel):
    status: str = "success"
    type: str
    decomposition: Optional[List[Dict[str, Any]]] = None
    worker_results: Optional[Dict[str, Any]] = None
    migrated_files: Optional[Dict[str, str]] = None
    generated_files: Optional[Dict[str, str]] = None
    agent: Optional[str] = None
