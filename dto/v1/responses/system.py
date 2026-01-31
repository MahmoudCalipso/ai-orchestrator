from typing import Dict, Any, List
from pydantic import BaseModel, Field
from dto.v1.schemas.enums import ModelStatus

class SystemInfoDTO(BaseModel):
    service: str = "AI Orchestrator"
    version: str = "1.0.0"
    status: str = "running"

class HealthResponseDTO(BaseModel):
    status: str
    version: str
    uptime: float
    models_loaded: int
    runtimes_available: List[str]

class SystemStatusDTO(BaseModel):
    status: str
    uptime: float
    models: Dict[str, ModelStatus]
    runtimes: Dict[str, Dict[str, Any]]
    resources: Dict[str, Any]
    metrics: Dict[str, Any]
