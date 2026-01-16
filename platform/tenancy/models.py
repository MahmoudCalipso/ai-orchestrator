"""
Tenant Database Model
"""

from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, Integer, Float
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Tenant(Base):
    """Tenant model for multi-tenancy support"""
    __tablename__ = "tenants"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    plan = Column(String, default="free")  # free, developer, pro, enterprise
    
    # Storage quotas
    storage_quota_gb = Column(Integer, default=10)
    storage_used_gb = Column(Float, default=0.0)
    
    # Workbench quotas
    workbench_quota = Column(Integer, default=3)  # -1 for unlimited
    
    # API rate limits (requests per minute)
    api_rate_limit = Column(Integer, default=100)  # -1 for unlimited
    
    # Billing
    stripe_customer_id = Column(String)
    stripe_subscription_id = Column(String)
    subscription_status = Column(String, default="active")  # active, canceled, past_due
    
    # Status
    is_active = Column(Boolean, default=True)
    trial_ends_at = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    users = relationship("User", back_populates="tenant")
    
    def __repr__(self):
        return f"<Tenant {self.name} ({self.plan})>"
    
    @property
    def is_unlimited_storage(self) -> bool:
        """Check if tenant has unlimited storage"""
        return self.storage_quota_gb == -1
    
    @property
    def is_unlimited_workbenches(self) -> bool:
        """Check if tenant has unlimited workbenches"""
        return self.workbench_quota == -1
    
    @property
    def storage_usage_percent(self) -> float:
        """Calculate storage usage percentage"""
        if self.is_unlimited_storage:
            return 0.0
        if self.storage_quota_gb == 0:
            return 100.0
        return (self.storage_used_gb / self.storage_quota_gb) * 100
