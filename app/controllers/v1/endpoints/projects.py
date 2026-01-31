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
from sqlalchemy import select

# Core & Middleware
from ....core.database import get_db
from core.security import verify_api_key, SecurityManager, Role
from core.container import container
from ....middleware.auth import require_auth

# Models & DTOs
from platform_core.auth.models import User
from dto.v1.base import BaseResponse, ResponseStatus
from dto.v1.requests.project import ProjectCreateRequest, ProjectUpdateRequest, ProjectSearchRequest
from dto.v1.responses.project import ProjectResponseDTO, ProjectListResponseDTO
from dto.v1.schemas.enums import ProjectStatus, BuildStatus, RunStatus
from core.security import get_security_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/projects", tags=["Project Management"])

# --- Helper ---
async def check_access(user_info: dict, target_user_id: str, db: AsyncSession):
    """Verify if user has access to target resources via DB check (Async)."""
    role = user_info.get("role")
    uid = user_info.get("user_id")
    tenant_id = user_info.get("tenant_id")
    
    if role == Role.ADMIN.value:
        return True
    
    if role == Role.ENTERPRISE.value:
        if uid == target_user_id: 
            return True
        # Async check for target user tenant
        result = await db.execute(select(User).where(User.id == target_user_id))
        target_user = result.scalar_one_or_none()
        
        if target_user and target_user.tenant_id == tenant_id:
            return True
        raise HTTPException(403, "Access denied to user outside organization")

    if role == Role.DEVELOPER.value:
        if uid != target_user_id:
            raise HTTPException(403, "Developers can only access their own projects")
        return True
    
    return False

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
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1),
    api_key: str = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db)
):
    """List all projects belonging to a user (RBAC Enforced)."""
    sm = get_security_manager()
    user_info = await sm.get_user_info(api_key, db)
    
    if not user_info:
        raise HTTPException(401, "User not found")
        
    # If user_id is provided, check admin access. Otherwise use current user.
    target_user_id = user_id or user_info.get("user_id")
    await check_access(user_info, target_user_id, db)
    
    if not container.project_manager:
        raise HTTPException(status_code=503, detail="Project Manager not ready")
        
    filters = {
        "name": search or name,
        "framework": framework,
        "language": language,
        "solution_id": solution_id
    }
    
    result = await container.project_manager.get_user_projects(user_id, status, page, page_size, filters)
    
    projects = [ProjectResponseDTO.model_validate(p) for p in result["projects"]]
    
    return BaseResponse(
        status=ResponseStatus.SUCCESS,
        code="PROJECTS_RETRIEVED",
        message=f"Retrieved {len(projects)} projects for user {target_user_id}",
        data=ProjectListResponseDTO(
            projects=projects,
            total=result["total"],
            page=result["page"],
            page_size=result["page_size"]
        ),
        meta={"filters": filters}
    )

@router.get("/{project_id}", response_model=BaseResponse[ProjectResponseDTO])
async def get_project(
    project_id: str, 
    api_key: str = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db)
):
    """Get project details."""
    sm = get_security_manager()
    user_info = await sm.get_user_info(api_key, db)
    if not user_info: raise HTTPException(401)
    
    await check_access(user_info, user_id, db)
    
    if not container.project_manager:
        raise HTTPException(status_code=503, detail="Project Manager not ready")
        
    project = await container.project_manager.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    await check_access(user_info, project["user_id"], db)
        
    return BaseResponse(
        status=ResponseStatus.SUCCESS,
        code="PROJECT_DETAILS_RETRIEVED",
        message="Project details retrieved successfully",
        data=ProjectResponseDTO.model_validate(project)
    )

