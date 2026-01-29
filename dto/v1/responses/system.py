from typing import Dict, Any, List
from pydantic import BaseModel, Field

class SystemInfoDTO(BaseModel):
    service: str = "AI Orchestrator"
    version: str = "1.0.0"
    status: str = "running"
from schemas.spec import ModelStatus

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
