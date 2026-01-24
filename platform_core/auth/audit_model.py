"""
Audit Log Model
"""
from datetime import datetime
from sqlalchemy import Column, String, DateTime, JSON, Text
from platform_core.database import Base

class AuditLog(Base):
    """Audit Log entry for system-wide actions"""
    __tablename__ = "audit_logs"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, index=True)
    tenant_id = Column(String, index=True, nullable=True)
    action = Column(String, index=True) # e.g., "PROJECT_CREATED", "USER_DELETED"
    resource_id = Column(String, index=True, nullable=True)
    details = Column(JSON, default={})
    ip_address = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f"<AuditLog {self.action} by {self.user_id}>"
