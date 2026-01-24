from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class MetadataDTO(BaseModel):
    """
    System telemetry and execution traces
    """
    trace_id: Optional[str] = Field(None, description="Unique trace identifier for observability")
    execution_time_ms: Optional[float] = Field(None, description="Time taken to process the request")
    version: str = Field("1.0.0", description="API version")
    environment: str = Field("production", description="Server environment")
    extra: Dict[str, Any] = Field(default_factory=dict, description="Additional contextual information")
