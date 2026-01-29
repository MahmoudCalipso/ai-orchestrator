"""
Emulator Controller - Manages mobile emulator lifecycle
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
from services.mobile.mobile_service import mobile_service
from core.security import verify_api_key
from dto.common.base_response import BaseResponse

router = APIRouter(prefix="/emulator", tags=["Mobile Emulator"])

@router.post("/start")
async def start_emulator(request: Dict[str, Any], api_key: str = Depends(verify_api_key)):
    """Start a mobile emulator"""
    project_id = request.get("project_id")
    if not project_id:
        raise HTTPException(400, "project_id is required")
        
    device_profile = request.get("device_profile", "Pixel_7_Pro")
    result = await mobile_service.start_emulator(project_id, device_profile)
    return BaseResponse(
        status="success",
        code="EMULATOR_STARTED",
        message=f"Emulator '{device_profile}' for project '{project_id}' started",
        data=result
    )

@router.post("/stop")
async def stop_emulator(request: Dict[str, Any], api_key: str = Depends(verify_api_key)):
    """Stop a mobile emulator"""
    emulator_id = request.get("emulator_id")
    if not emulator_id:
        raise HTTPException(400, "emulator_id is required")
        
    success = await mobile_service.stop_emulator(emulator_id)
    if not success:
        raise HTTPException(404, "Emulator not found")
        
    return BaseResponse(
        status="success",
        code="EMULATOR_STOPPED",
        message=f"Emulator '{emulator_id}' stopped successfully",
        data={"emulator_id": emulator_id}
    )

@router.get("/active", response_model=BaseResponse[List[Dict[str, Any]]])
async def list_active_emulators(api_key: str = Depends(verify_api_key)):
    """List all active emulators"""
    result = await mobile_service.list_active()
    return BaseResponse(
        status="success",
        code="ACTIVE_EMULATORS_RETRIEVED",
        data=result
    )

