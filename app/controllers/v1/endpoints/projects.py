"""
Project Management API Controller (Unified V2)
Handles project lifecycle, git sync, AI updates, workflows, and RBAC.
Fully Async implementation
"""
from typing import Dict, Any, List, Optional
import logging
import os
from fastapi import APIRouter, HTTPException, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

# Core & Middleware
from ....core.database import get_db
from core.security import verify_api_key, SecurityManager, Role
from core.container import container
from ....middleware.auth import require_auth

# Models & DTOs
from platform_core.auth.models import User
from dto.v1.base import BaseResponse, ResponseStatus
from dto.v1.requests.project import ProjectUpdateRequest, ProjectSearchRequest
from dto.v1.responses.project import ProjectResponseDTO, ProjectListResponseDTO
from dto.v1.schemas.enums import ProjectStatus, BuildStatus, RunStatus
from core.security import get_security_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/projects", tags=["Project Lifecycle"])

# --- Helper ---
async def check_access(
    user_info: dict, 
    target_user_id: Optional[str] = None, 
    db: AsyncSession = None,
    project_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Verify if user has access to target resources via DB check (Async).
    
    Returns a dict with access metadata:
    - has_access: bool
    - access_level: 'own' | 'tenant' | 'global'  
    - visible_user_ids: List[str] - List of user IDs the caller can see projects for
    """
    role = user_info.get("role")
    uid = user_info.get("user_id")
    tenant_id = user_info.get("tenant_id")
    
    # Super Admin - Global access to all projects across all enterprises
    if role == Role.ADMIN.value:
        return {
            "has_access": True,
            "access_level": "global",
            "visible_user_ids": None  # None means all users (no filter)
        }
    
    # Enterprise Admin - Access to all projects within their tenant
    if role == Role.ENTERPRISE.value:
        # If checking access to a specific target user
        if target_user_id and db:
            if uid == target_user_id:
                return {
                    "has_access": True,
                    "access_level": "own",
                    "visible_user_ids": [uid]
                }
            # Check if target user belongs to same tenant
            result = await db.execute(select(User).where(User.id == target_user_id))
            target_user = result.scalar_one_or_none()
            
            if target_user and target_user.tenant_id == tenant_id:
                return {
                    "has_access": True,
                    "access_level": "tenant",
                    "visible_user_ids": None  # Will be populated from tenant users
                }
            raise HTTPException(403, "Access denied to user outside organization")
        
        # Enterprise admin can see all users in their tenant
        return {
            "has_access": True,
            "access_level": "tenant",
            "visible_user_ids": None,  # Will be populated from tenant users
            "tenant_id": tenant_id
        }

    # Developer - Only access to their own projects
    if role == Role.DEVELOPER.value or role == Role.PRO_DEVELOPER.value:
        if target_user_id and uid != target_user_id:
            raise HTTPException(403, "Developers can only access their own projects")
        return {
            "has_access": True,
            "access_level": "own",
            "visible_user_ids": [uid]
        }
    
    return {"has_access": False, "access_level": None, "visible_user_ids": []}


async def get_visible_user_ids(user_info: dict, db: AsyncSession) -> Optional[List[str]]:
    """
    Get list of user IDs that the current user can view projects for.
    Returns None if user can see all users (Super Admin).
    Returns list of user IDs for Enterprise (tenant users) or Developer (self only).
    """
    role = user_info.get("role")
    uid = user_info.get("user_id")
    tenant_id = user_info.get("tenant_id")
    
    # Super Admin sees all
    if role == Role.ADMIN.value:
        return None
    
    # Enterprise Admin sees all users in their tenant
    if role == Role.ENTERPRISE.value and tenant_id:
        result = await db.execute(
            select(User.id).where(User.tenant_id == tenant_id)
        )
        return [u_id for u_id, in result.all()]
    
    # Developer/Pro Developer sees only their own projects
    return [uid]

# --- Endpoints ---

@router.get("/", response_model=BaseResponse[ProjectListResponseDTO])
async def list_projects(
    user_id: Optional[str] = None,
    search: Optional[str] = None,
    status: Optional[str] = None,
    name: Optional[str] = None,
    framework: Optional[str] = None,
    language: Optional[str] = None,
    solution_id: Optional[str] = None,
    tenant_id: Optional[str] = None,  # Super Admin can filter by tenant
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1),
    api_key: str = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db)
):
    """
    List projects with RBAC-enforced visibility:
    - Super Admin (Role.ADMIN): Can view all projects across all tenants. Can filter by tenant_id.
    - Enterprise Admin (Role.ENTERPRISE): Can view all projects within their own tenant.
    - Developer/Pro Developer: Can only view their own projects.
    """
    sm = get_security_manager()
    user_info = await sm.get_user_info(api_key, db)
    
    if not user_info:
        raise HTTPException(401, "User not found")
    
    role = user_info.get("role")
    current_user_id = user_info.get("user_id")
    current_tenant_id = user_info.get("tenant_id")
    
    if not container.project_manager:
        raise HTTPException(status_code=503, detail="Project Manager not ready")
    
    # Determine which user IDs the current user can view projects for
    visible_user_ids = await get_visible_user_ids(user_info, db)
    
    # If a specific user_id is requested, verify access
    if user_id:
        if visible_user_ids is not None and user_id not in visible_user_ids:
            raise HTTPException(403, "Access denied to view projects for this user")
        target_user_ids = [user_id]
    else:
        # Use all visible user IDs (or None for Super Admin to get all)
        target_user_ids = visible_user_ids
    
    # Super Admin can filter by tenant_id
    target_tenant_id = None
    if role == Role.ADMIN.value and tenant_id:
        target_tenant_id = tenant_id
    elif role == Role.ENTERPRISE.value:
        target_tenant_id = current_tenant_id
        
    filters = {
        "name": search or name,
        "framework": framework,
        "language": language,
        "solution_id": solution_id
    }
    
    # Call the updated method with user filtering
    result = await container.project_manager.get_projects(
        user_ids=target_user_ids,
        tenant_id=target_tenant_id,
        status=status,
        page=page,
        page_size=page_size,
        filters=filters
    )
    
    projects = [ProjectResponseDTO.model_validate(p) for p in result["projects"]]
    
    # Build appropriate message based on access level
    if role == Role.ADMIN.value:
        message = f"Retrieved {len(projects)} projects across all tenants"
    elif role == Role.ENTERPRISE.value:
        message = f"Retrieved {len(projects)} projects for organization"
    else:
        message = f"Retrieved {len(projects)} projects for user {current_user_id}"
    
    return BaseResponse(
        status=ResponseStatus.SUCCESS,
        code="PROJECTS_RETRIEVED",
        message=message,
        data=ProjectListResponseDTO(
            projects=projects,
            total=result["total"],
            page=result["page"],
            page_size=result["page_size"]
        ),
        meta={
            "filters": filters,
            "access_level": role,
            "tenant_filter": target_tenant_id
        }
    )

@router.get("/{project_id}", response_model=BaseResponse[ProjectResponseDTO])
async def get_project(
    project_id: str, 
    api_key: str = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db)
):
    """
    Get project details with RBAC enforcement:
    - Super Admin: Can view any project
    - Enterprise Admin: Can view any project within their tenant
    - Developer: Can only view their own projects
    """
    sm = get_security_manager()
    user_info = await sm.get_user_info(api_key, db)
    if not user_info:
        raise HTTPException(401, "Authentication required")
    
    if not container.project_manager:
        raise HTTPException(status_code=503, detail="Project Manager not ready")
        
    project = await container.project_manager.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check access to the project owner's data
    access_info = await check_access(user_info, project.get("user_id"), db)
    if not access_info["has_access"]:
        raise HTTPException(403, "Access denied to this project")
        
    return BaseResponse(
        status=ResponseStatus.SUCCESS,
        code="PROJECT_DETAILS_RETRIEVED",
        message="Project details retrieved successfully",
        data=ProjectResponseDTO.model_validate(project)
    )



@router.delete("/{project_id}", response_model=BaseResponse[Dict[str, str]])
async def delete_project(
    project_id: str, 
    api_key: str = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a user project with RBAC enforcement:
    - Super Admin: Can delete any project
    - Enterprise Admin: Can delete any project within their tenant
    - Developer: Can only delete their own projects
    """
    sm = get_security_manager()
    user_info = await sm.get_user_info(api_key, db)
    if not user_info:
        raise HTTPException(401, "Authentication required")
    
    if not container.project_manager:
        raise HTTPException(status_code=503, detail="Project Manager not ready")
        
    project = await container.project_manager.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check access - only owners, enterprise admins, or super admins can delete
    access_info = await check_access(user_info, project.get("user_id"), db)
    if not access_info["has_access"]:
        raise HTTPException(403, "Access denied to delete this project")
    
    # Developers can only delete their own projects
    role = user_info.get("role")
    if role in [Role.DEVELOPER.value, Role.PRO_DEVELOPER.value]:
        if user_info.get("user_id") != project.get("user_id"):
            raise HTTPException(403, "Developers can only delete their own projects")
    
    success = await container.project_manager.delete_project(project_id, project.get("user_id"))
    if not success:
        raise HTTPException(status_code=500, detail="Delete failed")
        
    return BaseResponse(
        status=ResponseStatus.SUCCESS,
        code="PROJECT_DELETED",
        message="Project deleted successfully",
        data={"project_id": project_id}
    )

# --- Action Endpoints ---

@router.post("/{project_id}/open", response_model=BaseResponse[Dict[str, Any]])
async def open_user_project(
    project_id: str, 
    request: Dict[str, Any], 
    api_key: str = Depends(verify_api_key), 
    db: AsyncSession = Depends(get_db)
):
    """
    Open a project: Clone from Git and load in IDE.
    RBAC: Super Admin and Enterprise Admin can open any project in their scope.
    Developers can only open their own projects.
    """
    if not container.project_manager or not container.git_sync_service or not container.editor_service:
         raise HTTPException(status_code=503, detail="Project services not ready")

    project = await container.project_manager.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check access
    sm = get_security_manager()
    user_info = await sm.get_user_info(api_key, db)
    access_info = await check_access(user_info, project.get("user_id"), db)
    if not access_info["has_access"]:
        raise HTTPException(403, "Access denied to open this project")
    
    # Clone if not already cloned
    local_path = project["local_path"]
    if not os.path.exists(os.path.join(local_path, ".git")):
        res = await container.git_sync_service.clone_repository(
            repo_url=project["git_repo_url"],
            local_path=local_path,
            branch=project.get("git_branch", "main"),
            credentials=request.get("git_credentials")
        )
        if not res["success"]:
            raise HTTPException(status_code=500, detail=res["message"])
    
    await container.project_manager.update_last_opened(project_id)
    
    # Create IDE workspace
    workspace = await container.editor_service.create_workspace(project["project_name"], local_path)
    
    return BaseResponse(
        status=ResponseStatus.SUCCESS,
        code="PROJECT_OPENED",
        data={
            "workspace_id": workspace.id,
            "project": ProjectResponseDTO.model_validate(project)
        }
    )

@router.post("/{project_id}/sync")
async def sync_user_project(
    project_id: str, 
    api_key: str = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db)
):
    """
    Sync project with Git remote (pull).
    RBAC: Super Admin and Enterprise Admin can sync any project in their scope.
    Developers can only sync their own projects.
    """
    if not container.project_manager or not container.git_sync_service:
        raise HTTPException(status_code=503, detail="Project services not ready")
        
    project = await container.project_manager.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check access
    sm = get_security_manager()
    user_info = await sm.get_user_info(api_key, db)
    access_info = await check_access(user_info, project.get("user_id"), db)
    if not access_info["has_access"]:
        raise HTTPException(403, "Access denied to sync this project")
    
    res = await container.git_sync_service.pull_latest(project["local_path"])
    if not res["success"]:
        raise HTTPException(status_code=500, detail=res["error"])
        
    return BaseResponse(
        status=ResponseStatus.SUCCESS,
        code="PROJECT_VERSION_CHECKED",
        data={"commit": res["commit_hash"]}
    )

