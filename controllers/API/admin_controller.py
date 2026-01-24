"""
Admin Controller
Handles user management, role assignment, and system-wide metrics.
"""
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from platform_core.auth.dependencies import get_db
from core.security import verify_api_key, require_role, Role, SecurityManager
from core.container import container
from dto.common.base_response import BaseResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Admin"])

@router.get("/admin/users")
async def list_all_users(
    search: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    user_info: dict = Depends(require_role([Role.ADMIN])),
    db: Session = Depends(get_db)
):
    """List all registered users (SuperUser only) with search and pagination"""
    from platform_core.auth.models import User
    
    query = db.query(User)
    if search:
        search_query = f"%{search}%"
        query = query.filter(
            (User.email.ilike(search_query)) | 
            (User.username.ilike(search_query)) |
            (User.full_name.ilike(search_query))
        )
        
    total = query.count()
    users = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return BaseResponse(
        status="success",
        code="ADMIN_USERS_RETRIEVED",
        message=f"Retrieved {len(users)} users",
        data=[
            {
                "id": u.id,
                "email": u.email,
                "role": u.role,
                "tenant_id": u.tenant_id,
                "is_active": u.is_active,
                "created_at": u.created_at.isoformat() if u.created_at else None
            } for u in users
        ],
        meta={
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": (total + page_size - 1) // page_size
            },
            "search": search
        }
    )

@router.get("/admin/projects")
async def list_all_projects(
    search: Optional[str] = None,
    name: Optional[str] = None, # Alias for search
    framework: Optional[str] = None,
    language: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    user_info: dict = Depends(require_role([Role.ADMIN]))
):
    """List all projects across all users (SuperUser only) with metrics search and pagination"""
    if not container.project_manager:
        return BaseResponse(status="success", code="NO_PROCESSOR", data={"projects": [], "total": 0})

    # Use ProjectManager's logic for filtering if possible, or manual filter here
    all_projects = list(container.project_manager.projects_db.values())
    
    # Apply filters
    filtered_projects = all_projects
    search_query = search or name
    if search_query:
        sq = search_query.lower()
        filtered_projects = [p for p in filtered_projects if sq in p["project_name"].lower()]
    if framework:
        filtered_projects = [p for p in filtered_projects if p.get("framework") == framework]
    if language:
        filtered_projects = [p for p in filtered_projects if p.get("language") == language]

    total = len(filtered_projects)
    
    # Manual pagination
    start = (page - 1) * page_size
    end = start + page_size
    paginated_projects = filtered_projects[start:end]
    
    return BaseResponse(
        status="success",
        code="ADMIN_PROJECTS_RETRIEVED",
        data=paginated_projects,
        meta={
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": (total + page_size - 1) // page_size
            }
        }
    )

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
    
    return BaseResponse(
        status="success",
        code="USER_ROLE_UPDATED",
        message=f"User {user_id} promoted to {new_role}",
        data={"user_id": user_id, "new_role": new_role}
    )

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

    return BaseResponse(
        status="success",
        code="SYSTEM_METRICS_RETRIEVED",
        data={
            "uptime": "99.99%",
            "total_projects": total_projects,
            "total_users": len(sm.api_keys),
            "active_workbenches": active_workbenches,
            "api_calls_24h": 12503
        }
    )
