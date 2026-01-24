"""
System Controller
Handles system-level endpoints like health checks, status, and root.
"""
from typing import Dict
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from core.security import verify_api_key
from core.container import container
from dto.common.base_response import BaseResponse
from dto.v1.responses.system import HealthResponseDTO, SystemStatusDTO
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["System"])

@router.get("/", response_model=BaseResponse[Dict[str, Any]])
async def root():
    """Root endpoint to verify service is running."""
    return BaseResponse(
        status="success",
        code="SYSTEM_ONLINE",
        message="Service is online and ready",
        data={
            "service": "AI Orchestrator",
            "version": "1.0.0",
            "status": "running"
        }
    )

@router.get("/health", response_model=BaseResponse[HealthResponseDTO])
async def health_check():
    """Check the health status of the orchestrator and runtimes."""
    try:
        # Access orchestrator via container
        if container.orchestrator:
             status = await container.orchestrator.get_health_status()
             return BaseResponse(
                 status="success",
                 code="HEALTH_CHECK_OK",
                 message="System health status retrieved",
                 data=HealthResponseDTO.model_validate(status)
             )
        return BaseResponse(
            status="warning",
            code="SYSTEM_INITIALIZING",
            message="Orchestrator is initializing",
            data={"components": {}, "memory_usage": {}}
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status", response_model=BaseResponse[SystemStatusDTO])
async def system_status(api_key: str = Depends(verify_api_key)):
    """Get detailed system metrics, resource usage, and loaded models."""
    try:
        if container.orchestrator:
            status = await container.orchestrator.get_system_status()
            return BaseResponse(
                status="success",
                code="SYSTEM_STATUS_RETRIEVED",
                message="System status and metrics retrieved",
                data=SystemStatusDTO.model_validate(status)
            )
        raise HTTPException(status_code=503, detail="Orchestrator not ready")
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