@router.post("/{project_id}/ai-update")
async def ai_update_project(
    project_id: str, 
    request: Dict[str, Any], 
    api_key: str = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db)
):
    """
    Apply AI updates via chat prompt.
    RBAC: Super Admin and Enterprise Admin can update any project in their scope.
    Developers can only update their own projects.
    """
    if not container.project_manager or not container.ai_update_service:
        raise HTTPException(status_code=503, detail="Project services not ready")
        
    project = await container.project_manager.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check access
    sm = get_security_manager()
    user_info = await sm.get_user_info(api_key, db)
    access_info = await check_access(user_info, project.get("user_id"), db)
    if not access_info["has_access"]:
        raise HTTPException(403, "Access denied to update this project")
    
    res = await container.ai_update_service.apply_chat_update(
        project_id=project_id,
        local_path=project["local_path"],
        prompt=request.get("prompt"),
        context=request.get("context")
    )
    
    if not res["success"]:
        raise HTTPException(status_code=500, detail=res["error"])
        
    return BaseResponse(
        status=ResponseStatus.SUCCESS,
        code="AI_UPDATE_APPLIED",
        data=res
    )

@router.post("/{project_id}/workflow", response_model=BaseResponse[Dict[str, Any]])
async def execute_project_workflow(
    project_id: str, 
    request: Dict[str, Any], 
    api_key: str = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db)
):
    """
    Execute a complete project workflow.
    RBAC: Super Admin and Enterprise Admin can execute workflows on any project in their scope.
    Developers can only execute workflows on their own projects.
    """
    if not container.project_manager or not container.workflow_engine:
        raise HTTPException(status_code=503, detail="Workflow engine not ready")
        
    project = await container.project_manager.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check access
    sm = get_security_manager()
    user_info = await sm.get_user_info(api_key, db)
    access_info = await check_access(user_info, project.get("user_id"), db)
    if not access_info["has_access"]:
        raise HTTPException(403, "Access denied to execute workflow on this project")
    
    workflow_id = await container.workflow_engine.execute_workflow(
        project_id=project_id,
        user_id=project["user_id"],
        steps=request.get("steps", ["sync", "update", "push", "build", "run"]),
        config=request
    )
    
    return BaseResponse(
        status=ResponseStatus.SUCCESS,
        code="WORKFLOW_STARTED",
        message="Workflow execution initialized",
        data={
            "workflow_id": workflow_id,
            "message": f"Workflow {workflow_id} started in background"
        }
    )

