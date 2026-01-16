"""
Workflow Engine
Orchestrates multi-step project tasks
"""
import logging
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)


class WorkflowEngine:
    """Orchestrates workflows like sync -> update -> build -> run"""
    
    def __init__(self, services: Dict[str, Any]):
        self.services = services
        self.active_workflows: Dict[str, Dict[str, Any]] = {}

    async def execute_workflow(
        self,
        project_id: str,
        user_id: str,
        steps: List[str],
        config: Dict[str, Any]
    ) -> str:
        """Execute a series of steps as a single workflow"""
        workflow_id = str(uuid.uuid4())
        
        workflow = {
            "id": workflow_id,
            "project_id": project_id,
            "user_id": user_id,
            "steps": [{"name": s, "status": "pending"} for s in steps],
            "status": "in_progress",
            "started_at": datetime.utcnow().isoformat(),
            "logs": []
        }
        
        self.active_workflows[workflow_id] = workflow
        
        # Start execution in background
        asyncio.create_task(self._run_workflow_daemon(workflow_id, config))
        
        return workflow_id

    async def _run_workflow_daemon(self, workflow_id: str, config: Dict[str, Any]):
        """Background daemon for workflow execution"""
        workflow = self.active_workflows.get(workflow_id)
        if not workflow:
            return

        project_id = workflow["project_id"]
        project = self.services["project_manager"].get_project(project_id)
        
        if not project:
            workflow["status"] = "failed"
            workflow["logs"].append("Project not found")
            return

        local_path = project["local_path"]
        
        try:
            for i, step_info in enumerate(workflow["steps"]):
                step_name = step_info["name"]
                step_info["status"] = "in_progress"
                
                logger.info(f"Workflow {workflow_id}: Executing step {step_name}")
                workflow["logs"].append(f"Starting {step_name}...")
                
                success = False
                result = {}
                
                if step_name == "sync":
                    result = await self.services["git_sync"].pull_latest(local_path)
                    success = result.get("success", False)
                elif step_name == "update":
                    result = await self.services["ai_update"].apply_chat_update(
                        project_id, local_path, config.get("update_prompt", ""), config.get("context")
                    )
                    success = result.get("success", False)
                elif step_name == "push":
                    result = await self.services["git_sync"].push_changes(
                        local_path, config.get("commit_message", "Updated by AI Orchestrator")
                    )
                    success = result.get("success", False)
                elif step_name == "build":
                    result = await self.services["build"].build_project(local_path, config.get("build_config"))
                    success = result.get("success", False)
                elif step_name == "run":
                    result = await self.services["runtime"].run_project(project_id, local_path, config.get("run_config"))
                    success = result.get("success", False)
                
                if success:
                    step_info["status"] = "completed"
                    workflow["logs"].append(f"Completed {step_name} successfully.")
                else:
                    step_info["status"] = "failed"
                    workflow["status"] = "failed"
                    workflow["logs"].append(f"Failed {step_name}: {result.get('error', 'Unknown error')}")
                    break
            
            if workflow["status"] != "failed":
                workflow["status"] = "completed"
                workflow["completed_at"] = datetime.utcnow().isoformat()
                
        except Exception as e:
            workflow["status"] = "failed"
            workflow["logs"].append(f"Workflow error: {str(e)}")
            logger.error(f"Workflow execution failed: {e}")

    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a workflow"""
        return self.active_workflows.get(workflow_id)
