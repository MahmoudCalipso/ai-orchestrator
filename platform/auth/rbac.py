"""
Role-Based Access Control (RBAC)
Define roles, permissions, and access control logic
"""

from enum import Enum
from typing import List, Set


class Role(str, Enum):
    """User roles aligned with subscription tiers"""
    ADMIN = "admin"
    PRO = "pro"
    DEVELOPER = "developer"
    FREE = "free"


class Permission(str, Enum):
    """Granular permissions for features"""
    
    # Project permissions
    PROJECT_CREATE = "project:create"
    PROJECT_READ = "project:read"
    PROJECT_UPDATE = "project:update"
    PROJECT_DELETE = "project:delete"
    PROJECT_SHARE = "project:share"
    
    # Workbench permissions
    WORKBENCH_CREATE = "workbench:create"
    WORKBENCH_UNLIMITED = "workbench:unlimited"
    WORKBENCH_SHARE = "workbench:share"
    
    # Advanced features
    SWARM_AGENTS = "swarm:agents"
    KUBERNETES_DEPLOY = "kubernetes:deploy"
    FIGMA_INTEGRATION = "figma:integration"
    DATABASE_REVERSE_ENGINEER = "database:reverse_engineer"
    
    # Code operations
    CODE_GENERATE = "code:generate"
    CODE_MIGRATE = "code:migrate"
    CODE_ANALYZE = "code:analyze"
    CODE_FIX = "code:fix"
    CODE_OPTIMIZE = "code:optimize"
    CODE_REVIEW = "code:review"
    
    # Template marketplace
    TEMPLATE_USE = "template:use"
    TEMPLATE_SUBMIT = "template:submit"
    TEMPLATE_PURCHASE = "template:purchase"
    
    # Collaboration
    COLLAB_REALTIME = "collab:realtime"
    COLLAB_SCREEN_SHARE = "collab:screen_share"
    COLLAB_VOICE_CHAT = "collab:voice_chat"
    
    # Admin
    ADMIN_USERS = "admin:users"
    ADMIN_TENANTS = "admin:tenants"
    ADMIN_BILLING = "admin:billing"
    ADMIN_ANALYTICS = "admin:analytics"


# Role to permissions mapping
ROLE_PERMISSIONS: dict[Role, Set[Permission]] = {
    Role.FREE: {
        Permission.PROJECT_CREATE,
        Permission.PROJECT_READ,
        Permission.CODE_GENERATE,
        Permission.TEMPLATE_USE,
    },
    
    Role.DEVELOPER: {
        Permission.PROJECT_CREATE,
        Permission.PROJECT_READ,
        Permission.PROJECT_UPDATE,
        Permission.PROJECT_DELETE,
        Permission.WORKBENCH_CREATE,
        Permission.CODE_GENERATE,
        Permission.CODE_MIGRATE,
        Permission.CODE_ANALYZE,
        Permission.CODE_FIX,
        Permission.FIGMA_INTEGRATION,
        Permission.DATABASE_REVERSE_ENGINEER,
        Permission.TEMPLATE_USE,
        Permission.TEMPLATE_PURCHASE,
    },
    
    Role.PRO: {
        Permission.PROJECT_CREATE,
        Permission.PROJECT_READ,
        Permission.PROJECT_UPDATE,
        Permission.PROJECT_DELETE,
        Permission.PROJECT_SHARE,
        Permission.WORKBENCH_CREATE,
        Permission.WORKBENCH_UNLIMITED,
        Permission.WORKBENCH_SHARE,
        Permission.SWARM_AGENTS,
        Permission.KUBERNETES_DEPLOY,
        Permission.FIGMA_INTEGRATION,
        Permission.DATABASE_REVERSE_ENGINEER,
        Permission.CODE_GENERATE,
        Permission.CODE_MIGRATE,
        Permission.CODE_ANALYZE,
        Permission.CODE_FIX,
        Permission.CODE_OPTIMIZE,
        Permission.CODE_REVIEW,
        Permission.TEMPLATE_USE,
        Permission.TEMPLATE_SUBMIT,
        Permission.TEMPLATE_PURCHASE,
        Permission.COLLAB_REALTIME,
        Permission.COLLAB_SCREEN_SHARE,
    },
    
    Role.ADMIN: set(Permission),  # All permissions
}


class RBACManager:
    """Role-Based Access Control Manager"""
    
    @staticmethod
    def check_permission(user_role: Role, required_permission: Permission) -> bool:
        """
        Check if a role has a specific permission
        
        Args:
            user_role: User's role
            required_permission: Permission to check
            
        Returns:
            True if role has permission, False otherwise
        """
        user_permissions = ROLE_PERMISSIONS.get(user_role, set())
        return required_permission in user_permissions
    
    @staticmethod
    def has_permissions(user_role: Role, permissions: List[Permission]) -> bool:
        """
        Check if a role has all specified permissions
        
        Args:
            user_role: User's role
            permissions: List of permissions to check
            
        Returns:
            True if role has all permissions, False otherwise
        """
        user_permissions = ROLE_PERMISSIONS.get(user_role, set())
        return all(p in user_permissions for p in permissions)
    
    @staticmethod
    def get_role_permissions(user_role: Role) -> Set[Permission]:
        """
        Get all permissions for a role
        
        Args:
            user_role: User's role
            
        Returns:
            Set of permissions
        """
        return ROLE_PERMISSIONS.get(user_role, set())
    
    @staticmethod
    def can_access_feature(user_role: Role, feature: str) -> bool:
        """
        Check if user can access a feature based on their role
        
        Args:
            user_role: User's role
            feature: Feature name (e.g., 'swarm_agents', 'kubernetes')
            
        Returns:
            True if user can access feature
        """
        feature_permission_map = {
            "swarm_agents": Permission.SWARM_AGENTS,
            "kubernetes": Permission.KUBERNETES_DEPLOY,
            "figma": Permission.FIGMA_INTEGRATION,
            "unlimited_workbenches": Permission.WORKBENCH_UNLIMITED,
            "collaboration": Permission.COLLAB_REALTIME,
            "screen_share": Permission.COLLAB_SCREEN_SHARE,
        }
        
        required_permission = feature_permission_map.get(feature)
        if not required_permission:
            return False
        
        return RBACManager.check_permission(user_role, required_permission)
