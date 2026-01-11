"""
Project Lifecycle Service - E2E Orchestration for 2026
Connects Storage, Workbench, Git, and Build Systems.
"""
import logging
import os
import shutil
from typing import Dict, Any, Optional
from core.storage.manager import StorageManager
from services.git.repository_manager import RepositoryManager

logger = logging.getLogger(__name__)

class ProjectLifecycleService:
    """Orchestrates the lifecycle from generation to deployment and Git push"""
    
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.storage = orchestrator.storage if hasattr(orchestrator, 'storage') else StorageManager()
        self.git = RepositoryManager(orchestrator.git_credentials) 
        
    async def provision_and_test(self, project_id: str, stack: str) -> Dict[str, Any]:
        """
        1. Extract project from storage
        2. Provision a Docker workbench
        3. Build and Start the project
        4. Return live testing URL
        """
        logger.info(f"Lifecycle: Provisioning test environment for project {project_id} ({stack})")
        
        # 1. Prepare local workspace
        project_meta = await self.storage.get_project(project_id)
        if not project_meta:
            raise ValueError(f"Project {project_id} not found in storage")
            
        temp_dir = f"temp/test_{project_id}"
        await self.storage.extract_project(project_id, temp_dir)
        
        # 2. Provision Workbench (Docker)
        workbench = await self.orchestrator.workbench_manager.create_workbench(
            stack=stack,
            project_name=project_meta.get("name", "app"),
            mount_path=os.path.abspath(temp_dir)
        )
        
        # 3. Generate and Run Build Script
        build_script = self.orchestrator.build_system.generate_build_script(stack, project_meta.get("name"))
        with open(os.path.join(temp_dir, "build.sh"), "w") as f:
            f.write(build_script)
            
        # Execute build in container
        build_result = await workbench.execute("bash build.sh")
        
        # 4. Port Forwarding / Tunneling
        # Assuming app runs on 8080 by default (stack dependent in real version)
        tunnel = await self.orchestrator.port_manager.create_tunnel(workbench.id, 8080)
        
        return {
            "status": "active",
            "workbench_id": workbench.id,
            "live_url": tunnel["public_url"],
            "build_log": build_result["stdout"]
        }

    async def sync_to_git(self, project_id: str, provider: str, repo_name: str) -> Dict[str, Any]:
        """
        1. Finalize code in storage
        2. Init local Git
        3. Create remote repo
        4. Push
        """
        logger.info(f"Lifecycle: Syncing project {project_id} to {provider}/{repo_name}")
        
        # Extract to a temp path for git operations
        temp_git_dir = f"temp/git_{project_id}"
        await self.storage.extract_project(project_id, temp_git_dir)
        
        # Init and Push
        remote_url = self.git.create_remote_repository(provider, repo_name)
        if not remote_url:
            return {"status": "error", "message": "Failed to create remote repository"}
            
        success = self.git.push_to_remote(temp_git_dir, remote_url)
        
        # Cleanup
        shutil.rmtree(temp_git_dir)
        
        return {
            "status": "success" if success else "failed",
            "remote_url": remote_url
        }
