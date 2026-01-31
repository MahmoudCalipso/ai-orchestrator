import logging
import asyncio
import os
import signal
import json
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class RuntimeService:
    """Handles running applications using local processes or Docker sandboxes asynchronously"""
    
    def __init__(self):
        self.active_processes: Dict[str, Dict[str, Any]] = {}
        from services.workspace.docker_sandbox import DockerSandboxService
        self.sandbox_service = DockerSandboxService()
        self.active_sandboxes: Dict[str, Dict[str, Any]] = {}
        
    async def start_project(
        self,
        project_id: str,
        local_path: str,
        port: int = 8000,
        env_vars: Optional[Dict[str, str]] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Run a project application in a sandbox or locally asynchronously"""
        if project_id in self.active_sandboxes or project_id in self.active_processes:
            return {"success": False, "error": "Project is already running"}
            
        logger.info(f"Starting project {project_id} at {local_path}")
        
        full_config = config or {}
        if env_vars:
            full_config["env"] = env_vars
        full_config["port"] = port
        
        # 1. Detect tech stack
        stack = full_config.get("stack", "node")
        
        try:
            # 2. Try sandbox first
            sandbox_info = self.sandbox_service.create_sandbox(project_id, local_path, stack)
            
            if sandbox_info:
                # 3. Detect and run start command inside sandbox
                start_info = self._detect_start_command(Path(local_path), full_config)
                if start_info:
                    cmd = " ".join(start_info["command"])
                    # Execute in background inside container
                    self.sandbox_service.execute_command(project_id, f"nohup {cmd} > /workspace/app.log 2>&1 &")
                    
                self.active_sandboxes[project_id] = {**sandbox_info, "local_path": local_path}
                
                return {
                    "success": True,
                    "message": "Application started in sandbox",
                    "host_port": sandbox_info["host_port"],
                    "internal_port": sandbox_info["internal_port"],
                    "container_id": sandbox_info.get("container_id", "local-sim")
                }
        except Exception as e:
            logger.warning(f"Docker sandbox failed: {e}, falling back to local")
            
        # 4. Fallback to local
        return await self._run_local(project_id, local_path, full_config)

    async def _run_local(self, project_id: str, local_path: str, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Run process locally using asyncio for non-blocking management"""
        local_path_obj = Path(local_path)
        start_info = self._detect_start_command(local_path_obj, config)
        
        if not start_info:
            return {"success": False, "error": "Could not detect start command"}
            
        cmd = start_info["command"]
        try:
            # Create log file for local execution
            log_path = local_path_obj / "app.log"
            
            # Use asyncio to start the process
            # Note: We need to handle the output stream to write to the log file asynchronously
            process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=local_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env={**os.environ, **(config.get("env", {}) if config else {})},
                # Handle process group for clean termination
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
            )
            
            # Start background tasks to pipe stdout/stderr to log file
            async def pipe_to_file(stream, path):
                with open(path, "a") as f:
                    while True:
                        line = await stream.readline()
                        if not line: break
                        f.write(line.decode())
                        f.flush()

            asyncio.create_task(pipe_to_file(process.stdout, log_path))
            asyncio.create_task(pipe_to_file(process.stderr, log_path))
            
            self.active_processes[project_id] = {
                "process": process,
                "local_path": local_path,
                "log_path": str(log_path)
            }
            
            return {
                "success": True,
                "message": "Application started locally",
                "command": " ".join(cmd),
                "pid": process.pid,
                "log_file": str(log_path)
            }
        except Exception as e:
            logger.error(f"Local start failed: {e}")
            return {"success": False, "error": str(e)}

    async def stop_project(self, project_id: str) -> Dict[str, Any]:
        """Stop a running project (sandbox or local) asynchronously"""
        success = False
        message = "Project not found"
        
        # Stop sandbox if exists
        if project_id in self.active_sandboxes:
            try:
                self.sandbox_service.stop_sandbox(project_id)
                del self.active_sandboxes[project_id]
                success = True
                message = "Sandbox stopped"
            except Exception as e:
                return {"success": False, "error": str(e)}
            
        # Stop local process
        if project_id in self.active_processes:
            info = self.active_processes.get(project_id)
            process = info["process"]
            try:
                if os.name == 'nt':
                    # Windows process group termination
                    import subprocess
                    subprocess.run(['taskkill', '/F', '/T', '/PID', str(process.pid)], capture_output=True)
                else:
                    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                
                # Non-blocking wait
                try:
                    await asyncio.wait_for(process.wait(), timeout=5.0)
                except asyncio.TimeoutError:
                    process.kill()
                    await process.wait()
                    
                del self.active_processes[project_id]
                success = True
                message = "Local process stopped"
            except Exception as e:
                logger.error(f"Failed to stop process: {e}")
                if process: process.kill()
                if project_id in self.active_processes:
                    del self.active_processes[project_id]
                success = True
                message = "Local process killed"
        
        return {"success": success, "message": message}

    async def get_logs(self, project_id: str, lines: int = 100) -> str:
        """Get project runtime logs asynchronously"""
        try:
            if project_id in self.active_sandboxes:
                # Read from sandbox log file
                res = self.sandbox_service.execute_command(project_id, f"tail -n {lines} /workspace/app.log")
                return res.get("output", "No logs found")
            
            elif project_id in self.active_processes:
                info = self.active_processes[project_id]
                log_path = Path(info["log_path"])
                if log_path.exists():
                    # Use a non-blocking read or small buffer
                    with open(log_path, "r") as f:
                        log_data = f.readlines()
                        return "".join(log_data[-lines:])
                return "Log file not found"
            
            return "No active session for this project"
        except Exception as e:
            return f"Error retrieving logs: {e}"

    def _detect_start_command(self, path: Path, config: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Detect how to start the application"""
        if config and config.get("command"):
            return {"command": config["command"] if isinstance(config["command"], list) else config["command"].split()}
            
        # Example detections
        if (path / "main.py").exists():
            return {"command": ["python", "main.py"]}
        elif (path / "app.py").exists():
            return {"command": ["python", "app.py"]}
        elif (path / "server.js").exists():
            return {"command": ["node", "server.js"]}
        elif (path / "index.js").exists():
            return {"command": ["node", "index.js"]}
        elif (path / "package.json").exists():
            try:
                with open(path / "package.json", 'r') as f:
                    data = json.load(f)
                    if data.get("scripts", {}).get("start"):
                         return {"command": ["npm", "start"]}
            except:
                pass
        return None
