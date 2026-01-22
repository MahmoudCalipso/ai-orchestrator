"""
Storage Controller
Handles project storage, archiving, cleanup, and backups.
"""
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends
from core.security import verify_api_key
from schemas.api_spec import StandardResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Storage"])

@router.get("/storage/stats")
async def get_storage_stats(api_key: str = Depends(verify_api_key)):
    """Retrieve statistics about local storage usage."""
    try:
        from core.storage import StorageManager
        storage = StorageManager()
        stats = await storage.get_storage_stats()
        return {"status": "success", "stats": stats}
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
        from core.storage import StorageManager
        storage = StorageManager()
        result = await storage.list_projects(
            status=status,
            language=language,
            min_size_gb=min_size_gb,
            page=page,
            page_size=page_size
        )
        return {
            "status": "success",
            "projects": result["projects"],
            "pagination": {
                "page": result["page"],
                "page_size": result["page_size"],
                "total": result["total"],
                "total_pages": result["total_pages"]
            }
        }
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
        from core.storage import StorageManager
        storage = StorageManager()
        project = await storage.get_project(project_id)
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        return {
            "status": "success",
            "project": project
        }
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
        from core.storage import StorageManager
        storage = StorageManager()
        success = await storage.delete_project(project_id, soft=soft)
        
        if not success:
            raise HTTPException(status_code=404, detail="Project not found")
        
        return {
            "status": "success",
            "message": f"Project {'soft' if soft else 'hard'} deleted",
            "project_id": project_id
        }
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
        from core.storage import StorageManager
        storage = StorageManager()
        success = await storage.archive_project(project_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Project not found")
        
        return {
            "status": "success",
            "message": "Project archived",
            "project_id": project_id
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to archive project: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/storage/cleanup")
async def cleanup_storage(api_key: str = Depends(verify_api_key)):
    """Run storage cleanup"""
    try:
        from core.storage import StorageManager, BackupManager
        
        storage = StorageManager()
        backup_mgr = BackupManager()
        
        # Archive old projects
        archived_count = await storage.archive_old_projects(days=90)
        
        # Clean cache
        freed_bytes = await storage.clean_cache()
        
        # Remove old backups
        removed_backups = await backup_mgr.cleanup_old_backups(days=30)
        
        return {
            "status": "success",
            "archived_projects": archived_count,
            "freed_bytes": freed_bytes,
            "freed_gb": freed_bytes / (1024**3),
            "removed_backups": removed_backups
        }
    except Exception as e:
        logger.error(f"Storage cleanup failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/storage/backup/{project_id}")
async def backup_stored_project(project_id: str, api_key: str = Depends(verify_api_key)):
    """Back up a stored project manually."""
    try:
        from core.storage.backup import BackupManager
        backup_manager = BackupManager()
        result = await backup_manager.create_backup(project_id)
        if result:
            return {"status": "success", "message": f"Backup created: {result}"}
        else:
            raise HTTPException(status_code=500, detail="Failed to create backup")
    except Exception as e:
        logger.error(f"Backup failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
