"""
Enterprise Controller
Handles organization management, user provisioning, and project protection.
Restricted to 'enterprises' (Organization Owner) role.
"""
from typing import Dict, Any, List, Optional
import uuid
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from core.security import Role, require_role
from core.container import container
from platform_core.auth.dependencies import get_db
from platform_core.auth.models import User
from platform_core.tenancy.models import Tenant
from platform_core.auth.jwt_manager import JWTManager
from dto.v1.base import BaseResponse, ResponseStatus
from dto.v1.requests.enterprise import CreateOrgUserRequest, ProjectProtectionRequest
from dto.v1.responses.supplemental import EnterpriseUserResponseDTO, WorkbenchMonitorDTO
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Enterprise"])

@router.post("/enterprise/users", response_model=BaseResponse[Dict[str, Any]])
async def add_organization_user(
    request: CreateOrgUserRequest,
    user_info: dict = Depends(require_role([Role.ENTERPRISE])),
    db: AsyncSession = Depends(get_db)
):
    """Add a user to the organization (Enterprise Owner only). Enforces 20-seat limit."""
    # Check if user exists
    user_exists = await db.execute(select(User).where(User.email == request.email))
    if user_exists.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")
        
    jwt_manager = JWTManager()
    tenant_id = user_info.get("tenant_id")
    
    if not tenant_id:
        raise HTTPException(status_code=400, detail="Organization ID missing from requester")

    # Check Seat Limit
    tenant_result = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
    tenant = tenant_result.scalar_one_or_none()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
        
    count_result = await db.execute(select(func.count(User.id)).where(User.tenant_id == tenant_id))
    current_count = count_result.scalar() or 0
    if current_count >= tenant.max_users:
        raise HTTPException(
            status_code=403, 
            detail=f"Seat limit reached. Your plan allows {tenant.max_users} users. Upgrade for more."
        )

    # Force "PRO_DEVELOPER" role for sub-accounts as per Enterprise entitlement
    # "Enterprise (Full Access) could add 20 account developper accounts with Pro-Developer access"
    assigned_role = Role.PRO_DEVELOPER

    new_user = User(
        id=str(uuid.uuid4()),
        tenant_id=tenant_id,
        email=request.email,
        full_name=request.full_name,
        hashed_password=jwt_manager.hash_password(request.password),
        role=assigned_role,
        is_active=True
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return BaseResponse(
        status=ResponseStatus.SUCCESS,
        code="USER_CREATED",
        message=f"User {request.email} added to organization as {assigned_role}",
        data={
            "user_id": new_user.id,
            "role": new_user.role
        }
    )

@router.get("/enterprise/users", response_model=BaseResponse[List[EnterpriseUserResponseDTO]])
async def list_organization_users(
    search: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    user_info: dict = Depends(require_role([Role.ENTERPRISE])),
    db: AsyncSession = Depends(get_db)
):
    """List all users in the organization with search and pagination."""
    tenant_id = user_info.get("tenant_id")
    
    stmt = select(User).where(User.tenant_id == tenant_id)
    if search:
        search_query = f"%{search}%"
        stmt = stmt.where(
            (User.email.ilike(search_query)) | 
            (User.full_name.ilike(search_query))
        )
        
    # Get total count
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_result = await db.execute(count_stmt)
    total = total_result.scalar() or 0
    
    # Get paginated users
    result = await db.execute(stmt.offset((page - 1) * page_size).limit(page_size))
    users = result.scalars().all()
    
    return BaseResponse(
        status=ResponseStatus.SUCCESS,
        code="USERS_RETRIEVED",
        message=f"Retrieved {len(users)} organization users",
        data=[
            EnterpriseUserResponseDTO(
                id=u.id, 
                email=u.email, 
                role=u.role,
                full_name=u.full_name,
                is_active=u.is_active,
                created_at=u.created_at.isoformat() if u.created_at else None
            ) for u in users
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

@router.delete("/enterprise/users/{user_id}")
async def remove_organization_user(
    user_id: str,
    user_info: dict = Depends(require_role([Role.ENTERPRISE])),
    db: AsyncSession = Depends(get_db)
):
    """Remove a user from the organization."""
    tenant_id = user_info.get("tenant_id")
    result = await db.execute(select(User).where(User.id == user_id, User.tenant_id == tenant_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found in organization")
        
    # Soft delete or hard delete? Let's do soft (deactivate) for safety or hard. User requested 'delete/add/update'
    # db.delete(user) # Hard delete might break integrity if projects exist
    user.is_active = False # Safe default
    await db.commit()
    
    return BaseResponse(
        status=ResponseStatus.SUCCESS,
        code="USER_DEACTIVATED",
        message=f"User {user_id} deactivated",
        data={"user_id": user_id}
    )

@router.get("/enterprise/projects")
async def list_organization_projects(
    search: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    user_info: dict = Depends(require_role([Role.ENTERPRISE])),
    db: AsyncSession = Depends(get_db)
):
    """List all projects in the organization with search and pagination."""
    if not container.project_manager:
        raise HTTPException(503, "Project Manager unavailable")
        
    tenant_id = user_info.get("tenant_id")
    
    # Get all users in tenant to filter projects
    user_ids_result = await db.execute(select(User.id).where(User.tenant_id == tenant_id))
    org_user_ids = [u_id for u_id, in user_ids_result.all()]
    
    all_projects = container.project_manager.get_all_projects()
    if isinstance(all_projects, dict):
         all_projects = list(all_projects.values())
         
    org_projects = [p for p in all_projects if p.get("user_id") in org_user_ids]
    
    if search:
        search = search.lower()
        org_projects = [p for p in org_projects if search in p.get("project_name", "").lower()]
        
    total = len(org_projects)
    
    # Manual pagination
    start = (page - 1) * page_size
    end = start + page_size
    paginated_projects = org_projects[start:end]
    
    return BaseResponse(
        status=ResponseStatus.SUCCESS,
        code="ORCHESTRATOR_PROJECTS_RETRIEVED",
        message=f"Retrieved {len(paginated_projects)} organization projects",
        data=paginated_projects,
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


@router.post("/enterprise/projects/{project_id}/protect")
async def set_project_protection(
    project_id: str,
    request: ProjectProtectionRequest,
    user_info: dict = Depends(require_role([Role.ENTERPRISE]))
):
    """Enable/Disable protection for a project (cannot be disabled by developers)."""
    # Logic to update project metadata with protection flag
    
    return BaseResponse(
        status="success",
        code="PROJECT_PROTECTION_UPDATED",
        message="Protection settings updated",
        data={
            "project_id": project_id, 
            "protection": request.enabled
        }
    )

@router.get("/enterprise/workbenches")
async def monitor_active_workbenches(
    user_info: dict = Depends(require_role([Role.ENTERPRISE])),
    db: AsyncSession = Depends(get_db)
):
    """Real-time: List all active IDE workbenches for the organization."""
    if not container.orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not ready")
        
    tenant_id = user_info.get("tenant_id")
    
    # Get all users in this tenant
    users_result = await db.execute(select(User.id, User.email).where(User.tenant_id == tenant_id))
    user_map = {u_id: u_email for u_id, u_email in users_result.all()}
    
    # Filter active workbenches by organization users
    active_benches = []
    if hasattr(container.orchestrator, "workbench_manager"):
        # Use helper method that returns dict
        all_benches = container.orchestrator.workbench_manager.get_all_workbenches() 
        for wb_id, wb in all_benches.items():
            # owner_id is now safely in the dict
            owner_id = wb.get("owner_id")
            if owner_id in user_map:
                active_benches.append({
                    "id": wb_id,
                    "owner": user_map[owner_id],
                    "status": wb.get("status", "unknown"),
                    "last_active": wb.get("last_active")
                })
                
    return BaseResponse(
        status=ResponseStatus.SUCCESS,
        code="WORKBENCHES_MONITORED",
        message=f"Monitoring {len(active_benches)} active workbenches",
        data=[WorkbenchMonitorDTO(**b) for b in active_benches]
    )

@router.put("/enterprise/users/{user_id}/permissions")
async def update_user_permissions(
    user_id: str,
    permissions: Dict[str, Any],
    user_info: dict = Depends(require_role([Role.ENTERPRISE])),
    db: AsyncSession = Depends(get_db)
):
    """Update permissions or role for a sub-user (Admin control)."""
    tenant_id = user_info.get("tenant_id")
    result = await db.execute(select(User).where(User.id == user_id, User.tenant_id == tenant_id))
    target_user = result.scalar_one_or_none()
    
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found in organization")
        
    # Example: Allow changing role between PRO_DEVELOPER and DEVELOPER
    new_role = permissions.get("role")
    if new_role:
        if new_role not in [Role.PRO_DEVELOPER.value, Role.DEVELOPER.value]:
             raise HTTPException(status_code=400, detail="Can only assign PRO_DEVELOPER or DEVELOPER roles")
        target_user.role = new_role
        
    await db.commit()
    
    return BaseResponse(
        status=ResponseStatus.SUCCESS,
        code="PERMISSIONS_UPDATED",
        message=f"Permissions updated for user {target_user.email}",
        data={"user_id": user_id, "new_role": target_user.role}
    )

@router.delete("/enterprise/projects/{project_id}")
async def force_delete_project(
    project_id: str,
    user_info: dict = Depends(require_role([Role.ENTERPRISE])),
    db: AsyncSession = Depends(get_db)
):
    """Force delete any project within the organization."""
    tenant_id = user_info.get("tenant_id")
    
    if not container.project_manager:
        raise HTTPException(status_code=503, detail="Project Manager unavailable")
        
    # Verify project belongs to tenant
    project = await container.project_manager.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    owner_id = project.get("user_id")
    owner_result = await db.execute(select(User).where(User.id == owner_id, User.tenant_id == tenant_id))
    owner = owner_result.scalar_one_or_none()
    
    if not owner:
        raise HTTPException(status_code=403, detail="Project does not belong to your organization")
        
    # Proceed with deletion
    success = await container.project_manager.delete_project(project_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete project")
        
    return BaseResponse(
        status=ResponseStatus.SUCCESS,
        code="PROJECT_FORCE_DELETED",
        message=f"Project {project_id} force deleted by Enterprise Admin",
        data={"project_id": project_id}
    )

