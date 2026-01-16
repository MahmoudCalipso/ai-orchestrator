"""
Tenant Manager
Handle tenant isolation, quotas, and resource management
"""

import os
from pathlib import Path
from typing import Optional
from sqlalchemy.orm import Session
from .models import Tenant


class TenantManager:
    """Manage tenant resources and enforce quotas"""
    
    def __init__(self, db_session: Session, storage_base_path: str = "storage"):
        self.db = db_session
        self.storage_base_path = Path(storage_base_path)
    
    def get_tenant(self, tenant_id: str) -> Optional[Tenant]:
        """
        Get tenant by ID
        
        Args:
            tenant_id: Tenant ID
            
        Returns:
            Tenant object or None
        """
        return self.db.query(Tenant).filter(Tenant.id == tenant_id).first()
    
    def get_tenant_storage_path(self, tenant_id: str) -> Path:
        """
        Get tenant's isolated storage path
        
        Args:
            tenant_id: Tenant ID
            
        Returns:
            Path to tenant's storage directory
        """
        tenant_path = self.storage_base_path / "tenants" / tenant_id
        tenant_path.mkdir(parents=True, exist_ok=True)
        return tenant_path
    
    def check_storage_quota(self, tenant_id: str, additional_gb: float = 0) -> bool:
        """
        Check if tenant has available storage quota
        
        Args:
            tenant_id: Tenant ID
            additional_gb: Additional storage to check (in GB)
            
        Returns:
            True if quota available, False otherwise
        """
        tenant = self.get_tenant(tenant_id)
        if not tenant:
            return False
        
        # Unlimited storage
        if tenant.is_unlimited_storage:
            return True
        
        # Check quota
        projected_usage = tenant.storage_used_gb + additional_gb
        return projected_usage <= tenant.storage_quota_gb
    
    def update_storage_usage(self, tenant_id: str, size_gb: float):
        """
        Update tenant's storage usage
        
        Args:
            tenant_id: Tenant ID
            size_gb: Size to add (positive) or remove (negative) in GB
        """
        tenant = self.get_tenant(tenant_id)
        if tenant:
            tenant.storage_used_gb = max(0, tenant.storage_used_gb + size_gb)
            self.db.commit()
    
    def calculate_storage_usage(self, tenant_id: str) -> float:
        """
        Calculate actual storage usage from filesystem
        
        Args:
            tenant_id: Tenant ID
            
        Returns:
            Storage usage in GB
        """
        tenant_path = self.get_tenant_storage_path(tenant_id)
        
        total_size = 0
        for item in tenant_path.rglob("*"):
            if item.is_file():
                total_size += item.stat().st_size
        
        # Convert bytes to GB
        return total_size / (1024 ** 3)
    
    def check_workbench_quota(self, tenant_id: str) -> bool:
        """
        Check if tenant can create more workbenches
        
        Args:
            tenant_id: Tenant ID
            
        Returns:
            True if quota available, False otherwise
        """
        tenant = self.get_tenant(tenant_id)
        if not tenant:
            return False
        
        # Unlimited workbenches
        if tenant.is_unlimited_workbenches:
            return True
        
        # Count active workbenches (this would query workbench table)
        # For now, returning True - implement actual counting later
        active_count = self.count_active_workbenches(tenant_id)
        return active_count < tenant.workbench_quota
    
    def count_active_workbenches(self, tenant_id: str) -> int:
        """
        Count active workbenches for tenant
        
        Args:
            tenant_id: Tenant ID
            
        Returns:
            Number of active workbenches
        """
        # TODO: Implement actual workbench counting
        # This would query the workbench table when it's created
        return 0
    
    def get_rate_limit(self, tenant_id: str) -> int:
        """
        Get API rate limit for tenant
        
        Args:
            tenant_id: Tenant ID
            
        Returns:
            Rate limit (requests per minute), -1 for unlimited
        """
        tenant = self.get_tenant(tenant_id)
        if not tenant:
            return 100  # Default rate limit
        
        return tenant.api_rate_limit
    
    def is_feature_enabled(self, tenant_id: str, feature: str) -> bool:
        """
        Check if a feature is enabled for tenant's plan
        
        Args:
            tenant_id: Tenant ID
            feature: Feature name
            
        Returns:
            True if feature is enabled
        """
        tenant = self.get_tenant(tenant_id)
        if not tenant:
            return False
        
        # Feature availability by plan
        feature_plans = {
            "swarm_agents": ["pro", "enterprise"],
            "kubernetes": ["pro", "enterprise"],
            "figma": ["developer", "pro", "enterprise"],
            "unlimited_workbenches": ["pro", "enterprise"],
            "collaboration": ["pro", "enterprise"],
            "custom_templates": ["pro", "enterprise"],
        }
        
        allowed_plans = feature_plans.get(feature, [])
        return tenant.plan in allowed_plans
    
    def upgrade_plan(self, tenant_id: str, new_plan: str):
        """
        Upgrade tenant's subscription plan
        
        Args:
            tenant_id: Tenant ID
            new_plan: New plan name (free, developer, pro, enterprise)
        """
        tenant = self.get_tenant(tenant_id)
        if not tenant:
            return
        
        # Update plan and quotas
        tenant.plan = new_plan
        
        # Update quotas based on plan
        plan_quotas = {
            "free": {"storage": 10, "workbenches": 3, "rate_limit": 100},
            "developer": {"storage": 50, "workbenches": 10, "rate_limit": 500},
            "pro": {"storage": 200, "workbenches": -1, "rate_limit": 2000},
            "enterprise": {"storage": -1, "workbenches": -1, "rate_limit": -1},
        }
        
        quotas = plan_quotas.get(new_plan, plan_quotas["free"])
        tenant.storage_quota_gb = quotas["storage"]
        tenant.workbench_quota = quotas["workbenches"]
        tenant.api_rate_limit = quotas["rate_limit"]
        
        self.db.commit()
