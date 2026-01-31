from typing import Any, Optional, Dict, Generic, TypeVar, List
from pydantic import BaseModel, Field
from datetime import datetime
import enum

T = TypeVar("T")

class ResponseStatus(str, enum.Enum):
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"

class BaseResponse(BaseModel, Generic[T]):
    """
    Standard API Response Envelope
    """
    status: ResponseStatus = Field(..., description="High-level result state")
    code: str = Field(..., description="Machine-readable action status code (e.g., USER_CREATED)")
    message: Optional[str] = Field(None, description="Human-readable status message")
    data: Optional[T] = Field(None, description="The main response payload")
    meta: Dict[str, Any] = Field(default_factory=dict, description="Metadata like trace IDs, timers, or pagination")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="ISO timestamp of the response")

class PaginationParams(BaseModel):
    """
    Standard Pagination Request Parameters
    """
    page: int = Field(1, ge=1, description="Page number (1-indexed)", example=1)
    page_size: int = Field(20, ge=1, le=100, description="Items per page", example=20)
    sort_by: Optional[str] = Field(None, description="Field name to sort by", example="created_at")
    sort_order: str = Field("desc", pattern="^(asc|desc)$", description="Sorting direction")

class PaginationMetadata(BaseModel):
    total: int = Field(..., description="Total number of items available")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Number of items per page")
    pages: int = Field(..., description="Total number of pages")

class PaginatedResponse(BaseResponse[List[T]], Generic[T]):
    """
    Standard Paginated Response Envelope
    """
    meta: Dict[str, Any] = Field(..., description="Metadata including pagination details")

class ErrorDetail(BaseModel):
    field: Optional[str] = Field(None, description="The specific field that caused the error")
    message: str = Field(..., description="Detailed error description")
    code: Optional[str] = Field(None, description="Detailed error category code")

class ErrorResponse(BaseResponse[None]):
    """
    Standard Error Response Envelope
    """
    status: ResponseStatus = ResponseStatus.ERROR
    errors: Optional[List[ErrorDetail]] = Field(None, description="List of specific validation or business errors")
    request_id: Optional[str] = Field(None, description="Unique trace ID for support or debugging")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional debug or context information")
