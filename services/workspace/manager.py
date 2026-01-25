"""
Team Workspace Management
Provides multi-user workspace management with role-based permissions
"""
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum


class WorkspaceRole(str, Enum):
    """Workspace roles aligned with global tiers"""
    ADMIN = "admin"
    ENTERPRISE = "enterprise"
    PRO_DEVELOPER = "pro_developer"
    DEVELOPER = "developer"


class Permission(str, Enum):
    """Workspace permissions"""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    MANAGE_MEMBERS = "manage_members"
    MANAGE_SETTINGS = "manage_settings"


# Role permissions mapping (Hierarchical)
ROLE_PERMISSIONS = {
    WorkspaceRole.ADMIN: [
        Permission.READ,
        Permission.WRITE,
        Permission.DELETE,
        Permission.MANAGE_MEMBERS,
        Permission.MANAGE_SETTINGS
    ],
    WorkspaceRole.ENTERPRISE: [
        Permission.READ,
        Permission.WRITE,
        Permission.DELETE,
        Permission.MANAGE_MEMBERS
    ],
    WorkspaceRole.PRO_DEVELOPER: [
        Permission.READ,
        Permission.WRITE
    ],
    WorkspaceRole.DEVELOPER: [
        Permission.READ
    ]
}


class WorkspaceMember:
    """Workspace member"""
    
    def __init__(self, user_id: str, username: str, role: WorkspaceRole):
        self.user_id = user_id
        self.username = username
        self.role = role
        self.joined_at = datetime.utcnow()
    
    def has_permission(self, permission: Permission) -> bool:
        """Check if member has permission"""
        return permission in ROLE_PERMISSIONS.get(self.role, [])
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "username": self.username,
            "role": self.role.value,
            "joined_at": self.joined_at.isoformat()
        }


class WorkspaceSettings:
    """Workspace settings"""
    
    def __init__(self):
        self.default_language = "python"
        self.default_framework = "fastapi"
        self.enable_ai_assistance = True
        self.enable_collaboration = True
        self.max_storage_gb = 100
        self.max_projects = 50
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "default_language": self.default_language,
            "default_framework": self.default_framework,
            "enable_ai_assistance": self.enable_ai_assistance,
            "enable_collaboration": self.enable_collaboration,
            "max_storage_gb": self.max_storage_gb,
            "max_projects": self.max_projects
        }


