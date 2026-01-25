"""
Debugger Service - Debugging support for browser IDE
Implements a bridge to various debuggers using localized DAP-like interfaces
"""

import asyncio
import os
import json
import logging
import uuid
from typing import Dict, Any, List, Optional
from fastapi import WebSocket

logger = logging.getLogger(__name__)


class Breakpoint:
    """Represents a breakpoint"""
    def __init__(self, file_path: str, line: int, condition: Optional[str] = None):
        self.id = str(uuid.uuid4())
        self.file_path = file_path
        self.line = line
        self.condition = condition
        self.verified = False
        self.enabled = True

    def to_dict(self):
        return {
            "id": self.id,
            "path": self.file_path,
            "line": self.line,
            "verified": self.verified,
            "enabled": self.enabled,
            "condition": self.condition
        }


class DebugSession:
    """Represents a live debug session"""
    
    def __init__(self, session_id: str, workspace_id: str, language: str):
        self.id = session_id
        self.workspace_id = workspace_id
        self.language = language
        self.process = None
        self.breakpoints: List[Breakpoint] = []
        self.state = "inactive"  # inactive, starting, running, paused, terminated
        self.websocket: Optional[WebSocket] = None
        self.debug_port = 0
    
    async def start(self, entry_point: str, args: List[str] = None):
        """Start the application in debug mode"""
        self.state = "starting"
        # Implementation depends heavily on language
        if self.language == "python":
            await self._start_python(entry_point, args)
        elif self.language in ["javascript", "typescript"]:
            await self._start_node(entry_point, args)
        else:
            raise ValueError(f"Debugging not supported for {self.language}")
    
    async def _start_python(self, entry_point: str, args: List[str]):
        """Start Python debugger (debugpy)"""
        import socket
        # Find a free port
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('', 0))
        self.debug_port = s.getsockname()[1]
        s.close()
        
        cmd = [
            "python", "-m", "debugpy", 
            "--listen", f"127.0.0.1:{self.debug_port}",
            "--wait-for-client",
            entry_point
        ]
        if args:
            cmd.extend(args)
            
        self.process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=f"storage/workspaces/{self.workspace_id}"
        )
        self.state = "running"
        logger.info(f"Python debugger started on port {self.debug_port}")

    async def _start_node(self, entry_point: str, args: List[str]):
        """Start Node.js debugger (--inspect)"""
        # Node defaults to 9229
        self.debug_port = 9229 
        cmd = ["node", "--inspect=127.0.0.1:0", entry_point]
        if args:
            cmd.extend(args)
            
        self.process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=f"storage/workspaces/{self.workspace_id}"
        )
        # We need to parse the port from stderr for Node's random port
        self.state = "running"

    async def stop(self):
        """Stop debug session"""
        self.state = "terminated"
        if self.process:
            try:
                self.process.terminate()
                await self.process.wait()
            except:
                pass
        self.process = None


class DebuggerService:
    """Debugger service for browser IDE"""
    
    def __init__(self):
        self.sessions: Dict[str, DebugSession] = {}
    
    async def create_session(
        self, 
        workspace_id: str, 
        language: str, 
        entry_point: str,
        args: List[str] = None
    ) -> str:
        """Create and start a new debug session"""
        session_id = str(uuid.uuid4())
        session = DebugSession(session_id, workspace_id, language)
        await session.start(entry_point, args)
        self.sessions[session_id] = session
        return session_id
    
    async def stop_session(self, session_id: str):
        """Stop a debug session"""
        session = self.sessions.get(session_id)
        if session:
            await session.stop()
            del self.sessions[session_id]
            
    async def handle_dap_message(self, session_id: str, message: Dict[str, Any]):
        """
        Handle Debug Adapter Protocol message
        In a real implementation, this would proxy to the actual debugger
        """
        session = self.sessions.get(session_id)
        if not session:
            return {"error": "Session not found"}
            
        command = message.get("command")
        
        if command == "setBreakpoints":
            return await self._handle_set_breakpoints(session, message.get("arguments", {}))
        elif command in ["continue", "next", "stepIn", "stepOut", "pause", "stackTrace", "scopes", "variables"]:
            # These require deeper implementation of the specific debugger bridge.
            # For now, we return a more structural response to avoid crashes.
            logger.info(f"DAP Command {command} received but not fully implemented for {session.language}")
            return {
                "success": False, 
                "message": f"Command '{command}' is currently in technical preview and not fully implemented.",
                "command": command
            }
            
        return {"error": f"Command '{command}' not supported"}

    async def _handle_set_breakpoints(self, session: DebugSession, args: Dict[str, Any]):
        """Set breakpoints for a file"""
        path = args.get("source", {}).get("path")
        lines = args.get("breakpoints", [])
        
        # Clear existing breakpoints for this path
        session.breakpoints = [bp for bp in session.breakpoints if bp.file_path != path]
        
        # Add new breakpoints
        new_bps = []
        for bp_data in lines:
            bp = Breakpoint(path, bp_data.get("line"))
            bp.verified = True # Simulate verification
            session.breakpoints.append(bp)
            new_bps.append(bp.to_dict())
            
        return {"breakpoints": new_bps}

    async def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """Get status of a debug session"""
        session = self.sessions.get(session_id)
        if not session:
            return {"status": "not_found"}
            
        return {
            "session_id": session.id,
            "workspace_id": session.workspace_id,
            "language": session.language,
            "state": session.state,
            "port": session.debug_port,
            "breakpoints_count": len(session.breakpoints)
        }
