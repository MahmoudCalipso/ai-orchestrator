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
    """Get all frameworks and their metadata categorized (Backend, Frontend, Mobile)"""
    all_cat = framework_registry.get_all_frameworks()
    
    if not search:
        return BaseResponse(
            status=ResponseStatus.SUCCESS,
            code="FRAMEWORKS_RETRIEVED",
            message=f"Retrieved categorized frameworks",
            data=all_cat
        )
        
    search = search.lower()
    filtered = {}
    for cat, langs in all_cat.items():
        cat_match = {}
        for lang, fws in langs.items():
            fw_match = {fw: data for fw, data in fws.items() if search in fw.lower() or search in lang.lower() or search in cat.lower()}
            if fw_match:
                cat_match[lang] = fw_match
        if cat_match:
            filtered[cat] = cat_match
            
    return BaseResponse(
        status=ResponseStatus.SUCCESS,
        code="FRAMEWORKS_SEARCHED",
        message=f"Found frameworks matching '{search}'",
        data=filtered,
        meta={"search": search}
    )

@router.get("/registry/frameworks/{category}/{language}")
async def get_categorized_frameworks(category: str, language: str):
    """Get all frameworks for a specific category and language"""
    cat, lang = category.lower(), language.lower()
    all_fw = framework_registry.get_all_frameworks()
    
    if cat not in all_fw:
        raise HTTPException(status_code=404, detail=f"Category '{category}' not found")
    if lang not in all_fw[cat]:
        raise HTTPException(status_code=404, detail=f"Language '{language}' not found in category '{category}'")
        
    return BaseResponse(
        status=ResponseStatus.SUCCESS,
        code="CATEGORY_FRAMEWORKS_RETRIEVED",
        data=all_fw[cat][lang]
    )

@router.post("/registry/frameworks/{category}/{language}/{framework}")
async def add_or_update_framework(
    category: str,
    language: str, 
    framework: str, 
    data: Dict[str, Any],
    user=Depends(require_admin)
):
    """Add or update a framework in the registry (Admin only)"""
    try:
        framework_registry.update_framework(category, language, framework, data)
        return BaseResponse(
            status=ResponseStatus.SUCCESS,
            code="FRAMEWORK_UPDATED",
            message=f"Framework {category}/{language}/{framework} updated",
            data={"category": category, "language": language, "framework": framework}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/registry/packages")
async def get_packages(language: str, framework: str, database: Optional[str] = None):
    """Get required packages for a given stack (includes DB drivers)"""
    packages = framework_registry.get_required_packages(language, framework, database)
    return BaseResponse(
        status=ResponseStatus.SUCCESS,
        code="PACKAGES_RETRIEVED",
        data={"packages": packages}
    )

@router.get("/registry/best-practices")
async def get_best_practices(language: str, framework: str):
    """Retrieve technical best practices for a specific framework"""
    practices = framework_registry.get_best_practices(language, framework)
    return BaseResponse(
        status=ResponseStatus.SUCCESS,
        code="BEST_PRACTICES_RETRIEVED",
        data={"best_practices": practices}
    )

@router.get("/registry/architecture-templates")
async def get_arch_templates(architecture: str, language: Optional[str] = None, framework: Optional[str] = None):
    """Get detailed project structure templates for a given architecture"""
    template = framework_registry.get_architecture_template(architecture, language, framework)
    return BaseResponse(
        status=ResponseStatus.SUCCESS,
        code="ARCH_TEMPLATE_RETRIEVED",
        data=template
    )

@router.get("/registry/languages")
async def get_languages(search: Optional[str] = None):
    """Get all supported languages with optional search"""
    langs = framework_registry.languages
    if search:
        search = search.lower()
        langs = {l: data for l, data in langs.items() if search in l.lower()}
        
    return BaseResponse(
        status=ResponseStatus.SUCCESS,
        code="LANGUAGES_RETRIEVED",
        message=f"Retrieved {len(langs)} supported languages",
        data=langs,
        meta={"search": search}
    )

@router.get("/registry/databases")
async def get_databases(search: Optional[str] = None):
    """Get all supported databases grouped by type (SQL, NoSQL, Vector)"""
    dbs = framework_registry.databases
    if not search:
        return BaseResponse(
            status=ResponseStatus.SUCCESS,
            code="DATABASES_RETRIEVED",
            message=f"Retrieved categorized databases",
            data=dbs
        )
        
    search = search.lower()
    filtered = {}
    for db_type, db_list in dbs.items():
        matched = {name: data for name, data in db_list.items() if search in name.lower() or search in db_type.lower()}
        if matched:
            filtered[db_type] = matched
            
    return BaseResponse(
        status=ResponseStatus.SUCCESS,
        code="DATABASES_SEARCHED",
        message=f"Found databases matching '{search}'",
        data=filtered,
        meta={"search": search}
    )

