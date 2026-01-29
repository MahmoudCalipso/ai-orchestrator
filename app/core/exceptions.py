"""Centralized exception handling for the AI Orchestrator."""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional
import logging
import traceback
import os
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

class BaseAppException(Exception):
    def __init__(
        self, 
        message: str, 
        status_code: int = 500, 
        error_code: str = "INTERNAL_ERROR",
        details: Dict[str, Any] = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        self.request_id = str(uuid.uuid4())
        super().__init__(self.message)

class ProjectNotFoundException(BaseAppException):
    def __init__(self, project_id: str):
        super().__init__(
            message=f"Project {project_id} not found",
            status_code=404,
            error_code="NOT_FOUND",
            details={"project_id": project_id, "resource": "project"}
        )

class AIModelException(BaseAppException):
    def __init__(self, message: str, model_name: str):
        super().__init__(
            message=message,
            status_code=503,
            error_code="MODEL_UNAVAILABLE",
            details={"model": model_name, "type": "ai_inference_error"}
        )

class ResourceLimitException(BaseAppException):
    def __init__(self, resource_type: str, limit: int):
        super().__init__(
            message=f"{resource_type} limit exceeded: {limit}",
            status_code=429,
            error_code="RATE_LIMIT_EXCEEDED",
            details={"resource_type": resource_type, "limit": limit}
        )

class AuthenticationException(BaseAppException):
    def __init__(self, message: str = "Authentication required"):
        super().__init__(
            message=message,
            status_code=401,
            error_code="AUTHENTICATION_ERROR"
        )

class PromptInjectionException(BaseAppException):
    def __init__(self, risk_level: str, risk_score: float, patterns: list):
        super().__init__(
            message="Potentially malicious prompt detected",
            status_code=400,
            error_code="PROMPT_INJECTION_DETECTED",
            details={
                "risk_level": risk_level,
                "risk_score": risk_score,
                "detected_patterns": patterns
            }
        )

from dto.v1.base import ErrorResponse, ResponseStatus, ErrorDetail

async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for all unhandled exceptions."""
    
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    
    if isinstance(exc, BaseAppException):
        logger.warning(f"{exc.__class__.__name__}: {exc.message}", extra=exc.details)
        
        # Standardize error response
        response = ErrorResponse(
            status=ResponseStatus.ERROR,
            code=exc.error_code,
            message=exc.message,
            request_id=request_id,
            meta=exc.details
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=response.model_dump()
        )
    
    # Log unexpected errors
    logger.error(
        f"Unexpected error: {str(exc)}",
        exc_info=True,
        extra={
            "path": str(request.url),
            "method": request.method,
            "request_id": request_id
        }
    )
    
    # Standardize internal error
    response = ErrorResponse(
        status=ResponseStatus.ERROR,
        code="INTERNAL_ERROR",
        message="An unexpected error occurred. Please contact support.",
        request_id=request_id,
        meta={
            "error_type": exc.__class__.__name__,
            "debug": str(exc) if os.getenv("DEBUG") == "true" else "Hidden in production"
        }
    )
    
    return JSONResponse(
        status_code=500,
        content=response.model_dump()
    )

