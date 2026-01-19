"""
Runtime Service
Handles running project applications
"""
import logging
import subprocess
import os
import signal
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class RuntimeService:
    """Handles running applications using local processes or Docker sandboxes"""
    
    def __init__(self):
        self.active_processes: Dict[str, subprocess.Popen] = {}
        from services.workspace.docker_sandbox import DockerSandboxService
        self.sandbox_service = DockerSandboxService()
        self.active_sandboxes: Dict[str, Dict[str, Any]] = {}
        
    async def run_project(
        self,
        project_id: str,
        local_path: str,
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Run a project application in a sandbox"""
        if project_id in self.active_sandboxes:
            return {"success": False, "error": "Project is already running in a sandbox"}
            
        logger.info(f"Starting project {project_id} in sandbox at {local_path}")
        
        # 1. Detect tech stack for image selection
        stack = config.get("stack", "node") if config else "node"
        
        # 2. Create sandbox
        sandbox_info = self.sandbox_service.create_sandbox(project_id, local_path, stack)
        
        if not sandbox_info:
            # Fallback to local process if Docker fails
            logger.warning("Docker sandbox failed, falling back to local execution")
            return await self._run_local(project_id, local_path, config)
            
        # 3. Detect and run start command inside sandbox
        start_info = self._detect_start_command(Path(local_path), config)
        if start_info:
            cmd = " ".join(start_info["command"])
            # Execute in background inside container
            # In a real DinD setup, we might use a supervisor or just exec
            self.sandbox_service.execute_command(project_id, f"nohup {cmd} > /workspace/app.log 2>&1 &")
            
        self.active_sandboxes[project_id] = sandbox_info
        
        return {
            "success": True,
            "message": "Application started in sandbox",
            "host_port": sandbox_info["host_port"],
            "internal_port": sandbox_info["internal_port"],
            "container_id": sandbox_info["container_id"]
        }

    async def _run_local(self, project_id: str, local_path: str, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Original local execution logic as fallback"""
        local_path_obj = Path(local_path)
        start_info = self._detect_start_command(local_path_obj, config)
        
        if not start_info:
            return {"success": False, "error": "Could not detect start command"}
            
        cmd = start_info["command"]
        try:
            process = subprocess.Popen(
                cmd,
                cwd=local_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                preexec_fn=os.setsid if hasattr(os, 'setsid') else None
            )
            self.active_processes[project_id] = process
            return {
                "success": True,
                "message": "Application started locally",
                "command": " ".join(cmd),
                "pid": process.pid
            }
        except Exception as e:
            logger.error(f"Local start failed: {e}")
            return {"success": False, "error": str(e)}

    def stop_project(self, project_id: str) -> bool:
        """Stop a running project (sandbox or local)"""
        # Stop sandbox if exists
        if project_id in self.active_sandboxes:
            self.sandbox_service.stop_sandbox(project_id)
            del self.active_sandboxes[project_id]
            return True
            
        # Stop local process
        process = self.active_processes.get(project_id)
        if not process:
            return False
        
        try:
            if hasattr(os, 'killpg'):
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)
            else:
                process.terminate()
            process.wait(timeout=5)
            del self.active_processes[project_id]
            return True
        except:
            if process: process.kill()
            del self.active_processes[project_id]
            return True

    def _detect_start_command(self, path: Path, config: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Detect how to start the application"""
        if config and config.get("command"):
            return {"command": config["command"].split()}
            
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
            return {"command": ["npm", "start"]}
        elif (path / "docker-compose.yml").exists():
            return {"command": ["docker-compose", "up", "-d"]}
            
        return None
