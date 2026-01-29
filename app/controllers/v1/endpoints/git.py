"""
Git Controller
Handles Git repository operations, configuration, and credentials.
"""
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends
from core.security import verify_api_key
from core.container import container
from dto.v1.base import BaseResponse, ResponseStatus
from dto.v1.requests.git import (
    GitConfigUpdate, GitRepoInit, GitRemoteCreate,
    GitBranchCreate, GitCommitRequest, GitConflictResolve, GitMergeRequest,
    GitCloneRequest, GitPullRequest
)
from dto.v1.responses.git import (
    GitStatusResponseDTO, GitLogResponseDTO, GitActionResponseDTO,
    GitBranchDTO, GitCommitDTO, GitCredentialsValidationDTO, GitRepoInfoDTO,
    GitBranchListResponseDTO, GitCheckoutResponseDTO
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Git"])

@router.post("/git/config/{provider}", response_model=BaseResponse)
async def set_git_config(provider: str, request: GitConfigUpdate, api_key: str = Depends(verify_api_key)):
    """Update or set credentials (token, SSH key) for a specific Git provider."""
    try:
        if not container.git_credentials:
            raise HTTPException(status_code=503, detail="Git Credentials service not ready")
            
        credentials = request.model_dump(exclude_none=True)
        success = container.git_credentials.set_credentials(provider, credentials)
        
        if success:
            return BaseResponse(
                status=ResponseStatus.SUCCESS, 
                code="GIT_CONFIG_UPDATED", 
                message=f"Credentials set for {provider}"
            )
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
            raise HTTPException(status_code=503, detail="Git Credentials service not ready")
            
        success = container.git_credentials.set_credentials(provider, {})
        if success:
            return BaseResponse(
                status=ResponseStatus.SUCCESS,
                code="GIT_CONFIG_DELETED",
                message=f"Credentials deleted for {provider}",
                data={"provider": provider}
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to delete credentials")
    except Exception as e:
        logger.error(f"Failed to delete Git config for {provider}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/git/validate/{provider}", response_model=BaseResponse[GitCredentialsValidationDTO])
async def validate_git_credentials(provider: str, api_key: str = Depends(verify_api_key)):
    """Validate credentials for a Git provider"""
    try:
        if not container.git_credentials:
             raise HTTPException(status_code=503, detail="Git Credentials service not ready")
             
        is_valid = container.git_credentials.validate_credentials(provider)
        return BaseResponse(
            status=ResponseStatus.SUCCESS if is_valid else ResponseStatus.ERROR,
            code="GIT_CREDENTIALS_VALIDATED",
            message="Credentials are valid" if is_valid else "Credentials are invalid or missing",
            data=GitCredentialsValidationDTO(
                valid=is_valid,
                provider=provider
            )
        )
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
        return BaseResponse(
            status=ResponseStatus.SUCCESS,
            code="GIT_CONFIG_RETRIEVED",
            data={"config": config}
        )
    except Exception as e:
        logger.error(f"Failed to get Git config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/git/repositories/init", response_model=BaseResponse[GitRepoInfoDTO])
async def init_repository(
    request: GitRepoInit,
    api_key: str = Depends(verify_api_key)
):
    """Initialize a new git repository in a specific directory."""
    try:
        if not container.repo_manager:
             raise HTTPException(status_code=503, detail="Repo Manager not ready")
             
        success = container.repo_manager.init_repository(request.path)
        return BaseResponse(
            status=ResponseStatus.SUCCESS if success else ResponseStatus.ERROR,
            code="GIT_REPO_INIT",
            message="Repository initialized" if success else "Failed to initialize repository",
            data=GitRepoInfoDTO(path=request.path)
        )
    except Exception as e:
        logger.error(f"Git init failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/git/repositories/clone", response_model=BaseResponse[GitActionResponseDTO])
async def clone_repository(
    request: GitCloneRequest,
    api_key: str = Depends(verify_api_key)
):
    """Clone a Git repository to local path."""
    try:
        if not container.git_sync_service:
             raise HTTPException(status_code=503, detail="Git Sync service not ready")
             
        result = await container.git_sync_service.clone_repository(
            repo_url=request.repo_url,
            local_path=request.local_path,
            branch=request.branch,
            credentials=request.credentials
        )
        
        if result["success"]:
            return BaseResponse(
                status=ResponseStatus.SUCCESS,
                code="GIT_CLONE_SUCCESS",
                message="Repository cloned successfully",
                data=GitActionResponseDTO(
                    success=True,
                    branch=request.branch,
                    output="Clone successful",
                    **{k:v for k,v in result.items() if k not in ["success", "branch"]}
                )
            )
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Clone failed"))
    except Exception as e:
        logger.error(f"Git clone failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/git/repositories/{repo_id}/push", response_model=BaseResponse[Dict[str, Any]])
async def push_repository(
    repo_id: str,
    request: GitCommitRequest,
    api_key: str = Depends(verify_api_key)
):
    """Push changes to remote repository."""
    try:
        if not container.git_sync_service:
             raise HTTPException(status_code=503, detail="Git Sync service not ready")
             
        result = await container.git_sync_service.push_changes(
            local_path=request.local_path,
            branch=request.branch,
            commit_message=request.message
        )
        
        if result["success"]:
            return BaseResponse(
                status=ResponseStatus.SUCCESS,
                code="GIT_PUSH_SUCCESS",
                message="Changes pushed successfully",
                data=GitActionResponseDTO(
                    success=True,
                    branch=request.branch,
                    output="Push successful",
                    **(result.get("metadata", {}) if isinstance(result.get("metadata"), dict) else {})
                )
            )
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Push failed"))
    except Exception as e:
        logger.error(f"Git push failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/git/repositories/{repo_id}/pull", response_model=BaseResponse[GitActionResponseDTO])
async def pull_repository(
    repo_id: str,
    request: GitPullRequest,
    api_key: str = Depends(verify_api_key)
):
    """Pull latest changes from remote repository."""
    try:
        if not container.git_sync_service:
             raise HTTPException(status_code=503, detail="Git Sync service not ready")
             
        result = await container.git_sync_service.pull_latest(request.local_path)
        
        if result["success"]:
            return BaseResponse(
                status=ResponseStatus.SUCCESS,
                code="GIT_PULL_SUCCESS",
                message="Latest changes pulled",
                data=GitActionResponseDTO(
                    success=True,
                    branch="current", # Assuming current
                    output="Pull successful",
                    **(result.get("metadata", {}) if isinstance(result.get("metadata"), dict) else {})
                )
            )
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
             
        status = await container.git_sync_service.get_status(local_path)
        return BaseResponse(
            status=ResponseStatus.SUCCESS,
            code="GIT_STATUS_RETRIEVED",
            message="Repository status retrieved",
            data=GitStatusResponseDTO.model_validate(status)
        )
    except Exception as e:
        logger.error(f"Git status failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/git/repositories/{repo_id}/branches")
async def list_branches(
    repo_id: str,
    local_path: str,
    search: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    api_key: str = Depends(verify_api_key)
):
    """List all branches in repository with search and pagination."""
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
                branches.append({"name": line, "current": False})
        
        if search:
            search = search.lower()
            branches = [b for b in branches if search in b["name"].lower()]
            
        total = len(branches)
        start = (page - 1) * page_size
        end = start + page_size
        paginated_branches = branches[start:end]
        
        return BaseResponse(
            status=ResponseStatus.SUCCESS,
            code="GIT_BRANCHES_RETRIEVED",
            message=f"Retrieved {len(paginated_branches)} branches for repository {repo_id}",
            data=GitBranchListResponseDTO(
                current_branch=current_branch,
                branches=[GitBranchDTO(name=b["name"], is_current=b["current"]) for b in paginated_branches]
            ),
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
    except Exception as e:
        logger.error(f"Git branches failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/git/repositories/{repo_id}/checkout", response_model=BaseResponse[Dict[str, Any]])
async def checkout_branch(
    repo_id: str,
    request: GitBranchCreate,
    api_key: str = Depends(verify_api_key)
):
    """Checkout a branch."""
    try:
        import subprocess
        
        local_path = request.local_path
        branch = request.branch_name
        create = True # Assuming creation if base branch is provided or for this flow
        
        cmd = ["git", "checkout"]
        # Basic logic: check if branch exists
        check_cmd = ["git", "rev-parse", "--verify", branch]
        exists = subprocess.run(check_cmd, cwd=local_path, capture_output=True).returncode == 0
        
        if not exists:
            cmd.append("-b")
        
        cmd.append(branch)
        
        result = subprocess.run(
            cmd,
            cwd=local_path,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            return BaseResponse(
                status=ResponseStatus.SUCCESS,
                code="GIT_CHECKOUT_SUCCESS",
                message=f"Switched to branch '{branch}'",
                data=GitCheckoutResponseDTO(branch=branch)
            )
        else:
            raise HTTPException(status_code=500, detail=result.stderr)
    except Exception as e:
        logger.error(f"Git checkout failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/git/repositories/{repo_id}/log", response_model=BaseResponse[GitLogResponseDTO])
async def get_repo_history(
    repo_id: str,
    local_path: str,
    limit: int = 50,
    api_key: str = Depends(verify_api_key)
):
    """Get repository commit history."""
    try:
        if not container.git_sync_service:
            raise HTTPException(status_code=503, detail="Git Sync service not ready")
        
        result = await container.git_sync_service.get_history(local_path, limit)
        # Assuming result is a list of commits or dict with commits
        commits = result if isinstance(result, list) else result.get("commits", [])
        
        return BaseResponse(
            status=ResponseStatus.SUCCESS,
            code="GIT_LOG_RETRIEVED",
            data=GitLogResponseDTO(
                commits=[GitCommitDTO(**c) for c in commits],
                total=len(commits)
            )
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/git/repositories/{repo_id}/diff")
async def get_repo_diff(
    repo_id: str,
    local_path: str,
    cached: bool = False,
    api_key: str = Depends(verify_api_key)
):
    """Get repository diff."""
    try:
        if not container.git_sync_service:
            raise HTTPException(status_code=503, detail="Git Sync service not ready")
        return await container.git_sync_service.get_diff(local_path, cached)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/git/repositories/{repo_id}/fetch", response_model=BaseResponse[GitActionResponseDTO])
async def fetch_repo(
    repo_id: str,
    local_path: str,
    api_key: str = Depends(verify_api_key)
):
    """Fetch from remote."""
    try:
        if not container.git_sync_service:
            raise HTTPException(status_code=503, detail="Git Sync service not ready")
        result = await container.git_sync_service.fetch_remote(local_path)
        return BaseResponse(
            status=ResponseStatus.SUCCESS if result["success"] else ResponseStatus.ERROR,
            code="GIT_FETCH_RESULT",
            data=GitActionResponseDTO(
                success=result["success"],
                branch="all",
                output=result.get("output", "Fetch completed"),
                error=result.get("error")
            )
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/git/repositories/{repo_id}/merge", response_model=BaseResponse[GitActionResponseDTO])
async def merge_branches(
    repo_id: str,
    request: GitMergeRequest,
    api_key: str = Depends(verify_api_key)
):
    """Merge branches using Repo Manager."""
    try:
        import subprocess
        subprocess.run(["git", "checkout", request.target_branch], cwd=request.local_path, check=True)
        result = subprocess.run(["git", "merge", request.source_branch], cwd=request.local_path, capture_output=True, text=True)
        
        if result.returncode == 0:
            return BaseResponse(
                status=ResponseStatus.SUCCESS,
                code="GIT_MERGE_SUCCESS",
                message=f"Merged {request.source_branch} into {request.target_branch}",
                data=GitActionResponseDTO(
                    success=True,
                    branch=request.target_branch,
                    output=result.stdout
                )
            )
        else:
            return BaseResponse(
                status=ResponseStatus.WARNING,
                code="GIT_MERGE_CONFLICT",
                message="Merge conflict detected",
                data=GitActionResponseDTO(
                    success=False,
                    branch=request.target_branch,
                    output=result.stdout,
                    error=result.stderr
                )
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/git/repositories/{repo_id}/remote", response_model=BaseResponse[Dict[str, Any]])
async def create_remote_repo(
    repo_id: str,
    request: GitRemoteCreate,
    api_key: str = Depends(verify_api_key)
):
    """Create a remote repository via API."""
    try:
        if not container.repo_manager:
            raise HTTPException(status_code=503, detail="Repo Manager not ready")
        
        clone_url = await container.repo_manager.create_remote_repository(
            provider=request.provider,
            name=request.name,
            description=request.description,
            private=request.private
        )
        
        if clone_url:
            return BaseResponse(
                status="success",
                code="GIT_REMOTE_CREATED",
                data={"clone_url": clone_url}
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to create remote repository")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/git/repositories/{repo_id}/resolve", response_model=BaseResponse[Dict[str, Any]])
async def resolve_conflict_ai(
    repo_id: str,
    request: GitConflictResolve,
    api_key: str = Depends(verify_api_key)
):
    """Resolve a conflict using AI."""
    try:
        if not container.repo_manager:
            raise HTTPException(status_code=503, detail="Repo Manager not ready")
        
        success = await container.repo_manager.ai_resolve_conflict(
            path=request.local_path,
            file_path=request.file_path,
            orchestrator=container.orchestrator
        )
        
        if success:
            return BaseResponse(
                status="success",
                code="GIT_CONFLICT_RESOLVED",
                message=f"Conflict resolved for {request.file_path}"
            )
        else:
            raise HTTPException(status_code=500, detail="AI failed to resolve conflict")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

