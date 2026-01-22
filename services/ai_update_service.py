"""
AI Update Service
Handles AI-assisted code updates (chat and inline)
"""
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import asyncio

logger = logging.getLogger(__name__)


class AIUpdateService:
    """Handles AI-assisted code updates for projects"""
    
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        
    async def apply_chat_update(
        self,
        project_id: str,
        local_path: str,
        prompt: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Apply code updates based on a chat prompt"""
        logger.info(f"Applying AI chat update for project {project_id}")
        
        # Validate orchestrator has required components
        if not hasattr(self.orchestrator, 'lead_architect') or self.orchestrator.lead_architect is None:
            logger.error("LeadArchitect not available in orchestrator")
            return {
                "success": False,
                "error": "AI update service not properly configured - LeadArchitect missing"
            }
        
        # In a real implementation, this would:
        # 1. Use the Universal AI Agent to analyze the prompt and project context
        # 2. Identify files that need to be changed
        # 3. Generate content for those changes
        # 4. Apply the changes to the files
        
        # For now, let's simulate the generation
        full_prompt = f"Project Path: {local_path}\nUpdate Request: {prompt}\nContext: {context}"
        
        try:
            # VISION 2026: Use Lead Architect for swarm-powered code updates
            logger.info(f"Delegating code update to LeadArchitect swarm")
            response = await self.orchestrator.lead_architect.act(
                task=prompt,
                context={
                    "type": "code_update",
                    "project_path": local_path,
                    "project_id": project_id,
                    "context": context
                }
            )
            
            # Aggregate summary from swarm result
            swarm_output = response.get("worker_results", {})
            summary = response.get("summary", f"Code updated via swarm across {len(swarm_output)} domains")
            
            return {
                "success": True,
                "summary": summary,
                "changes": [res.get("solution") for res in swarm_output.values()],
                "swarm_details": response.get("decomposition", []),
                "update_id": str(asyncio.get_event_loop().time())
            }
        except Exception as e:
            logger.error(f"AI chat update failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def apply_inline_update(
        self,
        local_path: str,
        file_path: str,
        prompt: str,
        selection: Optional[Dict[str, int]] = None
    ) -> Dict[str, Any]:
        """Apply an inline update to a specific file"""
        full_file_path = Path(local_path) / file_path
        if not full_file_path.exists():
            return {"success": False, "error": f"File {file_path} not found"}
        
        # Validate orchestrator has required components
        if not hasattr(self.orchestrator, 'universal_agent') or self.orchestrator.universal_agent is None:
            logger.error("UniversalAgent not available in orchestrator")
            return {
                "success": False,
                "error": "AI update service not properly configured - UniversalAgent missing"
            }
            
        logger.info(f"Applying AI inline update to {file_path}")
        
        try:
            content = full_file_path.read_text()
            
            # Use universal agent for targeted file editing
            result = await self.orchestrator.universal_agent.act(
                task=f"Edit the following file based on this request: {prompt}",
                context={
                    "code": content,
                    "file_path": str(full_file_path),
                    "selection": selection,
                    "type": "inline_edit"
                }
            )
            
            updated_content = result.get("solution", "")
            
            # Extract code from solution if it's wrapped in markdown
            import re
            code_match = re.search(r'```(?:\w+)?\n(.*?)\n```', updated_content, re.DOTALL)
            if code_match:
                updated_content = code_match.group(1)
            
            if updated_content:
                full_file_path.write_text(updated_content)
            
            return {
                "success": True,
                "file": file_path,
                "message": "File updated successfully"
            }
        except Exception as e:
            logger.error(f"AI inline update failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
