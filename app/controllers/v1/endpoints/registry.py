from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Dict, Any, List, Optional
from services.registry.framework_registry import framework_registry
from platform_core.auth.dependencies import require_admin
from dto.v1.base import BaseResponse, ResponseStatus
from dto.v1.responses.supplemental import FrameworkDetailDTO
import logging

router = APIRouter(tags=["Registry Management"])
logger = logging.getLogger(__name__)

@router.get("/registry/frameworks")
async def get_frameworks(search: Optional[str] = None):
    """Get all frameworks and their metadata with optional search"""
    all_fw = framework_registry.get_all_frameworks()
    all_fw = framework_registry.get_all_frameworks()
    if not search:
        return BaseResponse(
            status=ResponseStatus.SUCCESS,
            code="FRAMEWORKS_RETRIEVED",
            message=f"Retrieved {sum(len(v) for v in all_fw.values())} frameworks",
            data=all_fw
        )
        
    search = search.lower()
    filtered = {}
    for lang, frameworks in all_fw.items():
        matched = {fw: data for fw, data in frameworks.items() if search in fw.lower() or search in lang.lower()}
        if matched:
            filtered[lang] = matched
            
    return BaseResponse(
        status=ResponseStatus.SUCCESS,
        code="FRAMEWORKS_SEARCHED",
        message=f"Found {sum(len(v) for v in filtered.values())} frameworks matching '{search}'",
        data=filtered,
        meta={"search": search}
    )

@router.get("/registry/frameworks/{language}")
async def get_language_frameworks(language: str):
    """Get all frameworks for a specific language"""
    lang = language.lower()
    all_fw = framework_registry.get_all_frameworks()
    if lang not in all_fw:
        raise HTTPException(status_code=404, detail=f"Language '{language}' not found in registry")
    return BaseResponse(
        status=ResponseStatus.SUCCESS,
        code="LANGUAGE_FRAMEWORKS_RETRIEVED",
        data=all_fw[lang]
    )

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
        return BaseResponse(
            status=ResponseStatus.SUCCESS,
            code="FRAMEWORK_UPDATED",
            message=f"Framework {language}/{framework} updated",
            data={"language": language, "framework": framework}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/registry/sync")
async def trigger_sync(background_tasks: BackgroundTasks, user=Depends(require_admin)):
    """Trigger an immediate version sync from external registries (Admin only)"""
    background_tasks.add_task(framework_registry.check_for_updates, apply=True)
    return BaseResponse(
        status=ResponseStatus.SUCCESS,
        code="SYNC_STARTED",
        message="Version sync started in background"
    )

@router.get("/registry/languages")
async def get_languages(search: Optional[str] = None):
    """Get all supported languages with optional search"""
    langs = framework_registry.languages
    if search:
        search = search.lower()
        langs = [l for l in langs if search in l.lower()]
        
    return BaseResponse(
        status=ResponseStatus.SUCCESS,
        code="LANGUAGES_RETRIEVED",
        message=f"Retrieved {len(langs)} supported languages",
        data=langs,
        meta={"search": search}
    )

@router.get("/registry/databases")
async def get_databases(search: Optional[str] = None):
    """Get all supported databases with optional search"""
    dbs = framework_registry.databases
    if search:
        search = search.lower()
        dbs = [d for d in dbs if search in d.lower()]
        
    return BaseResponse(
        status=ResponseStatus.SUCCESS,
        code="DATABASES_RETRIEVED",
        message=f"Retrieved {len(dbs)} supported databases",
        data=dbs,
        meta={"search": search}
    )

