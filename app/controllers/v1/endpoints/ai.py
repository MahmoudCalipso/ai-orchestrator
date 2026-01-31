"""
AI Inference & Management API Controller (Open-Source Models)
Uses local Ollama inference - NO API KEYS REQUIRED
"""
from typing import Dict, Any, List, Optional
import logging
from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

# Core & Services
from core.security import verify_api_key, get_security_manager, Role
from core.container import container
from ....core.llm.service import get_llm_service, ModelTier
from ....core.database import get_db
from dto.v1.base import BaseResponse, ResponseStatus
from dto.v1.requests.ai import (
    InferenceRequest, FixCodeRequest, AnalyzeCodeRequest, TestCodeRequest,
    OptimizeCodeRequest, RefactorCodeRequest, ExplainCodeRequest,
    DocumentCodeRequest
)
from dto.v1.requests.generation import GenerationRequest, MigrationRequest as SwarmMigrationRequest
from dto.v1.responses.ai import ModelInfoDTO, InferenceResponseDTO, SwarmResponseDTO, ModelListResponseDTO, ModelSummaryDTO
from platform_core.auth.models import User as AuthUserModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai", tags=["AI Intelligence"])

@router.get("/models")
async def list_models(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1),
    api_key: str = Depends(verify_api_key)
):
    """List all available open-source AI models."""
    try:
        llm_service = get_llm_service()
        models = await llm_service.list_models()
        
        total = len(models)
        start = (page - 1) * page_size
        end = start + page_size
        paginated = models[start:end]
        
        models_data = [
            ModelSummaryDTO(name=m, provider="ollama", is_local=True) 
            for m in paginated
        ]
        
        return BaseResponse(
            status=ResponseStatus.SUCCESS,
            code="MODELS_DISCOVERED",
            message=f"Discovered {len(paginated)} open-source AI models",
            data=ModelListResponseDTO(
                models=models_data,
                total=total
            ),
            meta={
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total": total,
                    "total_pages": (total + page_size - 1) // page_size
                },
                "tier": llm_service.tier.value
            }
        )
    except Exception as e:
        logger.error(f"Failed to list models: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/models/{model_name}", response_model=BaseResponse[ModelInfoDTO])
async def get_model_info(
    model_name: str,
    api_key: str = Depends(verify_api_key)
):
    """Retrieve detailed metadata for a specific AI model."""
    try:
        if container.orchestrator:
            model_info = await container.orchestrator.get_model_info(model_name)
            if not model_info:
                raise HTTPException(status_code=404, detail="Model not found")
            return BaseResponse(
                status=ResponseStatus.SUCCESS,
                code="MODEL_INFO_RETRIEVED",
                data=ModelInfoDTO.model_validate(model_info)
            )
        raise HTTPException(status_code=503, detail="Orchestrator not valid")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get model info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/inference", response_model=BaseResponse[InferenceResponseDTO])
async def run_inference(
    request: InferenceRequest,
    api_key: str = Depends(verify_api_key)
):
    """Run AI inference."""
    try:
        logger.info(f"Inference request: task={request.task_type}, model={request.model}")
        
        if container.orchestrator:
            result = await container.orchestrator.run_inference(
                prompt=request.prompt,
                task_type=request.task_type,
                model=request.model,
                parameters=request.parameters.model_dump(),
                context=request.context
            )
            return BaseResponse(
                status=ResponseStatus.SUCCESS,
                code="INFERENCE_COMPLETED",
                message="AI inference completed",
                data=InferenceResponseDTO.model_validate(result)
            )
        raise HTTPException(status_code=503, detail="Orchestrator not ready")
    except Exception as e:
        logger.error(f"Inference failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/inference/stream")
async def run_inference_stream(
    request: InferenceRequest,
    api_key: str = Depends(verify_api_key)
):
    """Run streaming AI inference returned as server-sent events (SSE)."""
    
    async def generate():
        try:
            if container.orchestrator:
                async for chunk in container.orchestrator.run_inference_stream(
                    prompt=request.prompt,
                    task_type=request.task_type,
                    model=request.model,
                    parameters=request.parameters,
                    context=request.context
                ):
                    yield f"data: {chunk}\n\n"
            else:
                 yield f"data: {{\"error\": \"Orchestrator not ready\"}}\n\n"
        except Exception as e:
            logger.error(f"Streaming inference failed: {e}")
            yield f"data: {{\"error\": \"{str(e)}\"}}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")