@router.post("/{project_id}/build")
async def build_project(
    project_id: str,
    request: Dict[str, Any] = None,
    api_key: str = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db)
):
    """
    Build a project.
    RBAC: Super Admin and Enterprise Admin can build any project in their scope.
    Developers can only build their own projects.
    """
    if not container.project_manager or not container.build_service:
        raise HTTPException(status_code=503, detail="Services not ready")
        
    project = await container.project_manager.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check access
    sm = get_security_manager()
    user_info = await sm.get_user_info(api_key, db)
    access_info = await check_access(user_info, project.get("user_id"), db)
    if not access_info["has_access"]:
        raise HTTPException(403, "Access denied to build this project")
        
    try:
        result = await container.build_service.build_project(
            local_path=project["local_path"],
            config=request
        )
        return BaseResponse(
            status=ResponseStatus.SUCCESS if result["success"] else ResponseStatus.ERROR,
            code="PROJECT_BUILD_RESULT",
            data=result
        )
    except Exception as e:
        logger.error(f"Build failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{project_id}/run")
async def run_project(
    project_id: str,
    request: Dict[str, Any] = None,
    api_key: str = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db)
):
    """
    Run a project.
    RBAC: Super Admin and Enterprise Admin can run any project in their scope.
    Developers can only run their own projects.
    """
    if not container.project_manager or not container.runtime_service:
        raise HTTPException(status_code=503, detail="Services not ready")
        
    project = await container.project_manager.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check access
    sm = get_security_manager()
    user_info = await sm.get_user_info(api_key, db)
    access_info = await check_access(user_info, project.get("user_id"), db)
    if not access_info["has_access"]:
        raise HTTPException(403, "Access denied to run this project")
        
    try:
        port = request.get("port", 8000) if request else 8000
        env = request.get("env", {}) if request else {}
        
        result = await container.runtime_service.start_project(
            project_id=project_id,
            local_path=project["local_path"],
            port=port,
            env_vars=env
        )
        return BaseResponse(
            status=ResponseStatus.SUCCESS if result["success"] else ResponseStatus.ERROR,
            code="PROJECT_RUN_RESULT",
            data=result
        )
    except Exception as e:
        logger.error(f"Run failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{project_id}/stop")
