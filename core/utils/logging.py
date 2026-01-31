import logging
import uuid
import contextvars
from typing import Optional

# Context variables for request tracking
trace_id_var = contextvars.ContextVar("trace_id", default=None)
user_id_var = contextvars.ContextVar("user_id", default=None)

class ContextFilter(logging.Filter):
    """
    Logging filter that injects trace_id and user_id into log records.
    """
    def filter(self, record):
        record.trace_id = trace_id_var.get()
        record.user_id = user_id_var.get()
        return True

def setup_logging(level: str = "INFO"):
    """
    Configure structured logging with context variables.
    """
    log_format = (
        "%(asctime)s - %(name)s - %(levelname)s - "
        "[trace_id=%(trace_id)s user_id=%(user_id)s] - %(message)s"
    )
    
    # Root logger configuration
    logging.basicConfig(level=level)
    
    # Clear existing handlers
    root = logging.getLogger()
    for handler in root.handlers[:]:
        root.removeHandler(handler)
        
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(log_format))
    handler.addFilter(ContextFilter())
    
    root.addHandler(handler)
    root.setLevel(level)

def set_logging_context(trace_id: Optional[str] = None, user_id: Optional[str] = None):
    """Helper to set context manually (e.g. for background tasks)"""
    if trace_id:
        trace_id_var.set(trace_id)
    if user_id:
        user_id_var.set(user_id)
