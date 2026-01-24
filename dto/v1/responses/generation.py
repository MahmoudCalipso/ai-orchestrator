from typing import Dict, Any
from pydantic import BaseModel, Field

class DescriptionAnalysisResponseDTO(BaseModel):
    """Response with full auto-generated configuration"""
    analysis: Dict[str, Any]
    generated_config: Dict[str, Any]
    summary: str
