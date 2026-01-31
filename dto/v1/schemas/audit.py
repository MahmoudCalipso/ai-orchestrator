from typing import Dict, Any
from pydantic import BaseModel, Field

class AuditLog(BaseModel):
    """Audit log entry"""
    timestamp: float
    user: str
    action: str
    resource: str
    details: Dict[str, Any]
    status: str
