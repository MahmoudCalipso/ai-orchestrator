"""
Monitoring Controller
Handles system metrics and build monitoring.
"""
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from core.security import verify_api_key
from core.container import container
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Monitoring"])

@router.get("/monitoring/metrics")
async def get_monitoring_metrics(
    limit: int = 100,
    api_key: str = Depends(verify_api_key)
):
    """Get monitoring metrics"""
    try:
        if not container.monitoring_service:
            raise HTTPException(status_code=503, detail="Monitoring service not ready")
        metrics = container.monitoring_service.get_metrics(limit)
        return {"metrics": metrics}
    except Exception as e:
        logger.error(f"Failed to get metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/monitoring/metrics/current")
async def get_current_metrics(api_key: str = Depends(verify_api_key)):
    """Get current system metrics"""
    try:
        if not container.monitoring_service:
             raise HTTPException(status_code=503, detail="Monitoring service not ready")
        metrics = container.monitoring_service.get_current_metrics()
        return metrics or {}
    except Exception as e:
        logger.error(f"Failed to get current metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/monitoring/builds")
async def list_builds(
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    api_key: str = Depends(verify_api_key)
):
    """List build progress with pagination"""
    try:
        if not container.monitoring_service:
             raise HTTPException(status_code=503, detail="Monitoring service not ready")
        result = container.monitoring_service.list_builds(status, page, page_size)
        return {
            "builds": [b.to_dict() for b in result["builds"]],
            "pagination": {
                "page": result["page"],
                "page_size": result["page_size"],
                "total": result["total"],
                "total_pages": result["total_pages"]
            }
        }
    except Exception as e:
        logger.error(f"Failed to list builds: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/monitoring/builds/{build_id}")
async def get_build(
    build_id: str,
    api_key: str = Depends(verify_api_key)
):
    """Get build progress"""
    try:
        if not container.monitoring_service:
             raise HTTPException(status_code=503, detail="Monitoring service not ready")
        build = container.monitoring_service.get_build(build_id)
        if not build:
            raise HTTPException(status_code=404, detail="Build not found")
        return build.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get build: {e}")
        raise HTTPException(status_code=500, detail=str(e))
