from typing import Any, Optional, Dict, Generic, TypeVar, Union, List
from pydantic import BaseModel, Field
from datetime import datetime

T = TypeVar("T")

class BaseResponse(BaseModel, Generic[T]):
    """
    Standard API Response Contract
    """
    status: str = Field(..., description="High-level execution result: 'success' | 'error' | 'warning'")
    code: str = Field(..., description="Stable machine-readable action identifier")
    message: Optional[str] = Field(None, description="Human readable description")
    data: Optional[T] = Field(None, description="The main payload (business data)")
    meta: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Metadata including pagination, traces, and metrics")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Standard ISO timestamp of response")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "code": "ACTION_SUCCESS",
                "message": "Operation completed successfully",
                "data": {},
                "meta": {},
                "timestamp": "2026-01-24T10:00:00Z"
            }
        }
