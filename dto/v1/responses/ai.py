from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from schemas.spec import ModelStatus

class InferenceResponseDTO(BaseModel):
    """Detailed result of an AI inference operation"""
    request_id: str = Field(..., description="Unique trace ID for this inference request", example="inf-77b3-4f92")
    model: str = Field(..., description="Name of the model that processed the request", example="mistral-7b")
    runtime: str = Field(..., description="Backend runtime that executed the model", example="ollama")
    output: str = Field(..., description="The main generated text or data content")
    tokens_used: int = Field(..., description="Total token consumption (input + output)", example=156)
    processing_time: float = Field(..., description="Total wall-clock time in seconds", example=0.45)
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Extension metadata including performance metrics")

    class Config:
        from_attributes = True

class ModelInfoDTO(BaseModel):
    """Comprehensive metadata for a specific AI model"""
    name: str = Field(..., description="Display name of the model", example="Mistral 7B v0.2")
    family: str = Field(..., description="Model architecture family", example="mistral")
    size: str = Field(..., description="Model parameter size or weight size", example="7.2GB")
    context_length: int = Field(..., description="Maximum supported context window size", example=32768)
    capabilities: List[str] = Field(..., description="List of supported AI features", example=["chat", "code", "embeddings"])
    specialization: str = Field(..., description="Primary use-case optimization", example="general-purpose coding")
    status: ModelStatus = Field(..., description="Current operational state of the model")
    quantization: Optional[List[str]] = Field(None, description="Available quantization levels")

    class Config:
        from_attributes = True

class SwarmResponseDTO(BaseModel):
    """Encapsulation of complex multiservice AI swarm operations"""
    status: str = Field("success", description="Overall outcome of the swarm coordination", example="success")
    type: str = Field(..., description="Category of the swarm task performed", example="project_migration")
    decomposition: Optional[List[Dict[str, Any]]] = Field(None, description="Step-by-step task breakdown planned by the lead architect")
    worker_results: Optional[Dict[str, Any]] = Field(None, description="Aggregated results from individual agent workers")
    migrated_files: Optional[Dict[str, str]] = Field(None, description="Map of file paths to their new transformed content")
    generated_files: Optional[Dict[str, str]] = Field(None, description="Map of newly created file paths and their content")
    agent: Optional[str] = Field(None, description="Primary agent responsible for the outcome", example="LeadArchitect")

    class Config:
        from_attributes = True

class ModelSummaryDTO(BaseModel):
    """Succinct Metadata for Model Discovery"""
    name: str = Field(..., description="Display name of the model", example="mistral-7b")
    provider: str = Field(..., description="Inference backend provider", example="ollama")
    is_local: bool = Field(True, description="Indicates if the model is locally hosted")
    size: Optional[str] = Field(None, description="Reported model size on disk")

    class Config:
        from_attributes = True

class ModelListResponseDTO(BaseModel):
    """Paginated collection of available AI models"""
    models: List[ModelSummaryDTO] = Field(..., description="List of models for the current page")
    total: int = Field(..., description="Total number of models matching filters")
