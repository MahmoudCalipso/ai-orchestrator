"""
Emulator Controller - Manages mobile emulator lifecycle
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
from services.mobile.mobile_service import mobile_service
from core.security import verify_api_key
from dto.v1.base import BaseResponse, ResponseStatus
from dto.v1.requests.supplemental import EmulatorStartRequest
from dto.v1.responses.supplemental import EmulatorResponseDTO

router = APIRouter(prefix="/emulator", tags=["Mobile Emulator"])

@router.post("/start", response_model=BaseResponse[EmulatorResponseDTO])
async def start_emulator(request: EmulatorStartRequest, api_key: str = Depends(verify_api_key)):
    """Start a mobile emulator"""
    result = await mobile_service.start_emulator(request.project_id, request.device_profile)
    return BaseResponse(
        status=ResponseStatus.SUCCESS,
        code="EMULATOR_STARTED",
        message=f"Emulator '{request.device_profile}' for project '{request.project_id}' started",
        data=EmulatorResponseDTO(
            id=result.get("id"),
            device=request.device_profile,
            status="starting",
            port=result.get("port")
        )
    )

@router.post("/stop", response_model=BaseResponse[Dict[str, Any]])
async def stop_emulator(request: Dict[str, Any], api_key: str = Depends(verify_api_key)):
    """Stop a mobile emulator"""
    emulator_id = request.get("emulator_id")
    if not emulator_id:
        raise HTTPException(400, "emulator_id is required")
        
    success = await mobile_service.stop_emulator(emulator_id)
    if not success:
        raise HTTPException(404, "Emulator not found")
        
    return BaseResponse(
        status=ResponseStatus.SUCCESS,
        code="EMULATOR_STOPPED",
        message=f"Emulator '{emulator_id}' stopped successfully",
        data={"emulator_id": emulator_id}
    )

@router.get("/active", response_model=BaseResponse[List[EmulatorResponseDTO]])
async def list_active_emulators(api_key: str = Depends(verify_api_key)):
    """List all active emulators"""
    result = await mobile_service.list_active()
    return BaseResponse(
        status=ResponseStatus.SUCCESS,
        code="ACTIVE_EMULATORS_RETRIEVED",
        data=[EmulatorResponseDTO(
            id=e.get("id"),
            device=e.get("device"),
            status=e.get("status"),
            port=e.get("port")
        ) for e in result]
    )

