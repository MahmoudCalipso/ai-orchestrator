"""
Workspace Controller
Handles multi-tenant workspace management.
"""
from fastapi import APIRouter, HTTPException, Depends
from core.security import verify_api_key
from core.container import container
from schemas.api_spec import (
    StandardResponse, WorkspaceCreateRequest, WorkspaceInviteRequest
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Workspace"])

@router.post("/workspace", response_model=StandardResponse)
async def create_workspace(
    request: WorkspaceCreateRequest,
    api_key: str = Depends(verify_api_key)
):
    """Create a new multi-tenant workspace for organization and team management."""
    try:
        from services.workspace import WorkspaceManager
        workspace_mgr = WorkspaceManager()
        
        workspace = workspace_mgr.create_workspace(
            request.name, 
            request.owner_id, 
            request.owner_name
        )
        return StandardResponse(status="success", result=workspace.to_dict())
    except Exception as e:
        logger.error(f"Failed to create workspace: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/workspace/{workspace_id}")
async def get_workspace(
    workspace_id: str,
    api_key: str = Depends(verify_api_key)
):
    """Get workspace"""
    try:
        from services.workspace import WorkspaceManager
        workspace_mgr = WorkspaceManager()
        
        workspace = workspace_mgr.get_workspace(workspace_id)
        if not workspace:
            raise HTTPException(status_code=404, detail="Workspace not found")
        return workspace.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get workspace: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/workspace/user/{user_id}")
async def list_user_workspaces(
    user_id: str,
    page: int = 1,
    page_size: int = 20,
    api_key: str = Depends(verify_api_key)
):
    """List user workspaces with pagination"""
    try:
        from services.workspace import WorkspaceManager
        workspace_mgr = WorkspaceManager()
        
        result = workspace_mgr.list_user_workspaces(user_id, page, page_size)
        return {
            "workspaces": [w.to_dict() for w in result["workspaces"]],
            "pagination": {
                "page": result["page"],
                "page_size": result["page_size"],
                "total": result["total"],
                "total_pages": result["total_pages"]
            }
        }
    except Exception as e:
        logger.error(f"Failed to list workspaces: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/workspace/{workspace_id}/members", response_model=StandardResponse)
async def invite_member(
    workspace_id: str,
    request: WorkspaceInviteRequest,
    api_key: str = Depends(verify_api_key)
):
    """Invite a new member to the workspace with a specific role."""
    try:
        from services.workspace import WorkspaceManager, WorkspaceRole
        workspace_mgr = WorkspaceManager()
        
        role = WorkspaceRole(request.role)
        
        success = workspace_mgr.invite_member(
            workspace_id,
            request.inviter_id,
            request.user_id,
            request.username,
            role
        )
        
        if not success:
            raise HTTPException(status_code=403, detail="Permission denied or member already exists")
        
        return StandardResponse(status="success", message="Member invited successfully")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to invite member: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/workspace/{workspace_id}/members/{user_id}")
async def remove_member(
    workspace_id: str,
    user_id: str,
    remover_id: str,
    api_key: str = Depends(verify_api_key)
):
    """Remove member from workspace"""
    try:
        from services.workspace import WorkspaceManager
        workspace_mgr = WorkspaceManager()
        
        success = workspace_mgr.remove_member(workspace_id, remover_id, user_id)
        
        if not success:
            raise HTTPException(status_code=403, detail="Permission denied")
        
        return {"status": "success"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to remove member: {e}")
        raise HTTPException(status_code=500, detail=str(e))
