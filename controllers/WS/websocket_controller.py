"""
WebSocket Controller
Handles real-time WebSocket connections for terminals, monitoring, and collaboration.
"""
from fastapi import APIRouter, WebSocket
from core.container import container
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["WebSocket"])

@router.websocket("/ide/terminal/{session_id}")
async def terminal_websocket(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for terminal"""
    await websocket.accept()
    if container.terminal_service:
        await container.terminal_service.handle_websocket(websocket, session_id)
    else:
        await websocket.close(code=1000, reason="Terminal service unavailable")

@router.websocket("/monitoring/stream")
async def monitoring_stream(websocket: WebSocket):
    """WebSocket endpoint for real-time metrics streaming"""
    await websocket.accept()
    
    try:
        from services.monitoring import RealtimeMonitoringService
        monitoring = RealtimeMonitoringService()
        await monitoring.register_websocket(websocket)
        
        while True:
            await websocket.receive_text()  # Keep connection alive
    except Exception:
        pass
    finally:
        # monitoring.unregister_websocket(websocket) # Should be implemented in service
        pass

@router.websocket("/collaboration/{session_id}")
async def collaboration_websocket(
    websocket: WebSocket,
    session_id: str,
    user_id: str,
    username: str
):
    """WebSocket endpoint for collaboration"""
    await websocket.accept()
    
    try:
        from services.collaboration import CollaborationService
        collaboration = CollaborationService()
        await collaboration.handle_websocket(websocket, session_id, user_id, username)
    except Exception as e:
        logger.error(f"Collaboration WS error: {e}")
        await websocket.close()
