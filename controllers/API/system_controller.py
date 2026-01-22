"""
System Controller
Handles system-level endpoints like health checks, status, and root.
"""
from typing import Dict
from fastapi import APIRouter, HTTPException, Depends
from core.security import verify_api_key
from core.container import container
from schemas.spec import HealthResponse, SystemStatus
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["System"])

@router.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint to verify service is running."""
    return {
        "service": "AI Orchestrator",
        "version": "1.0.0",
        "status": "running"
    }

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Check the health status of the orchestrator and runtimes."""
    try:
        # Access orchestrator via container
        if container.orchestrator:
             status = await container.orchestrator.get_health_status()
             return HealthResponse(**status)
        return HealthResponse(status="starting", components={}, memory_usage={})
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status", response_model=SystemStatus)
async def system_status(api_key: str = Depends(verify_api_key)):
    """Get detailed system metrics, resource usage, and loaded models."""
    try:
        if container.orchestrator:
            status = await container.orchestrator.get_system_status()
            return SystemStatus(**status)
        raise HTTPException(status_code=503, detail="Orchestrator not ready")
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
