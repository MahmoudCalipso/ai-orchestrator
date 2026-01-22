"""
Git Controller
Handles Git repository operations, configuration, and credentials.
"""
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from core.security import verify_api_key
from core.container import container
from schemas.api_spec import (
    StandardResponse, GitConfigUpdate, GitRepoInit
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Git"])

@router.post("/git/config/{provider}", response_model=StandardResponse)
async def set_git_config(provider: str, request: GitConfigUpdate, api_key: str = Depends(verify_api_key)):
    """Update or set credentials (token, SSH key) for a specific Git provider."""
    try:
        if not container.git_credentials:
            raise HTTPException(status_code=503, detail="Git Credentials service not ready")
            
        credentials = request.model_dump(exclude_none=True)
        success = container.git_credentials.set_credentials(provider, credentials)
        
        if success:
            return StandardResponse(status="success", message=f"Credentials set for {provider}")
        else:
            raise HTTPException(status_code=500, detail="Failed to set credentials")
    except Exception as e:
        logger.error(f"Failed to set Git config for {provider}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/git/config/{provider}")
async def delete_git_config(provider: str, api_key: str = Depends(verify_api_key)):
    """Delete credentials for a Git provider"""
    try:
        if not container.git_credentials:
            raise HTTPException(status_code=53, detail="Git Credentials service not ready")
            
        success = container.git_credentials.set_credentials(provider, {})
        if success:
            return {"status": "success", "provider": provider, "message": f"Credentials deleted for {provider}"}
        else:
            raise HTTPException(status_code=500, detail="Failed to delete credentials")
    except Exception as e:
        logger.error(f"Failed to delete Git config for {provider}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/git/validate/{provider}")
async def validate_git_credentials(provider: str, api_key: str = Depends(verify_api_key)):
    """Validate credentials for a Git provider"""
    try:
        if not container.git_credentials:
             raise HTTPException(status_code=503, detail="Git Credentials service not ready")
             
        is_valid = container.git_credentials.validate_credentials(provider)
        return {
            "valid": is_valid,
            "provider": provider,
            "message": "Credentials are valid" if is_valid else "Credentials are invalid or missing"
        }
    except Exception as e:
        logger.error(f"Failed to validate Git credentials for {provider}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/git/config")
async def get_general_git_config(api_key: str = Depends(verify_api_key)):
    """Get general Git configuration"""
    try:
        if not container.git_credentials:
             raise HTTPException(status_code=503, detail="Git Credentials service not ready")
             
        config = container.git_credentials.get_git_config()
        return {"config": config}
    except Exception as e:
        logger.error(f"Failed to get Git config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/git/repositories/init", response_model=StandardResponse)
async def init_repository(
    request: GitRepoInit,
    api_key: str = Depends(verify_api_key)
):
    """Initialize a new git repository in a specific directory."""
    try:
        if not container.repo_manager:
             raise HTTPException(status_code=503, detail="Repo Manager not ready")
             
        success = container.repo_manager.init_repository(request.path)
        return StandardResponse(status="success" if success else "failed", result={"path": request.path})
    except Exception as e:
        logger.error(f"Git init failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/git/repositories/clone", response_model=StandardResponse)
async def clone_repository(
    request: Dict[str, Any],
    api_key: str = Depends(verify_api_key)
):
    """Clone a Git repository to local path."""
    try:
        if not container.git_sync_service:
             raise HTTPException(status_code=503, detail="Git Sync service not ready")
             
        repo_url = request.get("repo_url")
        local_path = request.get("local_path")
        branch = request.get("branch", "main")
        credentials = request.get("credentials")
        
        result = await container.git_sync_service.clone_repository(
            repo_url=repo_url,
            local_path=local_path,
            branch=branch,
            credentials=credentials
        )
        
        if result["success"]:
            return StandardResponse(status="success", result=result)
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Clone failed"))
    except Exception as e:
        logger.error(f"Git clone failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/git/repositories/{repo_id}/push", response_model=StandardResponse)
async def push_repository(
    repo_id: str,
    request: Dict[str, Any],
    api_key: str = Depends(verify_api_key)
):
    """Push changes to remote repository."""
    try:
        if not container.git_sync_service:
             raise HTTPException(status_code=503, detail="Git Sync service not ready")
             
        local_path = request.get("local_path")
        branch = request.get("branch", "main")
        message = request.get("message", "Update from AI Orchestrator")
        
        result = await container.git_sync_service.push_changes(
            local_path=local_path,
            branch=branch,
            commit_message=message
        )
        
        if result["success"]:
            return StandardResponse(status="success", result=result)
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Push failed"))
    except Exception as e:
        logger.error(f"Git push failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/git/repositories/{repo_id}/pull", response_model=StandardResponse)
async def pull_repository(
    repo_id: str,
    request: Dict[str, Any],
    api_key: str = Depends(verify_api_key)
):
    """Pull latest changes from remote repository."""
    try:
        if not container.git_sync_service:
             raise HTTPException(status_code=503, detail="Git Sync service not ready")
             
        local_path = request.get("local_path")
        
        result = await container.git_sync_service.pull_latest(local_path)
        
        if result["success"]:
            return StandardResponse(status="success", result=result)
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Pull failed"))
    except Exception as e:
        logger.error(f"Git pull failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/git/repositories/{repo_id}/status")
async def get_repository_status(
    repo_id: str,
    local_path: str,
    api_key: str = Depends(verify_api_key)
):
    """Get Git repository status."""
    try:
        if not container.git_sync_service:
             raise HTTPException(status_code=503, detail="Git Sync service not ready")
             
        return await container.git_sync_service.get_status(local_path)
    except Exception as e:
        logger.error(f"Git status failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/git/repositories/{repo_id}/branches")
async def list_branches(
    repo_id: str,
    local_path: str,
    page: int = 1,
    page_size: int = 20,
    api_key: str = Depends(verify_api_key)
):
    """List all branches in repository with pagination."""
    try:
        import subprocess
        
        result = subprocess.run(
            ["git", "branch", "-a"],
            cwd=local_path,
            capture_output=True,
            text=True
        )
        
        branches = []
        current_branch = None
        
        for line in result.stdout.strip().split('\n'):
            line = line.strip()
            if line.startswith('*'):
                current_branch = line[2:]
                branches.append({"name": current_branch, "current": True})
            elif line:
                # Handle remote branches (remove 'remotes/origin/' etc if needed, but keeping raw for now)
                branches.append({"name": line, "current": False})
        
        total = len(branches)
        start = (page - 1) * page_size
        end = start + page_size
        paginated_branches = branches[start:end]
        
        return {
            "status": "success",
            "repo_id": repo_id,
            "current_branch": current_branch,
            "branches": paginated_branches,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": (total + page_size - 1) // page_size
            }
        }
    except Exception as e:
        logger.error(f"Git branches failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/git/repositories/{repo_id}/checkout", response_model=StandardResponse)
async def checkout_branch(
    repo_id: str,
    request: Dict[str, Any],
    api_key: str = Depends(verify_api_key)
):
    """Checkout a branch."""
    try:
        import subprocess
        
        local_path = request.get("local_path")
        branch = request.get("branch")
        create = request.get("create", False)
        
        cmd = ["git", "checkout"]
        if create:
            cmd.append("-b")
        cmd.append(branch)
        
        result = subprocess.run(
            cmd,
            cwd=local_path,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            return StandardResponse(
                status="success",
                result={"branch": branch, "message": f"Switched to branch '{branch}'"}
            )
        else:
            raise HTTPException(status_code=500, detail=result.stderr)
    except Exception as e:
        logger.error(f"Git checkout failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
