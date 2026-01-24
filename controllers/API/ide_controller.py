"""
IDE Controller
Handles IDE workspaces, file operations, terminals, debugging, and code intelligence.
"""
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException, Depends
from core.security import verify_api_key
from core.container import container
from dto.common.base_response import BaseResponse
from dto.v1.requests.ide import (
    IDEWorkspaceRequest, IDEFileWriteRequest,
    IDETerminalRequest, IDEDebugRequest
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["IDE"])

@router.post("/ide/workspace", response_model=BaseResponse[Dict[str, Any]])
async def create_ide_workspace(
    request: IDEWorkspaceRequest,
    api_key: str = Depends(verify_api_key)
):
    """Initialize a persistent IDE workspace session, supporting multi-project bundles."""
    try:
        if not container.editor_service:
            raise HTTPException(status_code=503, detail="Editor service not ready")
            
        # Extract metadata for multi-project support
        data = request.model_dump()
        solution_id = data.get("solution_id")
        project_ids = data.get("project_ids", [])
        
        projects = []
        if solution_id:
            if container.project_manager:
                # Search for projects in this solution
                user_id = data.get("user_id") 
                proj_data = container.project_manager.get_user_projects(user_id, filters={"solution_id": solution_id})
                projects = proj_data.get("projects", [])
        elif project_ids:
            for pid in project_ids:
                p = container.project_manager.get_project(pid)
                if p: projects.append(p)

        if projects:
            # Multi-project initialization
            primary_project = projects[0]
            result = await container.editor_service.create_workspace(
                workspace_id=request.workspace_id,
                root_path=primary_project["local_path"]
            )
            # Add extra folders if service supports it
            if len(projects) > 1 and hasattr(container.editor_service, "add_workspace_folder"):
                 for p in projects[1:]:
                     await container.editor_service.add_workspace_folder(request.workspace_id, p["local_path"])
        else:
            result = await container.editor_service.create_workspace(request.workspace_id)
            
        return BaseResponse(
            status="success",
            code="IDE_WORKSPACE_CREATED",
            message=f"IDE Workspace '{request.workspace_id}' initialized",
            data=result,
            meta={"projects": [p["project_name"] for p in projects] if projects else [request.workspace_id]}
        )
    except Exception as e:
        logger.error(f"Failed to create IDE workspace: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ide/files/{workspace_id}/{path:path}")
async def read_file(
    workspace_id: str,
    path: str,
    api_key: str = Depends(verify_api_key)
):
    """Read file from workspace"""
    try:
        if not container.editor_service:
            raise HTTPException(status_code=503, detail="Editor service not ready")
            
        result = await container.editor_service.read_file(workspace_id, path)
        return result
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to read file: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ide/files/{workspace_id}/{path:path}", response_model=BaseResponse[Dict[str, Any]])
async def write_file(
    workspace_id: str,
    path: str,
    request: IDEFileWriteRequest,
    api_key: str = Depends(verify_api_key)
):
    """Write content to a file in the workspace."""
    try:
        if not container.editor_service:
            raise HTTPException(status_code=503, detail="Editor service not ready")
            
        result = await container.editor_service.write_file(workspace_id, path, request.content)
        return BaseResponse(
            status="success",
            code="FILE_WRITTEN",
            message=f"File {path} written successfully",
            data=result
        )
    except Exception as e:
        logger.error(f"Failed to write file: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/ide/files/{workspace_id}/{path:path}")
async def delete_file(
    workspace_id: str,
    path: str,
    api_key: str = Depends(verify_api_key)
):
    """Delete file from workspace"""
    try:
        if not container.editor_service:
            raise HTTPException(status_code=503, detail="Editor service not ready")
            
        result = await container.editor_service.delete_file(workspace_id, path)
        return result
    except Exception as e:
        logger.error(f"Failed to delete file: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ide/files/{workspace_id}")
async def list_files(
    workspace_id: str,
    directory: str = ".",
    search: Optional[str] = None,
    api_key: str = Depends(verify_api_key)
):
    """List files in workspace directory with search"""
    try:
        if not container.editor_service:
            raise HTTPException(status_code=503, detail="Editor service not ready")
            
        files = await container.editor_service.list_files(workspace_id, directory)
        if search:
            search = search.lower()
            files = [f for f in files if search in f["name"].lower()]
            
        return BaseResponse(
            status="success",
            code="FILES_LISTED",
            message=f"Listed {len(files)} files in {directory}",
            data=files,
            meta={"directory": directory, "search": search}
        )
    except Exception as e:
        logger.error(f"Failed to list files: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ide/terminal", response_model=BaseResponse[Dict[str, Any]])
