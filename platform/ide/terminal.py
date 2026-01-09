"""
Terminal Service - Integrated terminal for browser IDE
Provides PTY management and command execution in Docker containers
"""
import asyncio
import os
import pty
import struct
import fcntl
import termios
from typing import Dict, Any, Optional
from fastapi import WebSocket
import uuid


class TerminalSession:
    """Represents a terminal session"""
    
    def __init__(self, session_id: str, workspace_id: str):
        self.session_id = session_id
        self.workspace_id = workspace_id
        self.process: Optional[asyncio.subprocess.Process] = None
        self.master_fd: Optional[int] = None
        self.websocket: Optional[WebSocket] = None
        self.running = False
    
    async def start(self, shell: str = "/bin/bash", cwd: Optional[str] = None):
        """Start terminal session"""
        # Create PTY
        self.master_fd, slave_fd = pty.openpty()
        
        # Set terminal size
        self._set_terminal_size(80, 24)
        
        # Start shell process
        self.process = await asyncio.create_subprocess_exec(
            shell,
            stdin=slave_fd,
            stdout=slave_fd,
            stderr=slave_fd,
            cwd=cwd or f"./workspaces/{self.workspace_id}",
            env=os.environ.copy()
        )
        
        self.running = True
        os.close(slave_fd)
    
    def _set_terminal_size(self, cols: int, rows: int):
        """Set terminal window size"""
        if self.master_fd:
            size = struct.pack("HHHH", rows, cols, 0, 0)
            fcntl.ioctl(self.master_fd, termios.TIOCSWINSZ, size)
    
    async def write(self, data: str):
        """Write data to terminal"""
        if self.master_fd and self.running:
            os.write(self.master_fd, data.encode('utf-8'))
    
    async def read(self) -> bytes:
        """Read data from terminal"""
        if self.master_fd and self.running:
            try:
                return os.read(self.master_fd, 1024)
            except OSError:
                return b''
        return b''
    
    async def resize(self, cols: int, rows: int):
        """Resize terminal"""
        self._set_terminal_size(cols, rows)
    
    async def stop(self):
        """Stop terminal session"""
        self.running = False
        if self.process:
            self.process.terminate()
            await self.process.wait()
        if self.master_fd:
            os.close(self.master_fd)


class TerminalService:
    """Terminal service for browser IDE"""
    
    def __init__(self):
        self.sessions: Dict[str, TerminalSession] = {}
    
    async def create_session(self, workspace_id: str, shell: str = "/bin/bash") -> str:
        """Create new terminal session"""
        session_id = str(uuid.uuid4())
        session = TerminalSession(session_id, workspace_id)
        await session.start(shell)
        self.sessions[session_id] = session
        return session_id
    
    async def get_session(self, session_id: str) -> Optional[TerminalSession]:
        """Get terminal session"""
        return self.sessions.get(session_id)
    
    async def close_session(self, session_id: str):
        """Close terminal session"""
        session = self.sessions.get(session_id)
        if session:
            await session.stop()
            del self.sessions[session_id]
    
    async def handle_websocket(self, websocket: WebSocket, session_id: str):
        """Handle WebSocket connection for terminal"""
        session = self.sessions.get(session_id)
        if not session:
            await websocket.close(code=1008, reason="Session not found")
            return
        
        session.websocket = websocket
        
        # Create tasks for reading and writing
        read_task = asyncio.create_task(self._read_from_terminal(session, websocket))
        write_task = asyncio.create_task(self._write_to_terminal(session, websocket))
        
        try:
            await asyncio.gather(read_task, write_task)
        except Exception as e:
            print(f"Terminal WebSocket error: {e}")
        finally:
            read_task.cancel()
            write_task.cancel()
    
    async def _read_from_terminal(self, session: TerminalSession, websocket: WebSocket):
        """Read from terminal and send to WebSocket"""
        while session.running:
            try:
                data = await session.read()
                if data:
                    await websocket.send_text(data.decode('utf-8', errors='ignore'))
                await asyncio.sleep(0.01)  # Small delay to prevent busy loop
            except Exception as e:
                print(f"Error reading from terminal: {e}")
                break
    
    async def _write_to_terminal(self, session: TerminalSession, websocket: WebSocket):
        """Receive from WebSocket and write to terminal"""
        while session.running:
            try:
                data = await websocket.receive_text()
                
                # Handle special commands
                if data.startswith('\x1b['):  # Escape sequence
                    # Handle resize command
                    if 'resize' in data:
                        # Parse resize command
                        pass
                
                await session.write(data)
            except Exception as e:
                print(f"Error writing to terminal: {e}")
                break
    
    async def execute_command(
        self,
        workspace_id: str,
        command: str,
        cwd: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute a single command and return output"""
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=cwd or f"./workspaces/{workspace_id}"
        )
        
        stdout, stderr = await process.communicate()
        
        return {
            "command": command,
            "exit_code": process.returncode,
            "stdout": stdout.decode('utf-8', errors='ignore'),
            "stderr": stderr.decode('utf-8', errors='ignore')
        }
    
    async def list_sessions(self, workspace_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List active terminal sessions"""
        sessions = []
        for session_id, session in self.sessions.items():
            if workspace_id is None or session.workspace_id == workspace_id:
                sessions.append({
                    "session_id": session_id,
                    "workspace_id": session.workspace_id,
                    "running": session.running
                })
        return sessions


class DockerTerminalService(TerminalService):
    """Terminal service that runs in Docker containers"""
    
    async def create_session(
        self,
        workspace_id: str,
        container_image: str = "python:3.12-slim"
    ) -> str:
        """Create terminal session in Docker container"""
        import docker
        
        session_id = str(uuid.uuid4())
        
        # Create Docker client
        client = docker.from_env()
        
        # Create container
        container = client.containers.run(
            container_image,
            command="/bin/bash",
            detach=True,
            tty=True,
            stdin_open=True,
            volumes={
                f"./workspaces/{workspace_id}": {
                    "bind": "/workspace",
                    "mode": "rw"
                }
            },
            working_dir="/workspace"
        )
        
        # Create session
        session = TerminalSession(session_id, workspace_id)
        session.container = container
        session.running = True
        
        self.sessions[session_id] = session
        return session_id
    
    async def execute_in_container(
        self,
        session_id: str,
        command: str
    ) -> Dict[str, Any]:
        """Execute command in Docker container"""
        session = self.sessions.get(session_id)
        if not session or not hasattr(session, 'container'):
            raise ValueError("Invalid session or container not found")
        
        exec_result = session.container.exec_run(command)
        
        return {
            "command": command,
            "exit_code": exec_result.exit_code,
            "output": exec_result.output.decode('utf-8', errors='ignore')
        }
