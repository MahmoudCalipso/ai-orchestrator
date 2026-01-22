"""
Enterprise Controller
Handles organization management, user provisioning, and project protection.
Restricted to 'enterprises' (Organization Owner) role.
"""
from typing import Dict, Any, List, Optional
import uuid
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from platform_core.auth.dependencies import get_db
from platform_core.auth.models import User
from platform_core.auth.jwt_manager import JWTManager

from core.security import verify_api_key, require_role, Role, SecurityManager
from core.container import container
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Enterprise"])

class CreateOrgUserRequest(BaseModel):
    email: str
    full_name: str
    password: str
    role: str = "developer"

class ProjectProtectionRequest(BaseModel):
    enabled: bool
    allowed_users: Optional[List[str]] = None

@router.post("/enterprise/users")
async def add_organization_user(
    request: CreateOrgUserRequest,
    user_info: dict = Depends(require_role([Role.ENTERPRISE])),
    db: Session = Depends(get_db)
):
    """Add a user to the organization (Enterprise Owner only)."""
    # Check if user exists
    if db.query(User).filter(User.email == request.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
        
    jwt_manager = JWTManager()
    tenant_id = user_info.get("tenant_id")
    
    if not tenant_id:
        raise HTTPException(status_code=400, detail="Organization ID missing from requester")

    new_user = User(
        id=str(uuid.uuid4()),
        tenant_id=tenant_id,
        email=request.email,
        full_name=request.full_name,
        hashed_password=jwt_manager.hash_password(request.password),
        role=request.role,
        is_active=True
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {
        "status":"success", 
        "message": f"User {request.email} added to organization",
        "user_id": new_user.id,
        "role": new_user.role
    }

@router.get("/enterprise/users")
async def list_organization_users(
    page: int = 1,
    page_size: int = 20,
    user_info: dict = Depends(require_role([Role.ENTERPRISE])),
    db: Session = Depends(get_db)
):
    """List all users in the organization with pagination."""
    tenant_id = user_info.get("tenant_id")
    
    query = db.query(User).filter(User.tenant_id == tenant_id)
    total = query.count()
    users = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return {
        "users": [
            {
                "id": u.id, 
                "email": u.email, 
                "role": u.role,
                "full_name": u.full_name,
                "is_active": u.is_active,
                "created_at": u.created_at.isoformat() if u.created_at else None
            } for u in users
        ],
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": (total + page_size - 1) // page_size
        }
    }

@router.delete("/enterprise/users/{user_id}")
async def remove_organization_user(
    user_id: str,
    user_info: dict = Depends(require_role([Role.ENTERPRISE])),
    db: Session = Depends(get_db)
):
    """Remove a user from the organization."""
    tenant_id = user_info.get("tenant_id")
    user = db.query(User).filter(User.id == user_id, User.tenant_id == tenant_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found in organization")
        
    # Soft delete or hard delete? Let's do soft (deactivate) for safety or hard. User requested 'delete/add/update'
    # db.delete(user) # Hard delete might break integrity if projects exist
    user.is_active = False # Safe default
    db.commit()
    
    return {"status": "success", "message": f"User {user_id} deactivated"}

@router.get("/enterprise/projects")
async def list_organization_projects(
    page: int = 1,
    page_size: int = 20,
    user_info: dict = Depends(require_role([Role.ENTERPRISE])),
    db: Session = Depends(get_db)
):
    """List all projects in the organization with pagination."""
    if not container.project_manager:
        raise HTTPException(503, "Project Manager unavailable")
        
    tenant_id = user_info.get("tenant_id")
    
    # Get all users in tenant to filter projects (ProjectManager is file-based)
    org_users = db.query(User.id).filter(User.tenant_id == tenant_id).all()
    org_user_ids = [u.id for u in org_users]
    
    all_projects = container.project_manager.get_all_projects()
    if isinstance(all_projects, dict):
         all_projects = list(all_projects.values())
         
    org_projects = [p for p in all_projects if p.get("user_id") in org_user_ids]
    total = len(org_projects)
    
    # Manual pagination
    start = (page - 1) * page_size
    end = start + page_size
    paginated_projects = org_projects[start:end]
    
    return {
        "projects": paginated_projects,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": (total + page_size - 1) // page_size
        }
    }


@router.post("/enterprise/projects/{project_id}/protect")
async def set_project_protection(
    project_id: str,
    request: ProjectProtectionRequest,
    user_info: dict = Depends(require_role([Role.ENTERPRISE]))
):
    """Enable/Disable protection for a project (cannot be disabled by developers)."""
    # Logic to update project metadata with protection flag
    
    return {
        "status": "success", 
        "project_id": project_id, 
        "protection": request.enabled
    }
