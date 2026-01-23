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
        if not container.monitoring_service:
            await websocket.close(code=1011, reason="Monitoring service ready")
            return
            
        await container.monitoring_service.register_websocket(websocket)
        
        while True:
            await websocket.receive_text()  # Keep connection alive
    except Exception:
        pass
    finally:
        if container.monitoring_service:
            await container.monitoring_service.unregister_websocket(websocket)

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
        if not container.collaboration_service:
            await websocket.close(code=1011, reason="Collaboration service not ready")
            return
            
        await container.collaboration_service.handle_websocket(websocket, session_id, user_id, username)
    except Exception as e:
        logger.error(f"Collaboration WS error: {e}")
        await websocket.close()
