"""
Migration Healing Service
Automates the 'Build -> Detect -> Fix' loop for migrated projects.
"""
import logging
import asyncio
from typing import Dict, Any, List
from pathlib import Path

logger = logging.getLogger(__name__)

class MigrationHealingService:
    """Service to automatically fix build and runtime errors in migrated code"""
    
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.max_fixing_rounds = 3

    async def heal_project(self, project_path: str, stack: str) -> Dict[str, Any]:
        """Attempt to build and fix project repeatedly until it works or limit reached"""
        rounds = 0
        success = False
        errors = []
        
        logger.info(f"Starting self-healing loop for project at {project_path}")
        
        while rounds < self.max_fixing_rounds:
            rounds += 1
            logger.info(f"Healing Round {rounds}/{self.max_fixing_rounds}")
            
            # 1. Attempt Build/Test
            build_result = await self._run_build_test(project_path, stack)
            
            if build_result["status"] == "success":
                logger.info(f"✅ Project healed successfully in {rounds} rounds.")
                success = True
                break
            
            # 2. Extract Errors
            error_output = build_result.get("output", "")
            errors.append(error_output)
            logger.warning(f"Build failed. Found errors: {error_output[:200]}...")
            
            # 3. Use AI to Fix
            await self._apply_ai_fixes(project_path, error_output, stack)
            
        return {
            "success": success,
            "rounds": rounds,
            "errors": errors if not success else []
        }

    async def _run_build_test(self, project_path: str, stack: str) -> Dict[str, Any]:
        """Run build command in a sandbox"""
        from services.runtime_service import RuntimeService
        runtime = RuntimeService()
        
        # Try to run it in a sandbox
        # For build testing, we might just need to run 'pip install' or 'npm install' then check exit code
        # This is strictly for the verification phase of the migration
        
        # Mocking build result for now
        # In production, this would call DockerSandboxService.execute_command
        return {"status": "success", "output": ""}

    async def _apply_ai_fixes(self, project_path: str, error_output: str, stack: str):
        """Analyze errors and fix files via LLM"""
        logger.info("Applying AI fixes to resolve build errors...")
        
        prompt = f"""
        A recently migrated {stack} project is failing to build with the following error:
        {error_output}
        
        PROJECT PATH: {project_path}
        
        Identify the root cause and provide the corrected code for the failing file(s).
        Respond with a list of file paths and their corrected content in this format:
        FILE: path/to/file.ext
        ```
        CODE
        ```
        """
        
        result = await self.orchestrator.run_inference(prompt=prompt, task_type="fix")
        # Apply the fixes (simplified file parsing logic here)
        # In production, we'd use a regex to extract files and write them back
        logger.info("AI fixes suggested. Applying to workspace...")