async def create_terminal(
    request: IDETerminalRequest,
    api_key: str = Depends(verify_api_key)
):
    """Create a new interactive terminal session for a workspace."""
    try:
        if not container.terminal_service:
            raise HTTPException(status_code=503, detail="Terminal service not ready")
            
        session_id = await container.terminal_service.create_session(request.workspace_id, request.shell)
        return BaseResponse(
            status="success",
            code="TERMINAL_CREATED",
            message="Terminal session initialized",
            data={"session_id": session_id}
        )
    except Exception as e:
        logger.error(f"Failed to create terminal: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ide/debug", response_model=BaseResponse[Dict[str, Any]])
async def create_debug_session(
    request: IDEDebugRequest,
    api_key: str = Depends(verify_api_key)
):
    """Start a Debug Adapter Protocol (DAP) session for the project."""
    try:
        if not container.debugger_service:
            raise HTTPException(status_code=503, detail="Debugger service not ready")
            
        session_id = await container.debugger_service.create_session(
            request.workspace_id,
            request.language,
            request.program,
            request.args
        )
        return BaseResponse(
            status="success",
            code="DEBUG_SESSION_CREATED",
            message="Debug session initialized",
            data={"session_id": session_id}
        )
    except Exception as e:
        logger.error(f"Failed to create debug session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ide/debug/{session_id}/dap")
async def handle_dap_message(
    session_id: str,
    request: Dict[str, Any],
    api_key: str = Depends(verify_api_key)
):
    """Handle Debug Adapter Protocol message"""
    try:
        if not container.debugger_service:
            raise HTTPException(status_code=503, detail="Debugger service not ready")
            
        result = await container.debugger_service.handle_dap_message(session_id, request)
        return result
    except Exception as e:
        logger.error(f"DAP message failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ide/tree/{workspace_id}")
async def get_file_tree(
    workspace_id: str,
    api_key: str = Depends(verify_api_key)
):
    """Get complete file tree for a workspace"""
    try:
        if not container.editor_service:
            raise HTTPException(status_code=503, detail="Editor service not ready")
            
        return await container.editor_service.get_file_tree(workspace_id)
    except Exception as e:
        logger.error(f"Failed to get file tree: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ide/intelligence/completions/{workspace_id}/{path:path}")
async def get_completions(
    workspace_id: str,
    path: str,
    request: Dict[str, Any],
    api_key: str = Depends(verify_api_key)
):
    """Get AI-powered code completions"""
    try:
        if not container.editor_service:
            raise HTTPException(status_code=503, detail="Editor service not ready")
            
        return await container.editor_service.get_completions(
            workspace_id,
            path,
            request.get("offset", 0),
            request.get("language")
        )
    except Exception as e:
        logger.error(f"Failed to get completions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ide/intelligence/hover/{workspace_id}/{path:path}")
async def get_hover_info(
    workspace_id: str,
    path: str,
    request: Dict[str, Any],
    api_key: str = Depends(verify_api_key)
):
    """Get information about a symbol on hover"""
    try:
        if not container.editor_service:
            raise HTTPException(status_code=503, detail="Editor service not ready")
            
        return await container.editor_service.get_hover_info(
            workspace_id,
            path,
            request.get("symbol"),
            request.get("language")
        )
    except Exception as e:
        logger.error(f"Failed to get hover info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ide/intelligence/diagnostics/{workspace_id}/{path:path}")
async def get_diagnostics(
    workspace_id: str,
    path: str,
    language: Optional[str] = None,
    api_key: str = Depends(verify_api_key)
):
    """Get code diagnostics"""
    try:
        if not container.editor_service:
            raise HTTPException(status_code=503, detail="Editor service not ready")
            
        return await container.editor_service.get_diagnostics(workspace_id, path, language)
    except Exception as e:
        logger.error(f"Failed to get diagnostics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ide/intelligence/refactor/{workspace_id}/{path:path}")
async def ai_refactor(
    workspace_id: str,
    path: str,
    request: Dict[str, Any],
    api_key: str = Depends(verify_api_key)
):
    """Perform AI-powered refactoring"""
    try:
        if not container.editor_service:
            raise HTTPException(status_code=503, detail="Editor service not ready")
            
        return await container.editor_service.ai_refactor(
            workspace_id,
            path,
            request.get("instruction"),
            request.get("language")
        )
    except Exception as e:
        logger.error(f"Failed to perform AI refactor: {e}")
        raise HTTPException(status_code=500, detail=str(e))
