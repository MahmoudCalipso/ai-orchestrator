"""
Workspace Controller
Handles multi-tenant workspace management.
"""
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException, Depends
from core.security import verify_api_key
from core.container import container
from dto.common.base_response import BaseResponse
from dto.v1.requests.workspace import (
    WorkspaceCreateRequest, WorkspaceInviteRequest, CollaborationSessionRequest
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Workspace"])

@router.post("/workspace", response_model=BaseResponse[Dict[str, Any]])
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
        return BaseResponse(
            status="success",
            code="WORKSPACE_CREATED",
            message="Workspace created successfully",
            data=workspace.to_dict()
        )
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
    search: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    api_key: str = Depends(verify_api_key)
):
    """List user workspaces with search and pagination"""
    try:
        from services.workspace import WorkspaceManager
        workspace_mgr = WorkspaceManager()
        
        result = workspace_mgr.list_user_workspaces(user_id, page, page_size)
        workspaces = [w.to_dict() for w in result["workspaces"]]
        
        if search:
            search = search.lower()
            workspaces = [w for w in workspaces if search in w["name"].lower()]
            
        return BaseResponse(
            status="success",
            code="WORKSPACES_RETRIEVED",
            message=f"Retrieved {len(workspaces)} workspaces",
            data=workspaces,
            meta={
                "pagination": {
                    "page": result["page"],
                    "page_size": result["page_size"],
                    "total": len(workspaces) if search else result["total"],
                    "total_pages": result["total_pages"]
                },
                "search": search
            }
        )
    except Exception as e:
        logger.error(f"Failed to list workspaces: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/workspace/{workspace_id}/members", response_model=BaseResponse)
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
        
        return BaseResponse(
            status="success",
            code="MEMBER_INVITED",
            message="Member invited successfully",
            data={"workspace_id": workspace_id, "user_id": request.user_id}
        )
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
        
        return BaseResponse(
            status="success",
            code="MEMBER_REMOVED",
            message=f"User {user_id} removed from workspace"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to remove member: {e}")
        raise HTTPException(status_code=500, detail=str(e))