async def stop_project(
    project_id: str,
    api_key: str = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db)
):
    """
    Stop a running project.
    RBAC: Super Admin and Enterprise Admin can stop any project in their scope.
    Developers can only stop their own projects.
    """
    if not container.runtime_service:
         raise HTTPException(status_code=503, detail="Runtime service not ready")
    
    # Verify project exists and check access
    project = await container.project_manager.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check access
    sm = get_security_manager()
    user_info = await sm.get_user_info(api_key, db)
    access_info = await check_access(user_info, project.get("user_id"), db)
    if not access_info["has_access"]:
        raise HTTPException(403, "Access denied to stop this project")
    
    try:
        result = await container.runtime_service.stop_project(project_id)
        return BaseResponse(
            status=ResponseStatus.SUCCESS if result["success"] else ResponseStatus.ERROR,
            code="PROJECT_STOP_RESULT",
            data=result
        )
    except Exception as e:
        logger.error(f"Stop failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{project_id}/logs")
async def get_project_logs(
    project_id: str,
    lines: int = 100,
    api_key: str = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db)
):
    """
    Get project runtime logs.
    RBAC: Super Admin and Enterprise Admin can view logs of any project in their scope.
    Developers can only view logs of their own projects.
    """
    if not container.runtime_service:
         raise HTTPException(status_code=503, detail="Runtime service not ready")
    
    # Verify project exists and check access
    project = await container.project_manager.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check access
    sm = get_security_manager()
    user_info = await sm.get_user_info(api_key, db)
    access_info = await check_access(user_info, project.get("user_id"), db)
    if not access_info["has_access"]:
        raise HTTPException(403, "Access denied to view logs of this project")
    
    try:
        logs = await container.runtime_service.get_logs(project_id, lines)
        return BaseResponse(
            status=ResponseStatus.SUCCESS,
            code="PROJECT_LOGS_RETRIEVED",
            data={
                "project_id": project_id,
                "logs": logs
            }
        )
    except Exception as e:
        logger.error(f"Get logs failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

