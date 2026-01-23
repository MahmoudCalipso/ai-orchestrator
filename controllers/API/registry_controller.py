from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Dict, Any, List, Optional
from services.registry.framework_registry import framework_registry
from platform_core.auth.dependencies import require_admin
import logging

router = APIRouter(tags=["Registry Management"])
logger = logging.getLogger(__name__)

@router.get("/registry/frameworks")
async def get_frameworks():
    """Get all frameworks and their metadata"""
    return framework_registry.get_all_frameworks()

@router.get("/registry/frameworks/{language}")
async def get_language_frameworks(language: str):
    """Get all frameworks for a specific language"""
    lang = language.lower()
    all_fw = framework_registry.get_all_frameworks()
    if lang not in all_fw:
        raise HTTPException(status_code=404, detail=f"Language '{language}' not found in registry")
    return all_fw[lang]

@router.post("/registry/frameworks/{language}/{framework}")
async def add_or_update_framework(
    language: str, 
    framework: str, 
    data: Dict[str, Any],
    user=Depends(require_admin)
):
    """Add or update a framework in the registry (Admin only)"""
    try:
        framework_registry.update_framework(language, framework, data)
        return {"status": "success", "message": f"Framework {language}/{framework} updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/registry/sync")
async def trigger_sync(background_tasks: BackgroundTasks, user=Depends(require_admin)):
    """Trigger an immediate version sync from external registries (Admin only)"""
    background_tasks.add_task(framework_registry.check_for_updates, apply=True)
    return {"status": "success", "message": "Version sync started in background"}

@router.get("/registry/languages")
async def get_languages():
    """Get all supported languages"""
    return framework_registry.languages

@router.get("/registry/databases")
async def get_databases():
    """Get all supported databases"""
    return framework_registry.databases