class Workspace:
    """Workspace"""
    
    def __init__(
        self,
        workspace_id: str,
        name: str,
        owner_id: str,
        owner_name: str
    ):
        self.id = workspace_id
        self.name = name
        self.owner_id = owner_id
        self.members: Dict[str, WorkspaceMember] = {}
        self.projects: List[str] = []
        self.settings = WorkspaceSettings()
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.activities: List[Dict[str, Any]] = []
        
        # Add owner as member
        self.members[owner_id] = WorkspaceMember(
            owner_id,
            owner_name,
            WorkspaceRole.OWNER
        )
        self.log_activity("workspace_created", f"Workspace '{name}' created by {owner_name}")

    def log_activity(self, activity_type: str, message: str, user_id: Optional[str] = None):
        """Record a workspace activity"""
        self.activities.insert(0, {
            "type": activity_type,
            "timestamp": datetime.utcnow().isoformat(),
            "message": message,
            "user_id": user_id
        })
        # Keep only last 100 activities
        if len(self.activities) > 100:
            self.activities = self.activities[:100]
    
    def add_member(self, user_id: str, username: str, role: WorkspaceRole) -> bool:
        """Add member to workspace"""
        if user_id in self.members:
            return False
        
        self.members[user_id] = WorkspaceMember(user_id, username, role)
        self.updated_at = datetime.utcnow()
        self.log_activity("member_added", f"User {username} added as {role.value}", user_id)
        return True
    
    def remove_member(self, user_id: str) -> bool:
        """Remove member from workspace"""
        if user_id == self.owner_id:
            return False  # Cannot remove owner
        
        if user_id in self.members:
            del self.members[user_id]
            self.updated_at = datetime.utcnow()
            return True
        return False
    
    def update_member_role(self, user_id: str, new_role: WorkspaceRole) -> bool:
        """Update member role"""
        if user_id == self.owner_id:
            return False  # Cannot change owner role
        
        member = self.members.get(user_id)
        if member:
            member.role = new_role
            self.updated_at = datetime.utcnow()
            return True
        return False
    
    def has_permission(self, user_id: str, permission: Permission) -> bool:
        """Check if user has permission"""
        member = self.members.get(user_id)
        if not member:
            return False
        return member.has_permission(permission)
    
    def add_project(self, project_id: str) -> bool:
        """Add project to workspace"""
        if project_id not in self.projects:
            self.projects.append(project_id)
            self.updated_at = datetime.utcnow()
            return True
        return False
    
    def remove_project(self, project_id: str) -> bool:
        """Remove project from workspace"""
        if project_id in self.projects:
            self.projects.remove(project_id)
            self.updated_at = datetime.utcnow()
            return True
        return False
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get workspace usage statistics"""
        return {
            "total_members": len(self.members),
            "total_projects": len(self.projects),
            "storage_used_gb": 0,  # Would calculate actual storage
            "storage_limit_gb": self.settings.max_storage_gb,
            "projects_limit": self.settings.max_projects
        }
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "owner_id": self.owner_id,
            "members": [m.to_dict() for m in self.members.values()],
            "projects": self.projects,
            "settings": self.settings.to_dict(),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "usage_stats": self.get_usage_stats()
        }


class WorkspaceManager:
    """Workspace manager"""
    
    def __init__(self):
        self.workspaces: Dict[str, Workspace] = {}
        self.user_workspaces: Dict[str, List[str]] = {}  # user_id -> workspace_ids
    
    def create_workspace(
        self,
        name: str,
        owner_id: str,
        owner_name: str
    ) -> Workspace:
        """Create new workspace"""
        workspace_id = str(uuid.uuid4())
        workspace = Workspace(workspace_id, name, owner_id, owner_name)
        
        self.workspaces[workspace_id] = workspace
        
        # Track user workspaces
        if owner_id not in self.user_workspaces:
            self.user_workspaces[owner_id] = []
        self.user_workspaces[owner_id].append(workspace_id)
        
        return workspace
    
    def get_workspace(self, workspace_id: str) -> Optional[Workspace]:
        """Get workspace by ID"""
        return self.workspaces.get(workspace_id)
    
    def delete_workspace(self, workspace_id: str, user_id: str) -> bool:
        """Delete workspace (only owner can delete)"""
        workspace = self.workspaces.get(workspace_id)
        if not workspace or workspace.owner_id != user_id:
            return False
        
        # Remove from all members' workspace lists
        for member_id in workspace.members.keys():
            if member_id in self.user_workspaces:
                self.user_workspaces[member_id].remove(workspace_id)
        
        del self.workspaces[workspace_id]
        return True
    
    def list_user_workspaces(
        self, 
        user_id: str,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """List workspaces for user with pagination"""
        workspace_ids = self.user_workspaces.get(user_id, [])
        all_user_workspaces = [self.workspaces[wid] for wid in workspace_ids if wid in self.workspaces]
        
        total = len(all_user_workspaces)
        start = (page - 1) * page_size
        end = start + page_size
        paginated_workspaces = all_user_workspaces[start:end]
        
        return {
            "workspaces": paginated_workspaces,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }
    
    def invite_member(
        self,
        workspace_id: str,
        inviter_id: str,
        user_id: str,
        username: str,
        role: WorkspaceRole = WorkspaceRole.DEVELOPER
    ) -> bool:
        """Invite member to workspace"""
        workspace = self.workspaces.get(workspace_id)
        if not workspace:
            return False
        
        # Check if inviter has permission
        if not workspace.has_permission(inviter_id, Permission.MANAGE_MEMBERS):
            return False
        
        # Add member
        if workspace.add_member(user_id, username, role):
            # Track user workspace
            if user_id not in self.user_workspaces:
                self.user_workspaces[user_id] = []
            self.user_workspaces[user_id].append(workspace_id)
            return True
        
        return False
    
    def remove_member(
        self,
        workspace_id: str,
        remover_id: str,
        user_id: str
    ) -> bool:
        """Remove member from workspace"""
        workspace = self.workspaces.get(workspace_id)
        if not workspace:
            return False
        
        # Check if remover has permission
        if not workspace.has_permission(remover_id, Permission.MANAGE_MEMBERS):
            return False
        
        # Remove member
        if workspace.remove_member(user_id):
            # Update user workspaces
            if user_id in self.user_workspaces:
                self.user_workspaces[user_id].remove(workspace_id)
            return True
        
        return False
    
    def update_settings(
        self,
        workspace_id: str,
        user_id: str,
        settings: Dict[str, Any]
    ) -> bool:
        """Update workspace settings"""
        workspace = self.workspaces.get(workspace_id)
        if not workspace:
            return False
        
        # Check if user has permission
        if not workspace.has_permission(user_id, Permission.MANAGE_SETTINGS):
            return False
        
        # Update settings
        for key, value in settings.items():
            if hasattr(workspace.settings, key):
                setattr(workspace.settings, key, value)
        
        workspace.updated_at = datetime.utcnow()
        return True
    
    def get_activity_feed(
        self,
        workspace_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get workspace activity feed"""
        workspace = self.workspaces.get(workspace_id)
        if not workspace:
            return []
            
        return workspace.activities[:limit]
