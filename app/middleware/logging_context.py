import uuid
from fastapi import Request
from core.utils.logging import trace_id_var, user_id_var

async def logging_context_middleware(request: Request, call_next):
    """
    Middleware to inject trace_id and user_id into the logging context.
    """
    # Extract or generate trace_id
    trace_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    
    # Set context variables
    trace_token = trace_id_var.set(trace_id)
    
    # User ID will be set by auth middleware later, 
    # but we can try to get it if already present in state
    user_id = getattr(request.state, "user_id", None)
    user_token = user_id_var.set(user_id)
    
    try:
        response = await call_next(request)
        # Add trace ID to response headers
        response.headers["X-Request-ID"] = trace_id
        return response
    finally:
        # Reset context variables for this event loop task
        trace_id_var.reset(trace_token)
        user_id_var.reset(user_token)
