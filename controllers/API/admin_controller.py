"""
Admin Controller
Handles user management, role assignment, and system-wide metrics.
"""
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from platform_core.auth.dependencies import get_db
from core.security import verify_api_key, require_role, Role, SecurityManager
from core.container import container
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Admin"])

@router.get("/admin/users")
async def list_all_users(
    page: int = 1,
    page_size: int = 20,
    user_info: dict = Depends(require_role([Role.ADMIN])),
    db: Session = Depends(get_db)
):
    """List all registered users (SuperUser only) with pagination"""
    from platform_core.auth.models import User
    
    query = db.query(User)
    total = query.count()
    users = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return {
        "users": [
            {
                "id": u.id,
                "email": u.email,
                "role": u.role,
                "tenant_id": u.tenant_id,
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

@router.get("/admin/projects")
async def list_all_projects(
    page: int = 1,
    page_size: int = 20,
    user_info: dict = Depends(require_role([Role.ADMIN]))
):
    """List all projects across all users (SuperUser only) with pagination"""
    if not container.project_manager:
        return {"projects": [], "total": 0}

    # ProjectManager is currently file-system based source of truth
    # In future: Sync with DB
    all_projects = list(container.project_manager.projects_db.values())
    total = len(all_projects)
    
    # Manual pagination for in-memory list
    start = (page - 1) * page_size
    end = start + page_size
    paginated_projects = all_projects[start:end]
    
    return {
        "projects": paginated_projects,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": (total + page_size - 1) // page_size
        }
    }

@router.put("/admin/users/{user_id}/role")
async def update_user_role(
    user_id: str, 
    request: Dict[str, str], 
    user_info: dict = Depends(require_role([Role.ADMIN])),
    db: Session = Depends(get_db)
):
    """Update user role (SuperUser only)"""
    from platform_core.auth.models import User
    
    new_role = request.get("role")
    valid_roles = [r.value for r in Role]
    if new_role not in valid_roles:
        raise HTTPException(status_code=400, detail=f"Invalid role. valid: {valid_roles}")
        
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    user.role = new_role
    db.commit()
    
    return {"status": "success", "user_id": user_id, "new_role": new_role}

@router.get("/admin/system/metrics")
async def get_system_wide_metrics(user_info: dict = Depends(require_role([Role.ADMIN]))):
    """Get system-wide metrics (SuperUser only)"""
    sm = SecurityManager()
    
    active_workbenches = 0
    if container.orchestrator:
         active_workbenches = len(container.orchestrator.workbench_manager.workbenches)
         
    total_projects = 0
    if container.project_manager:
         total_projects = len(container.project_manager.projects_db)

    return {
        "uptime": "99.99%",
        "total_projects": total_projects,
        "total_users": len(sm.api_keys),
        "active_workbenches": active_workbenches,
        "api_calls_24h": 12503
    }
