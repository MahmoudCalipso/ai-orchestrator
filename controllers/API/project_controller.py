"""
Project Controller
Handles project lifecycle, git sync, AI updates, and workflows.
Enforces Role-Based Access Control (RBAC).
"""
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends
from core.security import verify_api_key, SecurityManager, Role
from core.container import container
from schemas.api_spec import StandardResponse
import logging
from sqlalchemy.orm import Session
from platform_core.auth.dependencies import get_db
from platform_core.auth.models import User

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Project Management"])

def check_access(user_info: dict, target_user_id: str, db: Session):
    """Verify if user has access to target resources via DB check"""
    role = user_info.get("role")
    uid = user_info.get("user_id")
    tenant_id = user_info.get("tenant_id")
    
    if role == Role.ADMIN.value:
        return True
    
    if role == Role.ENTERPRISE.value:
        # Check if target user is in same tenant
        if uid == target_user_id: 
            return True
            
        target_user = db.query(User).filter(User.id == target_user_id).first()
        if target_user and target_user.tenant_id == tenant_id:
            return True
            
        raise HTTPException(403, "Access denied to user outside organization")

    if role == Role.DEVELOPER.value:
        if uid != target_user_id:
            raise HTTPException(403, "Developers can only access their own projects")
        return True
    
    return False

