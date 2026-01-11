"""
WebSocket Gateway for Live Console
Bridges browser terminal to Docker containers
"""
import logging
from typing import Dict
from fastapi import WebSocket, WebSocketDisconnect
import json

logger = logging.getLogger(__name__)

class ConsoleSession:
    """Represents a live console session"""
    
    def __init__(self, session_id: str, workbench_id: str, websocket: WebSocket):
        self.session_id = session_id
        self.workbench_id = workbench_id
        self.websocket = websocket
        self.active = True
    
    async def send(self, data: str):
        """Send data to browser"""
        if self.active:
            await self.websocket.send_text(data)
    
    async def receive(self) -> str:
        """Receive data from browser"""
        return await self.websocket.receive_text()

class WebSocketGateway:
    """Manages WebSocket connections for live console"""
    
    def __init__(self, workbench_manager):
        self.workbench_manager = workbench_manager
        self.sessions: Dict[str, ConsoleSession] = {}
    
    async def handle_connection(
        self,
        websocket: WebSocket,
        session_id: str,
        workbench_id: str
    ):
        """Handle a new WebSocket connection"""
        await websocket.accept()
        
        session = ConsoleSession(session_id, workbench_id, websocket)
        self.sessions[session_id] = session
        
        logger.info(f"Console session {session_id} connected to workbench {workbench_id}")
        
        try:
            # Start bidirectional streaming
            await self._stream_console(session)
        except WebSocketDisconnect:
            logger.info(f"Console session {session_id} disconnected")
        except Exception as e:
            logger.error(f"Console session error: {e}")
        finally:
            session.active = False
            del self.sessions[session_id]
    
    async def _stream_console(self, session: ConsoleSession):
        """Stream console I/O between browser and container"""
        while session.active:
            try:
                # Receive command from browser
                data = await session.receive()
                command_data = json.loads(data)
                
                if command_data.get("type") == "command":
                    command = command_data.get("command")
                    
                    # Execute in workbench
                    result = await self.workbench_manager.execute_in_workbench(
                        session.workbench_id,
                        command
                    )
                    
                    # Send output back to browser
                    await session.send(json.dumps({
                        "type": "output",
                        "stdout": result.get("stdout", ""),
                        "stderr": result.get("stderr", ""),
                        "exit_code": result.get("exit_code", 0)
                    }))
                    
            except Exception as e:
                logger.error(f"Stream error: {e}")
                break
