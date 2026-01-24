"""
Universal Workbench Manager
Manages Docker-based isolated environments for any tech stack
"""
import logging
import uuid
from typing import Dict, Any, List
import docker
from docker.models.containers import Container
from core.workbench.blueprint import BlueprintRegistry, WorkbenchBlueprint

logger = logging.getLogger(__name__)

class Workbench:
    """Represents a single isolated workbench environment"""
    
    def __init__(self, workbench_id: str, stack: str, container: Container, blueprint: WorkbenchBlueprint):
        self.id = workbench_id
        self.stack = stack
        self.container = container
        self.blueprint = blueprint
        self.status = "running"
        
    async def execute(self, command: str, workdir: str = "/workspace") -> Dict[str, Any]:
        """Execute a command inside the workbench"""
        try:
            exec_result = self.container.exec_run(
                cmd=f"sh -c '{command}'",
                workdir=workdir,
                demux=True
            )
            
            stdout = exec_result.output[0].decode() if exec_result.output[0] else ""
            stderr = exec_result.output[1].decode() if exec_result.output[1] else ""
            
            return {
                "exit_code": exec_result.exit_code,
                "stdout": stdout,
                "stderr": stderr,
                "success": exec_result.exit_code == 0
            }
        except Exception as e:
            logger.error(f"Failed to execute command in workbench {self.id}: {e}")
            return {
                "exit_code": -1,
                "stdout": "",
                "stderr": str(e),
                "success": False
            }
    
    async def upload_file(self, local_path: str, container_path: str):
        """Upload a file to the workbench"""
        # Implementation would use docker.put_archive
        pass
    
    async def download_file(self, container_path: str, local_path: str):
        """Download a file from the workbench"""
        # Implementation would use docker.get_archive
        pass

class WorkbenchManager:
    """Manages lifecycle of all workbenches"""
    
    def __init__(self):
        try:
            self.docker_client = docker.from_env()
            logger.info("Docker client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Docker client: {e}")
            self.docker_client = None
        
        self.workbenches: Dict[str, Workbench] = {}
        self.blueprint_registry = BlueprintRegistry()
    
    async def create_workbench(
        self,
        stack: str,
        project_name: str = None,
        mount_path: str = None
    ) -> Workbench:
        """Create a new isolated workbench for a specific stack"""
        if not self.docker_client:
            raise RuntimeError("Docker client not available")
        
        blueprint = self.blueprint_registry.get_blueprint(stack)
        if not blueprint:
            raise ValueError(f"Unknown stack: {stack}")
        
        workbench_id = f"wb-{uuid.uuid4().hex[:8]}"
        container_name = f"orchestrator-{workbench_id}"
        
        logger.info(f"Creating workbench {workbench_id} for stack {stack}")
        
        # Prepare volumes
        volumes = {}
        if mount_path:
            volumes[mount_path] = {"bind": "/workspace", "mode": "rw"}
        
        # Environment variables
        environment = {
            "WORKBENCH_ID": workbench_id,
            "STACK": stack,
            "PROJECT_NAME": project_name or "migration"
        }
        
        # Create Dockerfile content for universal tooling
        dockerfile_content = f"""
FROM {blueprint.base_image}

# Install universal tooling
RUN apt-get update && apt-get install -y \\
    git \\
    curl \\
    jq \\
    wget \\
    vim \\
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Keep container running
CMD ["tail", "-f", "/dev/null"]
"""
        
        try:
            # For simplicity, we'll use the base image directly
            # In production, you'd build custom images with universal tools
            container = self.docker_client.containers.run(
                image=blueprint.base_image,
                name=container_name,
                detach=True,
                volumes=volumes,
                environment=environment,
                network_mode="bridge",
                remove=False,
                command="tail -f /dev/null"  # Keep container alive
            )
            
            # Install universal tools
            await self._install_universal_tools(container)
            
            workbench = Workbench(workbench_id, stack, container, blueprint)
            self.workbenches[workbench_id] = workbench
            
            logger.info(f"Workbench {workbench_id} created successfully")
            return workbench
            
        except Exception as e:
            logger.error(f"Failed to create workbench: {e}")
            raise
    
    async def _install_universal_tools(self, container: Container):
        """Install git, curl, jq in the container"""
        commands = [
            "apt-get update || apk update || yum update -y || true",
            "apt-get install -y git curl jq || apk add git curl jq || yum install -y git curl jq || true"
        ]
        
        for cmd in commands:
            try:
                container.exec_run(cmd)
            except:
                pass  # Best effort
    
    async def execute_in_workbench(
        self,
        workbench_id: str,
        command: str,
        workdir: str = "/workspace"
    ) -> Dict[str, Any]:
        """Execute a command in a specific workbench"""
        workbench = self.workbenches.get(workbench_id)
        if not workbench:
            raise ValueError(f"Workbench {workbench_id} not found")
        
        return await workbench.execute(command, workdir)
    
    async def destroy_workbench(self, workbench_id: str):
        """Destroy a workbench and cleanup resources"""
        workbench = self.workbenches.get(workbench_id)
        if not workbench:
            logger.warning(f"Workbench {workbench_id} not found")
            return
        
        try:
            workbench.container.stop()
            workbench.container.remove()
            del self.workbenches[workbench_id]
            logger.info(f"Workbench {workbench_id} destroyed")
        except Exception as e:
            logger.error(f"Failed to destroy workbench {workbench_id}: {e}")
    
    async def list_workbenches(self) -> List[Dict[str, Any]]:
        """List all active workbenches"""
        return [
            {
                "id": wb.id,
                "stack": wb.stack,
                "status": wb.status,
                "container_id": wb.container.id[:12]
            }
            for wb in self.workbenches.values()
        ]
    
    async def cleanup_all(self):
        """Cleanup all workbenches"""
        for workbench_id in list(self.workbenches.keys()):
            await self.destroy_workbench(workbench_id)

    def get_all_workbenches(self) -> Dict[str, Any]:
        """Get raw workbenches dictionary (For Enterprise monitoring)"""
        return {
            wb_id: {
                "id": wb.id,
                "stack": wb.stack,
                "status": wb.status,
                "owner_id": getattr(wb, "owner_id", None), # Safe access
                "last_active": getattr(wb, "last_active", None)
            }
            for wb_id, wb in self.workbenches.items()
        }
