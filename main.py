"""
AI Orchestrator - Main Entry Point
"""
import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from core.orchestrator import Orchestrator
from core.registry import ModelRegistry
from core.security import SecurityManager, verify_api_key
from schemas.spec import (
    InferenceRequest,
    InferenceResponse,
    ModelInfo,
    HealthResponse,
    SystemStatus
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global orchestrator instance
orchestrator: Orchestrator = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle management for the application"""
    global orchestrator
    
    # Startup
    logger.info("Starting AI Orchestrator...")
    orchestrator = Orchestrator()
    await orchestrator.initialize()
    logger.info("AI Orchestrator initialized successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down AI Orchestrator...")
    await orchestrator.shutdown()
    logger.info("AI Orchestrator shut down successfully")


# Create FastAPI app
app = FastAPI(
    title="AI Orchestrator",
    description="Advanced AI Model Orchestration System",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint"""
    return {
        "service": "AI Orchestrator",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        status = await orchestrator.get_health_status()
        return HealthResponse(**status)
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/status", response_model=SystemStatus)
async def system_status(api_key: str = Depends(verify_api_key)):
    """Get detailed system status"""
    try:
        status = await orchestrator.get_system_status()
        return SystemStatus(**status)
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/models", response_model=list[ModelInfo])
async def list_models(api_key: str = Depends(verify_api_key)):
    """List all available models"""
    try:
        models = await orchestrator.list_available_models()
        return [ModelInfo(**model) for model in models]
    except Exception as e:
        logger.error(f"Failed to list models: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/models/{model_name}", response_model=ModelInfo)
async def get_model_info(
    model_name: str,
    api_key: str = Depends(verify_api_key)
):
    """Get information about a specific model"""
    try:
        model_info = await orchestrator.get_model_info(model_name)
        if not model_info:
            raise HTTPException(status_code=404, detail="Model not found")
        return ModelInfo(**model_info)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get model info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/inference", response_model=InferenceResponse)
async def run_inference(
    request: InferenceRequest,
    api_key: str = Depends(verify_api_key)
):
    """Run inference with automatic model selection and routing"""
    try:
        logger.info(f"Inference request: task={request.task_type}, model={request.model}")
        
        result = await orchestrator.run_inference(
            prompt=request.prompt,
            task_type=request.task_type,
            model=request.model,
            parameters=request.parameters,
            context=request.context
        )
        
        return InferenceResponse(**result)
    
    except Exception as e:
        logger.error(f"Inference failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/inference/stream")
async def run_inference_stream(
    request: InferenceRequest,
    api_key: str = Depends(verify_api_key)
):
    """Run streaming inference"""
    from fastapi.responses import StreamingResponse
    
    async def generate():
        try:
            async for chunk in orchestrator.run_inference_stream(
                prompt=request.prompt,
                task_type=request.task_type,
                model=request.model,
                parameters=request.parameters,
                context=request.context
            ):
                yield f"data: {chunk}\n\n"
        except Exception as e:
            logger.error(f"Streaming inference failed: {e}")
            yield f"data: {{\"error\": \"{str(e)}\"}}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")


@app.post("/models/{model_name}/load")
async def load_model(
    model_name: str,
    api_key: str = Depends(verify_api_key)
):
    """Load a specific model"""
    try:
        result = await orchestrator.load_model(model_name)
        return {"status": "success", "model": model_name, "details": result}
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/models/{model_name}/unload")
async def unload_model(
    model_name: str,
    api_key: str = Depends(verify_api_key)
):
    """Unload a specific model"""
    try:
        result = await orchestrator.unload_model(model_name)
        return {"status": "success", "model": model_name, "details": result}
    except Exception as e:
        logger.error(f"Failed to unload model: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/migrate")
async def migrate_task(
    request: Dict[str, Any],
    api_key: str = Depends(verify_api_key)
):
    """Migrate a running task to a different model/runtime"""
    try:
        result = await orchestrator.migrate_task(
            task_id=request.get("task_id"),
            target_model=request.get("target_model"),
            target_runtime=request.get("target_runtime")
        )
        return {"status": "success", "migration": result}
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/metrics")
async def get_metrics(api_key: str = Depends(verify_api_key)):
    """Get system metrics"""
    try:
        metrics = await orchestrator.get_metrics()
        return metrics
    except Exception as e:
        logger.error(f"Failed to get metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="AI Orchestrator")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8080, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    parser.add_argument("--workers", type=int, default=1, help="Number of workers")
    
    args = parser.parse_args()
    
    uvicorn.run(
        "main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        workers=args.workers,
        log_level="info"
    )


if __name__ == "__main__":
    main()