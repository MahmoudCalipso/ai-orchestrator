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
    """Handles running applications"""
    
    def __init__(self):
        self.active_processes: Dict[str, subprocess.Popen] = {}
        
    async def run_project(
        self,
        project_id: str,
        local_path: str,
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Run a project application"""
        if project_id in self.active_processes:
            return {"success": False, "error": "Project is already running"}
            
        local_path_obj = Path(local_path)
        logger.info(f"Starting project {project_id} at {local_path}")
        
        # 1. Detect start command
        start_info = self._detect_start_command(local_path_obj, config)
        
        if not start_info:
            return {"success": False, "error": "Could not detect start command"}
            
        cmd = start_info["command"]
        
        try:
            # 2. Start process
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
                "message": "Application started",
                "command": " ".join(cmd),
                "pid": process.pid
            }
            
        except Exception as e:
            logger.error(f"Failed to start application: {e}")
            return {"success": False, "error": str(e)}

    def stop_project(self, project_id: str) -> bool:
        """Stop a running project"""
        process = self.active_processes.get(project_id)
        if not process:
            return False
            
        try:
            # Kill process group
            if hasattr(os, 'killpg'):
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)
            else:
                process.terminate()
                
            process.wait(timeout=5)
            del self.active_processes[project_id]
            return True
        except:
            if process:
                process.kill()
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
