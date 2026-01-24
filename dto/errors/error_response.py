from typing import Any, Optional, Dict
from pydantic import BaseModel, Field
from .base_response import BaseResponse

class ErrorDetail(BaseModel):
    field: Optional[str] = None
    message: str
    code: Optional[str] = None

class ErrorResponse(BaseResponse):
    """
    Standard error response with details
    """
    status: str = "error"
    details: Optional[Dict[str, Any]] = Field(None, description="Detailed error information")
    errors: Optional[list[ErrorDetail]] = Field(None, description="List of specific validation or logic errors")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "error",
                "code": "PROJECT_NOT_FOUND",
                "message": "The requested project does not exist",
                "details": {
                    "project_id": "abc123"
                },
                "timestamp": "2026-01-24T10:00:00Z"
            }
        }