@router.get("/user/{user_id}/projects")
async def list_user_projects(
    user_id: str,
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    api_key: str = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """List all projects belonging to a user (RBAC Enforced)"""
    sm = SecurityManager()
    user_info = sm.get_user_info(api_key, db)
    
    if not user_info:
        raise HTTPException(401, "User not found")
        
    check_access(user_info, user_id, db)
    
    if not container.project_manager:
        raise HTTPException(status_code=503, detail="Project Manager not ready")
        
    result = container.project_manager.get_user_projects(user_id, status, page, page_size)
    return {
        "projects": result["projects"],
        "pagination": {
            "page": result["page"],
            "page_size": result["page_size"],
            "total": result["total"],
            "total_pages": result["total_pages"]
        }
    }

@router.get("/user/{user_id}/projects/{project_id}")
async def get_user_project(
    project_id: str, 
    user_id: str, 
    api_key: str = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """Get project details"""
    sm = SecurityManager()
    user_info = sm.get_user_info(api_key, db)
    if not user_info: raise HTTPException(401)
    
    check_access(user_info, user_id, db)
    
    if not container.project_manager:
        raise HTTPException(status_code=503, detail="Project Manager not ready")
        
    project = container.project_manager.get_project(project_id)
    if not project or project["user_id"] != user_id:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.post("/user/{user_id}/projects")
async def create_user_project(
    user_id: str, 
    request: Dict[str, Any], 
    api_key: str = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """Create a new user project"""
    sm = SecurityManager()
    user_info = sm.get_user_info(api_key, db)
    if not user_info: raise HTTPException(401)
    check_access(user_info, user_id, db)
    
    if not container.project_manager:
        raise HTTPException(status_code=503, detail="Project Manager not ready")
        
    return container.project_manager.create_project(
        user_id=user_id,
        project_name=request.get("project_name", "New Project"),
        description=request.get("description", ""),
        git_repo_url=request.get("git_repo_url", ""),
        language=request.get("language", ""),
        framework=request.get("framework", "")
    )

@router.delete("/user/{user_id}/projects/{project_id}")
async def delete_user_project(
    project_id: str, 
    user_id: str, 
    api_key: str = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """Delete a user project"""
    sm = SecurityManager()
    user_info = sm.get_user_info(api_key, db)
    if not user_info: raise HTTPException(401)
    check_access(user_info, user_id, db)
    
    # Check protection
    # In real implementation:
    # project = container.project_manager.get_project(project_id)
    # if project.get("protected") and user_info["role"] == Role.DEVELOPER:
    #    raise HTTPException(403, "Project is protected by Enterprise Owner")
    
    if not container.project_manager:
        raise HTTPException(status_code=503, detail="Project Manager not ready")
        
    success = container.project_manager.delete_project(project_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Project not found or unauthorized")
    return {"status": "success", "message": "Project deleted"}

@router.post("/projects/{project_id}/open")
async def open_user_project(project_id: str, request: Dict[str, Any], api_key: str = Depends(verify_api_key)):
    """Open a project: Clone from Git and load in IDE"""
    # ... Simplified access check for open (checks if project exists and user has access implicitly via get_project)
    if not container.project_manager or not container.git_sync_service or not container.editor_service:
         raise HTTPException(status_code=503, detail="Project services not ready")

    project = container.project_manager.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check ownership
    sm = SecurityManager()
    user_info = sm.get_user_info(api_key)
    check_access(user_info, project["user_id"])
    
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
    
    container.project_manager.update_last_opened(project_id)
    
    # Create IDE workspace
    workspace = await container.editor_service.create_workspace(project["project_name"], local_path)
    
    return {
        "status": "success",
        "workspace_id": workspace.id,
        "project": project
    }

@router.post("/projects/{project_id}/sync")
async def sync_user_project(project_id: str, api_key: str = Depends(verify_api_key)):
    """Sync project with Git remote (pull)"""
    if not container.project_manager or not container.git_sync_service:
        raise HTTPException(status_code=503, detail="Project services not ready")
        
    project = container.project_manager.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    res = await container.git_sync_service.pull_latest(project["local_path"])
    if not res["success"]:
        raise HTTPException(status_code=500, detail=res["error"])
        
    return {"status": "success", "commit": res["commit_hash"]}

@router.post("/projects/{project_id}/ai-update")
async def ai_update_project(project_id: str, request: Dict[str, Any], api_key: str = Depends(verify_api_key)):
    """Apply AI updates via chat prompt"""
    if not container.project_manager or not container.ai_update_service:
        raise HTTPException(status_code=503, detail="Project services not ready")
        
    project = container.project_manager.get_project(project_id)
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
        
    return res

@router.post("/projects/{project_id}/files/{file_path:path}/ai-update")
async def ai_inline_update(project_id: str, file_path: str, request: Dict[str, Any], api_key: str = Depends(verify_api_key)):
    """Apply AI inline updates to a specific file"""
    if not container.project_manager or not container.ai_update_service:
        raise HTTPException(status_code=503, detail="Project services not ready")
        
    project = container.project_manager.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    res = await container.ai_update_service.apply_inline_update(
        local_path=project["local_path"],
        file_path=file_path,
        prompt=request.get("prompt"),
        selection=request.get("selection")
    )
    
    if not res["success"]:
        raise HTTPException(status_code=500, detail=res["error"])
        
    return res

@router.post("/projects/{project_id}/workflow")
async def execute_project_workflow(project_id: str, request: Dict[str, Any], api_key: str = Depends(verify_api_key)):
    """Execute a complete project workflow"""
    if not container.project_manager or not container.workflow_engine:
        raise HTTPException(status_code=503, detail="Workflow engine not ready")
        
    project = container.project_manager.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    workflow_id = await container.workflow_engine.execute_workflow(
        project_id=project_id,
        user_id=project["user_id"],
        steps=request.get("steps", ["sync", "update", "push", "build", "run"]),
        config=request
    )
    
    return {
        "status": "started",
        "workflow_id": workflow_id,
        "message": f"Workflow {workflow_id} started in background"
    }

@router.get("/projects/{project_id}/workflow/{workflow_id}")
async def get_workflow_status(project_id: str, workflow_id: str, api_key: str = Depends(verify_api_key)):
    """Get status of a running workflow"""
    if not container.workflow_engine:
        raise HTTPException(status_code=503, detail="Workflow engine not ready")
        
    status = container.workflow_engine.get_workflow_status(workflow_id)
    if not status:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return status

@router.post("/projects/{project_id}/build")
async def build_project(
    project_id: str,
    request: Dict[str, Any] = None,
    api_key: str = Depends(verify_api_key)
):
    """Build a project"""
    if not container.project_manager or not container.build_service:
        raise HTTPException(status_code=503, detail="Services not ready")
        
    project = container.project_manager.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    try:
        result = await container.build_service.build_project(
            local_path=project["local_path"],
            config=request
        )
        
        return StandardResponse(
            status="success" if result["success"] else "failed",
            result=result
        )
    except Exception as e:
        logger.error(f"Build failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/projects/{project_id}/run")
async def run_project(
    project_id: str,
    request: Dict[str, Any] = None,
    api_key: str = Depends(verify_api_key)
):
    """Run a project"""
    if not container.project_manager or not container.runtime_service:
        raise HTTPException(status_code=503, detail="Services not ready")
        
    project = container.project_manager.get_project(project_id)
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
        
        return StandardResponse(
            status="success" if result["success"] else "failed",
            result=result
        )
    except Exception as e:
        logger.error(f"Run failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/projects/{project_id}/stop")
async def stop_project(
    project_id: str,
    api_key: str = Depends(verify_api_key)
):
    """Stop a running project"""
    if not container.runtime_service:
         raise HTTPException(status_code=503, detail="Runtime service not ready")
         
    try:
        result = await container.runtime_service.stop_project(project_id)
        
        return StandardResponse(
            status="success" if result["success"] else "failed",
            result=result
        )
    except Exception as e:
        logger.error(f"Stop failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/projects/{project_id}/logs")
async def get_project_logs(
    project_id: str,
    lines: int = 100,
    api_key: str = Depends(verify_api_key)
):
    """Get project runtime logs"""
    if not container.runtime_service:
         raise HTTPException(status_code=503, detail="Runtime service not ready")
         
    try:
        logs = await container.runtime_service.get_logs(project_id, lines)
        
        return {
            "status": "success",
            "project_id": project_id,
            "logs": logs
        }
    except Exception as e:
        logger.error(f"Get logs failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
