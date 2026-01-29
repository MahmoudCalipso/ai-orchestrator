"""
Storage Controller
Handles project storage, archiving, cleanup, and backups.
"""
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException, Depends
from core.security import verify_api_key
from core.container import container
from dto.common.base_response import BaseResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Storage"])

@router.get("/storage/stats")
async def get_storage_stats(api_key: str = Depends(verify_api_key)):
    """Retrieve statistics about local storage usage."""
    try:
        if not container.storage_manager:
            raise HTTPException(status_code=503, detail="Storage service not ready")
        stats = await container.storage_manager.get_storage_stats()
        return BaseResponse(
            status="success",
            code="STORAGE_STATS_RETRIEVED",
            message="Storage statistics retrieved",
            data=stats
        )
    except Exception as e:
        logger.error(f"Failed to get storage stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/storage/projects")
async def list_stored_projects(
    status: Optional[str] = None,
    language: Optional[str] = None,
    min_size_gb: Optional[float] = None,
    page: int = 1,
    page_size: int = 20,
    api_key: str = Depends(verify_api_key)
):
    """List all generated projects currently stored on disk with pagination."""
    try:
        if not container.storage_manager:
            raise HTTPException(status_code=53, detail="Storage service not ready")
        result = await container.storage_manager.list_projects(
            status=status,
            language=language,
            min_size_gb=min_size_gb,
            page=page,
            page_size=page_size
        )
        return BaseResponse(
            status="success",
            code="STORED_PROJECTS_RETRIEVED",
            message=f"Retrieved {len(result['projects'])} projects from storage",
            data=result["projects"],
            meta={
                "pagination": {
                    "page": result["page"],
                    "page_size": result["page_size"],
                    "total": result["total"],
                    "total_pages": result["total_pages"]
                }
            }
        )
    except Exception as e:
        logger.error(f"Failed to list projects: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to list projects: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/storage/projects/{project_id}")
async def get_stored_project(
    project_id: str,
    api_key: str = Depends(verify_api_key)
):
    """Retrieve detailed metadata and file structure for a specific stored project."""
    try:
        if not container.storage_manager:
            raise HTTPException(status_code=503, detail="Storage service not ready")
        project = await container.storage_manager.get_project(project_id)
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        return BaseResponse(
            status="success",
            code="STORED_PROJECT_RETRIEVED",
            data=project
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get project: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/storage/projects/{project_id}")
async def delete_stored_project(
    project_id: str,
    soft: bool = True,
    api_key: str = Depends(verify_api_key)
):
    """Delete a project (soft or hard delete)"""
    try:
        if not container.storage_manager:
            raise HTTPException(status_code=503, detail="Storage service not ready")
        success = await container.storage_manager.delete_project(project_id, soft=soft)
        
        if not success:
            raise HTTPException(status_code=404, detail="Project not found")
        
        return BaseResponse(
            status="success",
            code="PROJECT_DELETED",
            message=f"Project {'soft' if soft else 'hard'} deleted",
            data={"project_id": project_id}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete project: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/storage/archive/{project_id}")
async def archive_stored_project(
    project_id: str,
    api_key: str = Depends(verify_api_key)
):
    """Archive a project"""
    try:
        if not container.storage_manager:
            raise HTTPException(status_code=503, detail="Storage service not ready")
        success = await container.storage_manager.archive_project(project_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Project not found")
        
        return BaseResponse(
            status="success",
            code="PROJECT_ARCHIVED",
            message="Project archived",
            data={"project_id": project_id}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to archive project: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/storage/cleanup")
async def cleanup_storage(api_key: str = Depends(verify_api_key)):
    """Run storage cleanup"""
    try:
        if not container.storage_manager or not container.backup_manager:
            raise HTTPException(status_code=503, detail="Storage or Backup service not ready")
        
        # Archive old projects
        archived_count = await container.storage_manager.archive_old_projects(days=90)
        
        # Clean cache
        freed_bytes = await container.storage_manager.clean_cache()
        
        # Remove old backups
        removed_backups = await container.backup_manager.cleanup_old_backups(days=30)
        
        return BaseResponse(
            status="success",
            code="STORAGE_CLEANUP_SUCCESS",
            data={
                "archived_projects": archived_count,
                "freed_bytes": freed_bytes,
                "freed_gb": freed_bytes / (1024**3),
                "removed_backups": removed_backups
            }
        )
    except Exception as e:
        logger.error(f"Storage cleanup failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/storage/backup/{project_id}")
async def backup_stored_project(project_id: str, api_key: str = Depends(verify_api_key)):
    """Back up a stored project manually."""
    try:
        if not container.backup_manager:
            raise HTTPException(status_code=503, detail="Backup service not ready")
        result = await container.backup_manager.create_backup(project_id)
        if result:
            return BaseResponse(
                status="success",
                code="BACKUP_CREATED",
                message=f"Backup created: {result}",
                data={"backup_path": result}
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to create backup")
    except Exception as e:
        logger.error(f"Backup failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

