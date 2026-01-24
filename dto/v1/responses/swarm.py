from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

class SwarmResponse(BaseModel):
    """Response from a swarm-powered operation"""
    status: str = "success"
    type: str
    decomposition: Optional[List[Dict[str, Any]]] = None
    worker_results: Optional[Dict[str, Any]] = None
    migrated_files: Optional[Dict[str, str]] = None
    generated_files: Optional[Dict[str, str]] = None
    documentation: Optional[str] = None
    agent: Optional[str] = Field(None, description="The agent that handled the request")
