"""
Audit Service
Handles recording and retrieving system audit logs.
"""
import uuid
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from sqlalchemy.orm import Session
from platform_core.auth.audit_model import AuditLog

logger = logging.getLogger(__name__)

class AuditService:
    def __init__(self, db: Session):
        self.db = db

    def log_action(self, user_id: str, action: str, tenant_id: str = None, 
                   resource_id: str = None, details: Dict[str, Any] = None, ip_address: str = None):
        """Record an audit event"""
        try:
            log_entry = AuditLog(
                id=str(uuid.uuid4()),
                user_id=user_id,
                tenant_id=tenant_id,
                action=action,
                resource_id=resource_id,
                details=details or {},
                ip_address=ip_address,
                timestamp=datetime.utcnow()
            )
            self.db.add(log_entry)
            self.db.commit()
        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")
            self.db.rollback()

    def get_logs(self, limit: int = 50, user_id: str = None, tenant_id: str = None, action: str = None) -> List[AuditLog]:
        """Retrieve audit logs with filtering"""
        query = self.db.query(AuditLog)
        
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        if tenant_id:
            query = query.filter(AuditLog.tenant_id == tenant_id)
        if action:
            query = query.filter(AuditLog.action == action)
            
        return query.order_by(AuditLog.timestamp.desc()).limit(limit).all()