@router.post("/models/{model_name}/load")
async def load_model(
    model_name: str,
    api_key: str = Depends(verify_api_key)
):
    """Manually load a specific model into memory."""
    try:
        if container.orchestrator:
            result = await container.orchestrator.load_model(model_name)
            return BaseResponse(
                status=ResponseStatus.SUCCESS,
                code="MODEL_LOADED",
                message=f"Model '{model_name}' loaded successfully",
                data={"model": model_name, "details": result}
            )
        raise HTTPException(status_code=503, detail="Orchestrator not ready")
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/models/{model_name}/unload")
async def unload_model(
    model_name: str,
    api_key: str = Depends(verify_api_key)
):
    """Unload a specific model from memory."""
    try:
        if container.orchestrator:
            result = await container.orchestrator.unload_model(model_name)
            return BaseResponse(
                status=ResponseStatus.SUCCESS,
                code="MODEL_UNLOADED",
                message=f"Model '{model_name}' unloaded successfully",
                data={"model": model_name, "details": result}
            )
        raise HTTPException(status_code=503, detail="Orchestrator not ready")
    except Exception as e:
        logger.error(f"Failed to unload model: {e}")
        raise HTTPException(status_code=500, detail=str(e))
@router.post("/generate", response_model=BaseResponse[SwarmResponseDTO])
async def generate_project(
    request: GenerationRequest,
    api_key: str = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate a full project or component using AI swarm.
    RBAC: Super Admin can generate for any user/tenant.
    Enterprise Admin can generate for their tenant users.
    Developers can only generate for themselves.
    """
    try:
        sm = get_security_manager()
        user_info = await sm.get_user_info(api_key, db)
        if not user_info:
            raise HTTPException(401, "Authentication required")
        
        role = user_info.get("role")
        current_user_id = user_info.get("user_id")
        tenant_id = user_info.get("tenant_id")
        
        # Determine target user for project creation
        # Default to current user, but Super Admin/Enterprise Admin can specify target
        target_user_id = current_user_id
        
        # If request includes a user_id (for admin/enterprise use)
        if hasattr(request, 'user_id') and request.user_id:
            if role == Role.ADMIN.value:
                # Super Admin can generate for any user
                target_user_id = request.user_id
            elif role == Role.ENTERPRISE.value:
                # Enterprise Admin can only generate for users in their tenant
                result = await db.execute(select(AuthUserModel).where(AuthUserModel.id == request.user_id))
                target_user = result.scalar_one_or_none()
                if not target_user or target_user.tenant_id != tenant_id:
                    raise HTTPException(403, "Cannot generate project for user outside your organization")
                target_user_id = request.user_id
            else:
                # Developers can only generate for themselves
                if request.user_id != current_user_id:
                    raise HTTPException(403, "Developers can only generate projects for themselves")
        
        if container.orchestrator and container.orchestrator.lead_architect:
            # Pass target user info to the generation context
            generation_context = {
                **request.model_dump(),
                "type": "full_project_generation",
                "user_id": target_user_id,
                "tenant_id": tenant_id,
                "requested_by": current_user_id,
                "requested_by_role": role
            }
            
            result = await container.orchestrator.lead_architect.act(
                f"Generate project: {request.project_name}",
                generation_context
            )
            return BaseResponse(
                status=ResponseStatus.SUCCESS,
                code="GENERATION_STARTED",
                message=f"Generation task for project '{request.project_name}' started for user {target_user_id}",
                data=SwarmResponseDTO.model_validate(result)
            )
        raise HTTPException(status_code=503, detail="Orchestrator not ready")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/migrate", response_model=BaseResponse[SwarmResponseDTO])
async def migrate_project(
    request: SwarmMigrationRequest,
    api_key: str = Depends(verify_api_key)
):
    """Migrate code or projects between stacks."""
    try:
        if container.orchestrator and container.orchestrator.lead_architect:
            result = await container.orchestrator.lead_architect.act(
                "Perform stack migration and logic healing.",
                {**request.model_dump(), "type": "migration"}
            )
            return BaseResponse(
                status=ResponseStatus.SUCCESS,
                code="MIGRATION_STARTED",
                message="Migration task initialized",
                data=SwarmResponseDTO.model_validate(result)
            )
        raise HTTPException(status_code=503, detail="Orchestrator not ready")
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/fix", response_model=BaseResponse[Dict[str, Any]])
async def fix_code(
    request: FixCodeRequest,
    api_key: str = Depends(verify_api_key)
):
    """Automatically fix code issues using AI Swarm."""
    try:
        if not container.ai_update_service:
            raise HTTPException(status_code=503, detail="AI Update Service not ready")
            
        result = await container.ai_update_service.fix_code(
            code=request.code,
            issue=request.issue,
            language=request.language
        )
        
        if result["success"]:
            return BaseResponse(
                status=ResponseStatus.SUCCESS,
                code="CODE_FIXED",
                message="Code fixed successfully",
                data=result
            )
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Fix failed"))
    except Exception as e:
        logger.error(f"Fix failed: {e}")
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze", response_model=BaseResponse[Dict[str, Any]])
async def analyze_code(
    request: AnalyzeCodeRequest,
    api_key: str = Depends(verify_api_key)
):
    """Analyze code quality and security using AI."""
    try:
        if not container.ai_update_service:
            raise HTTPException(status_code=503, detail="AI Update Service not ready")
            
        result = await container.ai_update_service.analyze_code(
            code=request.code,
            analysis_type=request.analysis_type,
            language=request.language
        )
        
        if result["success"]:
            return BaseResponse(
                status=ResponseStatus.SUCCESS,
                code="CODE_ANALYZED",
                message="Code analysis completed",
                data=result
            )
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Analysis failed"))
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test", response_model=BaseResponse[Dict[str, Any]])
async def generate_tests(
    request: TestCodeRequest,
    api_key: str = Depends(verify_api_key)
):
    """Generate tests for the provided code."""
    try:
        task = f"Generate {request.test_framework or ''} tests for this code:\n{request.code}"
        result = await container.orchestrator.universal_agent.act(task, {"type": "test_generation", "language": request.language})
        return BaseResponse(
            status=ResponseStatus.SUCCESS,
            code="TESTS_GENERATED",
            data={"result": result.get("solution")}
        )
    except Exception as e:
        logger.error(f"Test generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/optimize", response_model=BaseResponse[Dict[str, Any]])
async def optimize_code(
    request: OptimizeCodeRequest,
    api_key: str = Depends(verify_api_key)
):
    """Optimize code for performance or readability."""
    try:
        task = f"Optimize this code for {request.optimization_goal}:\n{request.code}"
        result = await container.orchestrator.universal_agent.act(task, {"type": "optimize", "language": request.language})
        return BaseResponse(
            status=ResponseStatus.SUCCESS,
            code="CODE_OPTIMIZED",
            data={"result": result.get("solution")}
        )
    except Exception as e:
        logger.error(f"Optimization failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/refactor", response_model=BaseResponse[Dict[str, Any]])
async def refactor_code(
    request: RefactorCodeRequest,
    api_key: str = Depends(verify_api_key)
):
    """Apply architectural or logic refactorings."""
    try:
        task = f"Refactor this code to achieve: {request.refactoring_goal}\nCode:\n{request.code}"
        result = await container.orchestrator.universal_agent.act(task, {"type": "refactor", "language": request.language})
        return BaseResponse(
            status=ResponseStatus.SUCCESS,
            code="CODE_REFACTORED",
            data={"result": result.get("solution")}
        )
    except Exception as e:
        logger.error(f"Refactor failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/explain", response_model=BaseResponse[Dict[str, Any]])
async def explain_code(
    request: ExplainCodeRequest,
    api_key: str = Depends(verify_api_key)
):
    """Explain code logic using open-source models."""
    try:
        if not container.ai_update_service:
            raise HTTPException(status_code=503, detail="AI Update Service not ready")
            
        result = await container.ai_update_service.explain_code(
            code=request.code,
            language=request.language
        )
        
        if result["success"]:
            return BaseResponse(
                status=ResponseStatus.SUCCESS,
                code="CODE_EXPLAINED",
                message="Code explanation generated",
                data=result
            )
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Explanation failed"))
    except Exception as e:
        logger.error(f"Explanation failed: {e}")
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail=str(e))
