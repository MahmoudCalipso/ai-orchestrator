"""
AI Controller
Handles AI inference, model management, and streaming generation.
"""
from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from core.security import verify_api_key
from core.container import container
from schemas.api_spec import (
    InferenceRequest, InferenceResponse, ModelInfo,
    FixCodeRequest, AnalyzeCodeRequest, TestCodeRequest,
    OptimizeCodeRequest, DocumentCodeRequest, ReviewCodeRequest,
    ExplainCodeRequest, RefactorCodeRequest, SwarmResponse,
    StandardResponse
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["AI"])

@router.get("/models")
async def list_models(
    page: int = 1,
    page_size: int = 20,
    api_key: str = Depends(verify_api_key)
):
    """List all available AI models supported by the system with pagination."""
    try:
        if container.orchestrator:
             models = await container.orchestrator.list_available_models()
             model_infos = [ModelInfo(**model) for model in models]
             
             total = len(model_infos)
             start = (page - 1) * page_size
             end = start + page_size
             paginated_models = model_infos[start:end]
             
             return {
                 "models": paginated_models,
                 "pagination": {
                     "page": page,
                     "page_size": page_size,
                     "total": total,
                     "total_pages": (total + page_size - 1) // page_size
                 }
             }
        return {"models": [], "pagination": {"page": page, "page_size": page_size, "total": 0, "total_pages": 0}}
    except Exception as e:
        logger.error(f"Failed to list models: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/models/{model_name}", response_model=ModelInfo)
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
            return ModelInfo(**model_info)
        raise HTTPException(status_code=503, detail="Orchestrator not valid")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get model info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/inference", response_model=InferenceResponse)
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
                parameters=request.parameters,
                context=request.context
            )
            return InferenceResponse(**result)
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
            return {"status": "success", "model": model_name, "details": result}
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
            return {"status": "success", "model": model_name, "details": result}
        raise HTTPException(status_code=503, detail="Orchestrator not ready")
    except Exception as e:
        logger.error(f"Failed to unload model: {e}")
        raise HTTPException(status_code=500, detail=str(e))
@router.post("/api/generate", response_model=SwarmResponse)
async def generate_project(
    request: Dict[str, Any],
    api_key: str = Depends(verify_api_key)
):
    """Generate a full project or component using AI swarm."""
    try:
        if container.orchestrator and container.orchestrator.lead_architect:
            result = await container.orchestrator.lead_architect.act(
                f"Generate project: {request.get('project_name')}",
                {**request, "type": "full_project_generation"}
            )
            return SwarmResponse(**result)
        raise HTTPException(status_code=503, detail="Orchestrator not ready")
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/migrate", response_model=SwarmResponse)
async def migrate_project(
    request: Dict[str, Any],
    api_key: str = Depends(verify_api_key)
):
    """Migrate code or projects between stacks."""
    try:
        if container.orchestrator and container.orchestrator.lead_architect:
            result = await container.orchestrator.lead_architect.act(
                "Perform stack migration and logic healing.",
                {**request, "type": "migration"}
            )
            return SwarmResponse(**result)
        raise HTTPException(status_code=503, detail="Orchestrator not ready")
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/fix", response_model=StandardResponse)
async def fix_code(
    request: FixCodeRequest,
    api_key: str = Depends(verify_api_key)
):
    """Automatically fix code issues."""
    try:
        task = f"Fix the following issue: {request.issue}\nCode:\n{request.code}"
        result = await container.orchestrator.universal_agent.act(task, {"type": "fix", "language": request.language})
        return StandardResponse(status="success", result=result.get("solution"))
    except Exception as e:
        logger.error(f"Fix failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/analyze", response_model=StandardResponse)
async def analyze_code(
    request: AnalyzeCodeRequest,
    api_key: str = Depends(verify_api_key)
):
    """Analyze code quality and security."""
    try:
        task = f"Perform {request.analysis_type} analysis on this code:\n{request.code}"
        result = await container.orchestrator.universal_agent.act(task, {"type": "analyze", "language": request.language})
        return StandardResponse(status="success", result=result.get("solution"))
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/test", response_model=StandardResponse)
async def generate_tests(
    request: TestCodeRequest,
    api_key: str = Depends(verify_api_key)
):
    """Generate tests for the provided code."""
    try:
        task = f"Generate {request.test_framework or ''} tests for this code:\n{request.code}"
        result = await container.orchestrator.universal_agent.act(task, {"type": "test_generation", "language": request.language})
        return StandardResponse(status="success", result=result.get("solution"))
    except Exception as e:
        logger.error(f"Test generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/optimize", response_model=StandardResponse)
async def optimize_code(
    request: OptimizeCodeRequest,
    api_key: str = Depends(verify_api_key)
):
    """Optimize code for performance or readability."""
    try:
        task = f"Optimize this code for {request.optimization_goal}:\n{request.code}"
        result = await container.orchestrator.universal_agent.act(task, {"type": "optimize", "language": request.language})
        return StandardResponse(status="success", result=result.get("solution"))
    except Exception as e:
        logger.error(f"Optimization failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/refactor", response_model=StandardResponse)
async def refactor_code(
    request: RefactorCodeRequest,
    api_key: str = Depends(verify_api_key)
):
    """Apply architectural or logic refactorings."""
    try:
        task = f"Refactor this code to achieve: {request.refactoring_goal}\nCode:\n{request.code}"
        result = await container.orchestrator.universal_agent.act(task, {"type": "refactor", "language": request.language})
        return StandardResponse(status="success", result=result.get("solution"))
    except Exception as e:
        logger.error(f"Refactor failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/explain", response_model=StandardResponse)
async def explain_code(
    request: ExplainCodeRequest,
    api_key: str = Depends(verify_api_key)
):
    """Explain code logic in natural language."""
    try:
        task = f"Explain the logic of this code in detail:\n{request.code}"
        result = await container.orchestrator.universal_agent.act(task, {"type": "explain", "language": request.language})
        return StandardResponse(status="success", result=result.get("solution"))
    except Exception as e:
        logger.error(f"Explanation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