@router.post("/", response_model=BaseResponse[ProjectResponseDTO], status_code=status.HTTP_201_CREATED)
async def create_project(
    request: ProjectCreateRequest, 
    api_key: str = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db)
):
    """Create a new user project."""
    sm = get_security_manager()
    user_info = await sm.get_user_info(api_key, db)
    if not user_info: raise HTTPException(401)
    target_user_id = user_info.get("user_id")
    
    if not container.project_manager:
        raise HTTPException(status_code=503, detail="Project Manager not ready")
        
    project = await container.project_manager.create_project(
        user_id=target_user_id,
        project_name=request.project_name,
        description=request.description,
        git_repo_url=request.git_repo_url,
        language=request.language or "",
        framework=request.framework or ""
    )
    
    return BaseResponse(
        status=ResponseStatus.SUCCESS,
        code="PROJECT_CREATED",
        message="Project created successfully",
        data=ProjectResponseDTO.model_validate(project)
    )

@router.delete("/{project_id}", response_model=BaseResponse[Dict[str, str]])
async def delete_project(
    project_id: str, 
    api_key: str = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db)
):
    """Delete a user project."""
    sm = get_security_manager()
    user_info = await sm.get_user_info(api_key, db)
    if not user_info: raise HTTPException(401)
    project = await container.project_manager.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    await check_access(user_info, project["user_id"], db)
    
    success = await container.project_manager.delete_project(project_id, project["user_id"])
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
async def open_user_project(project_id: str, request: Dict[str, Any], api_key: str = Depends(verify_api_key), db: AsyncSession = Depends(get_db)):
    """Open a project: Clone from Git and load in IDE."""
    if not container.project_manager or not container.git_sync_service or not container.editor_service:
         raise HTTPException(status_code=503, detail="Project services not ready")

    project = await container.project_manager.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check ownership
    sm = get_security_manager()
    user_info = await sm.get_user_info(api_key, db)
    await check_access(user_info, project["user_id"], db)
    
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
async def sync_user_project(project_id: str, api_key: str = Depends(verify_api_key)):
    """Sync project with Git remote (pull)."""
    if not container.project_manager or not container.git_sync_service:
        raise HTTPException(status_code=503, detail="Project services not ready")
        
    project = await container.project_manager.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    res = await container.git_sync_service.pull_latest(project["local_path"])
    if not res["success"]:
        raise HTTPException(status_code=500, detail=res["error"])
        
    return BaseResponse(
        status=ResponseStatus.SUCCESS,
        code="PROJECT_VERSION_CHECKED",
        data={"commit": res["commit_hash"]}
    )

@router.post("/{project_id}/ai-update")
async def ai_update_project(project_id: str, request: Dict[str, Any], api_key: str = Depends(verify_api_key)):
    """Apply AI updates via chat prompt."""
    if not container.project_manager or not container.ai_update_service:
        raise HTTPException(status_code=503, detail="Project services not ready")
        
    project = await container.project_manager.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
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
async def execute_project_workflow(project_id: str, request: Dict[str, Any], api_key: str = Depends(verify_api_key)):
    """Execute a complete project workflow."""
    if not container.project_manager or not container.workflow_engine:
        raise HTTPException(status_code=503, detail="Workflow engine not ready")
        
    project = await container.project_manager.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
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
    api_key: str = Depends(verify_api_key)
):
    """Build a project."""
    if not container.project_manager or not container.build_service:
        raise HTTPException(status_code=503, detail="Services not ready")
        
    project = await container.project_manager.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
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
    api_key: str = Depends(verify_api_key)
):
    """Run a project."""
    if not container.project_manager or not container.runtime_service:
        raise HTTPException(status_code=503, detail="Services not ready")
        
    project = await container.project_manager.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
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
    api_key: str = Depends(verify_api_key)
):
    """Stop a running project."""
    if not container.runtime_service:
         raise HTTPException(status_code=503, detail="Runtime service not ready")
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
    api_key: str = Depends(verify_api_key)
):
    """Get project runtime logs."""
    if not container.runtime_service:
         raise HTTPException(status_code=503, detail="Runtime service not ready")
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

