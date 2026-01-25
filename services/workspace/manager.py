import uuid
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
from sqlalchemy import select, delete, desc
from platform_core.database import SessionLocal
from models.workspace import (
    Workspace as WorkspaceModel, 
    WorkspaceMember as MemberModel, 
    WorkspaceActivity as ActivityModel
)

logger = logging.getLogger(__name__)


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
    """Workspace manager with Database Persistence"""
    
    def __init__(self):
        # We no longer need in-memory storage for persistence
        pass
    
    def create_workspace(
        self,
        name: str,
        owner_id: str,
        owner_name: str
    ) -> Dict[str, Any]:
        """Create new workspace and persist to DB"""
        workspace_id = str(uuid.uuid4())
        
        with SessionLocal() as db:
            # Create Workspace
            db_workspace = WorkspaceModel(
                id=workspace_id,
                name=name,
                owner_id=owner_id
            )
            db.add(db_workspace)
            
            # Add Owner as first member
            db_member = MemberModel(
                workspace_id=workspace_id,
                user_id=owner_id,
                username=owner_name,
                role=WorkspaceRole.ADMIN.value # Owner is Admin
            )
            db.add(db_member)
            
            # Log Activity
            db_activity = ActivityModel(
                workspace_id=workspace_id,
                user_id=owner_id,
                activity_type="workspace_created",
                message=f"Workspace '{name}' created by {owner_name}"
            )
            db.add(db_activity)
            
            db.commit()
            return {
                "id": workspace_id,
                "name": name,
                "owner_id": owner_id,
                "status": "created"
            }
    
    def get_workspace(self, workspace_id: str) -> Optional[Dict[str, Any]]:
        """Get workspace by ID from DB"""
        with SessionLocal() as db:
            workspace = db.query(WorkspaceModel).filter(WorkspaceModel.id == workspace_id).first()
            if not workspace:
                return None
                
            # Convert to dict for API compatibility
            return {
                "id": workspace.id,
                "name": workspace.name,
                "owner_id": workspace.owner_id,
                "settings": workspace.settings,
                "created_at": workspace.created_at.isoformat(),
                "members_count": db.query(MemberModel).filter(MemberModel.workspace_id == workspace_id).count()
            }
    
    def delete_workspace(self, workspace_id: str, user_id: str) -> bool:
        """Delete workspace from DB (only owner can delete)"""
        with SessionLocal() as db:
            workspace = db.query(WorkspaceModel).filter(
                WorkspaceModel.id == workspace_id,
                WorkspaceModel.owner_id == user_id
            ).first()
            
            if not workspace:
                return False
            
            db.delete(workspace)
            db.commit()
            return True
    
    def list_user_workspaces(
        self, 
        user_id: str,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """List workspaces for user from DB with pagination"""
        with SessionLocal() as db:
            # Join with members table to find workspaces where user is a member
            query = db.query(WorkspaceModel).join(MemberModel).filter(MemberModel.user_id == user_id)
            
            total = query.count()
            results = query.offset((page - 1) * page_size).limit(page_size).all()
            
            workspaces = []
            for w in results:
                workspaces.append({
                    "id": w.id,
                    "name": w.name,
                    "owner_id": w.owner_id,
                    "created_at": w.created_at.isoformat()
                })
            
            return {
                "workspaces": workspaces,
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
        """Invite member to workspace in DB"""
        with SessionLocal() as db:
            # Check if inviter has permission (must be admin or enterprise in this workspace)
            inviter = db.query(MemberModel).filter(
                MemberModel.workspace_id == workspace_id,
                MemberModel.user_id == inviter_id
            ).first()
            
            if not inviter or inviter.role not in [WorkspaceRole.ADMIN.value, WorkspaceRole.ENTERPRISE.value]:
                return False
            
            # Check if already member
            existing = db.query(MemberModel).filter(
                MemberModel.workspace_id == workspace_id,
                MemberModel.user_id == user_id
            ).first()
            
            if existing:
                return False
            
            # Add member
            db_member = MemberModel(
                workspace_id=workspace_id,
                user_id=user_id,
                username=username,
                role=role.value
            )
            db.add(db_member)
            
            # Log Activity
            db_activity = ActivityModel(
                workspace_id=workspace_id,
                user_id=inviter_id,
                activity_type="member_added",
                message=f"User {username} added as {role.value}"
            )
            db.add(db_activity)
            
            db.commit()
            return True
    
    def remove_member(
        self,
        workspace_id: str,
        remover_id: str,
        user_id: str
    ) -> bool:
        """Remove member from workspace in DB"""
        with SessionLocal() as db:
            # Check permission
            remover = db.query(MemberModel).filter(
                MemberModel.workspace_id == workspace_id,
                MemberModel.user_id == remover_id
            ).first()
            
            if not remover or remover.role not in [WorkspaceRole.ADMIN.value, WorkspaceRole.ENTERPRISE.value]:
                return False
            
            # Cannot remove owner
            workspace = db.query(WorkspaceModel).get(workspace_id)
            if not workspace or workspace.owner_id == user_id:
                return False
            
            member = db.query(MemberModel).filter(
                MemberModel.workspace_id == workspace_id,
                MemberModel.user_id == user_id
            ).first()
            
            if member:
                db.delete(member)
                
                # Log Activity
                db_activity = ActivityModel(
                    workspace_id=workspace_id,
                    user_id=remover_id,
                    activity_type="member_removed",
                    message=f"User {user_id} removed from workspace"
                )
                db.add(db_activity)
                
                db.commit()
                return True
            return False
    
    def update_settings(
        self,
        workspace_id: str,
        user_id: str,
        settings: Dict[str, Any]
    ) -> bool:
        """Update workspace settings in DB"""
        with SessionLocal() as db:
            # Check permission (Admin only)
            member = db.query(MemberModel).filter(
                MemberModel.workspace_id == workspace_id,
                MemberModel.user_id == user_id
            ).first()
            
            if not member or member.role != WorkspaceRole.ADMIN.value:
                return False
            
            workspace = db.query(WorkspaceModel).get(workspace_id)
            if not workspace:
                return False
            
            # Update settings (JSON merge)
            current_settings = workspace.settings or {}
            current_settings.update(settings)
            workspace.settings = current_settings
            
            db.commit()
            return True
    
    def get_activity_feed(
        self,
        workspace_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get workspace activity feed from DB"""
        with SessionLocal() as db:
            activities = db.query(ActivityModel).filter(
                ActivityModel.workspace_id == workspace_id
            ).order_by(desc(ActivityModel.timestamp)).limit(limit).all()
            
            return [{
                "id": a.id,
                "type": a.activity_type,
                "message": a.message,
                "user_id": a.user_id,
                "timestamp": a.timestamp.isoformat()
            } for a in activities]
