"""
Docker Sandbox Service - Ephemeral Runtime Workspaces
Provides sandboxed execution environments for projects.
"""
import docker
import logging
import os
import socket
import time
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

class DockerSandboxService:
    """Manages ephemeral Docker containers for project execution and testing"""
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(DockerSandboxService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, '_initialized') and self._initialized:
            return
            
        try:
            self.client = docker.from_env()
            self._initialized = True
            logger.info("Docker Sandbox Service initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Docker client: {e}")
            self.client = None
            self._initialized = False

    def create_sandbox(self, project_id: str, local_path: str, tech_stack: str = "node") -> Optional[Dict[str, Any]]:
        """
        Create a new sandbox container for a project
        
        Args:
            project_id: Unique identifier for the project
            local_path: Absolute path to project source on host
            tech_stack: Detected tech stack (node, python, go, etc.)
            
        Returns:
            Dict with container info and mapped ports
        """
        if not self._initialized:
            logger.error("Docker service not available")
            return None
        
        container_name = f"orch-sandbox-{project_id}"
        image = self._get_image_for_stack(tech_stack)
        
        # Ensure fresh start
        self.stop_sandbox(project_id)
        
        try:
            # Detect primary app port (default 3000 for web apps)
            app_port = 3000
            host_port = self._find_free_port()
            
            # Start container
            container = self.client.containers.run(
                image=image,
                name=container_name,
                volumes={
                    os.path.abspath(local_path): {'bind': '/workspace', 'mode': 'rw'}
                },
                working_dir='/workspace',
                ports={f'{app_port}/tcp': host_port},
                detach=True,
                tty=True,
                stdin_open=True,
                environment={
                    "ORCH_SANDBOX": "true",
                    "PROJECT_ID": project_id,
                    "NODE_ENV": "development",
                    "PYTHONUNBUFFERED": "1"
                },
                labels={"type": "ai-orchestrator-sandbox", "project_id": project_id}
            )
            
            logger.info(f"Sandbox created: {container_name} | Image: {image} | Port: {host_port}->{app_port}")
            
            return {
                "container_id": container.id,
                "name": container_name,
                "host_port": host_port,
                "internal_port": app_port,
                "status": "running"
            }
        except Exception as e:
            logger.error(f"Failed to start sandbox container: {e}")
            return None

    def execute_command(self, project_id: str, command: str) -> Dict[str, Any]:
        """Execute a command inside the sandbox"""
        if not self._initialized: return {"error": "Docker not available"}
        
        container_name = f"orch-sandbox-{project_id}"
        try:
            container = self.client.containers.get(container_name)
            exec_result = container.exec_run(command, stream=False, demux=True)
            
            stdout = exec_result.output[0].decode('utf-8') if exec_result.output[0] else ""
            stderr = exec_result.output[1].decode('utf-8') if exec_result.output[1] else ""
            
            return {
                "exit_code": exec_result.exit_code,
                "stdout": stdout,
                "stderr": stderr
            }
        except Exception as e:
            logger.error(f"Command execution failed in {container_name}: {e}")
            return {"error": str(e)}

    def stop_sandbox(self, project_id: str):
        """Stop and remove sandbox"""
        if not self._initialized: return
        
        container_name = f"orch-sandbox-{project_id}"
        try:
            container = self.client.containers.get(container_name)
            container.stop(timeout=2)
            container.remove()
            logger.info(f"Sandbox removed: {container_name}")
        except docker.errors.NotFound:
            pass
        except Exception as e:
            logger.warning(f"Error removing sandbox {container_name}: {e}")

    def get_logs_stream(self, project_id: str):
        """Stream logs from container"""
        if not self._initialized: return
        
        container_name = f"orch-sandbox-{project_id}"
        try:
            container = self.client.containers.get(container_name)
            return container.logs(stream=True, follow=True, tail=100)
        except Exception as e:
            logger.error(f"Log stream failed for {container_name}: {e}")
            return None

    def _get_image_for_stack(self, stack: str) -> str:
        """Map tech stack to appropriate Docker image"""
        stack = stack.lower()
        mapping = {
            "node": "node:20-alpine",
            "angular": "node:20-alpine",
            "react": "node:20-alpine",
            "python": "python:3.12-slim",
            "django": "python:3.12-slim",
            "fastapi": "python:3.12-slim",
            "go": "golang:1.22-alpine",
            "rust": "rust:1.75-slim",
            "java": "eclipse-temurin:21-alpine",
            "dotnet": "mcr.microsoft.com/dotnet/sdk:8.0"
        }
        return mapping.get(stack, "alpine:latest")

    def _find_free_port(self) -> int:
        """Allocate a free port on host"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            return s.getsockname()[1]
