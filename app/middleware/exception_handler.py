import logging
import os
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from dto.v1.base import ErrorResponse, ErrorDetail, ResponseStatus

logger = logging.getLogger(__name__)

async def exception_handler_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as exc:
        return await handle_exception(request, exc)

async def handle_exception(request: Request, exc: Exception) -> JSONResponse:
    request_id = request.headers.get("X-Request-ID")
    
    if isinstance(exc, StarletteHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                status=ResponseStatus.ERROR,
                code=f"HTTP_{exc.status_code}",
                message=str(exc.detail),
                request_id=request_id,
                details={"path": request.url.path}
            ).model_dump(mode="json")
        )
        
    if isinstance(exc, RequestValidationError):
        errors = [
            ErrorDetail(
                field=".".join(map(str, err["loc"])), 
                message=err["msg"], 
                code=err["type"]
            )
            for err in exc.errors()
        ]
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=ErrorResponse(
                status=ResponseStatus.ERROR,
                code="VALIDATION_ERROR",
                message="Input validation failed",
                errors=errors,
                request_id=request_id,
                details={"path": request.url.path}
            ).model_dump(mode="json")
        )

    # Generic unhandled exception
    logger.error(f"Unhandled Exception: {exc}", exc_info=True)
    
    debug_info = None
    if os.getenv("DEBUG", "false").lower() == "true":
        debug_info = {
            "error_type": exc.__class__.__name__,
            "debug": str(exc)
        }
        
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            status=ResponseStatus.ERROR,
            code="INTERNAL_SERVER_ERROR",
            message="An unexpected server error occurred",
            request_id=request_id,
            details=debug_info or {"path": request.url.path}
        ).model_dump(mode="json")
    )

def register_exception_handlers(app):
    """Register custom exception handlers to the FastAPI app"""
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        return await handle_exception(request, exc)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return await handle_exception(request, exc)

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        return await handle_exception(request, exc)
