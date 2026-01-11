"""
Lead Architect Agent
Orchestrates the swarm of specialized workers
"""
import logging
import json
import re
from typing import List, Dict, Any
from agents.base import BaseAgent

logger = logging.getLogger(__name__)

class LeadArchitectAgent(BaseAgent):
    """The central intelligence that decomposes tasks and manages workers"""
    
    def __init__(self, orchestrator):
        super().__init__(
            name="LeadArchitect",
            role="System Architect",
            system_prompt="""You are the Lead Architect of an AI Migration Factory.
            Your job is to receive high-level migration requests, decompose them into technical subtasks,
            delegate those tasks to specialized workers, and aggregate the results.
            
            When decomposing tasks, return a JSON list of subtasks. Each subtask MUST have:
            - "domain": The technical domain (e.g., 'java', 'frontend', 'database', 'devops').
            - "instruction": Specific, actionable instruction for a worker agent.
            
            Example output format:
            [
              {"domain": "java", "instruction": "Analyze legacy controllers in /src/main/java..."},
              {"domain": "frontend", "instruction": "Map CSS variables to the new design system..."}
            ]"""
        )
        self.orchestrator = orchestrator

    async def act(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        logger.info(f"Lead Architect acting on task: {task[:100]}")
        context = context or {}
        
        # 1. Check for SPECIAL DIRECTIVES (like Self-Healing / Auto-Repair)
        if context.get("type") == "self_healing":
            logger.info("Lead Architect in SELF-HEALING mode. Analyzing repair task...")
            # For self-healing, we often want a direct fix rather than standard decomposition
            # We use the universal_agent directly to generate a patch
            repair_result = await self.orchestrator.universal_agent.act(
                task, 
                {"context": "Runtime Error Repair", "priority": "critical"}
            )
            return {
                "status": "repaired",
                "fix_details": repair_result,
                "agent": "LeadArchitect[SelfHealing]"
            }
            
        # 2. Check for Lifecycle Finalization (E2E Push/Test)
        if context.get("type") == "finalization":
            logger.info("Lead Architect in FINALIZATION mode. Syncing to Git/Provisioning...")
            project_id = context.get("project_id")
            stack = context.get("stack", "general")
            
            # Auto-provision test
            test_info = await self.orchestrator.lifecycle.provision_and_test(project_id, stack)
            
            # Auto-sync to Git (if requested)
            git_info = {}
            if context.get("git_sync"):
                git_info = await self.orchestrator.lifecycle.sync_to_git(
                    project_id, 
                    context.get("git_provider", "github"),
                    context.get("repo_name", "generated-app")
                )
                
            return {
                "status": "finalized",
                "test_env": test_info,
                "git_sync": git_info,
                "agent": "LeadArchitect[Lifecycle]"
            }

        # 3. Standard flow: Dynamically decompose task using LLM
        subtasks = await self._decompose(task)
        results = {}
        
        # 2. Delegate to Universal AI Agent for each domain
        # In a more advanced swarm, we'd create specialized WorkerAgents here
        for subtask in subtasks:
            domain = subtask.get("domain", "general")
            instruction = subtask.get("instruction")
            
            if instruction:
                logger.info(f"Delegating technical task to universal worker for domain: {domain}...")
                # We use the universal_agent as the base worker for all domains now
                # Pass domain context to help the universal agent focus
                worker_context = context.copy() if context else {}
                worker_context["domain"] = domain
                
                results[domain] = await self.orchestrator.universal_agent.act(instruction, worker_context)
            else:
                logger.warning(f"Empty instruction for domain: {domain}")
        
        # 3. Aggregate results
        return {
            "status": "success",
            "decomposition": subtasks,
            "worker_results": results
        }

    async def _decompose(self, task: str) -> List[Dict[str, str]]:
        """Use LLM to decompose task into specialized subtasks"""
        prompt = f"Decompose the following migration request into a list of specialized subtasks: {task}"
        
        try:
            response = await self.orchestrator.llm.generate(
                prompt=prompt,
                system_prompt=self.system_prompt
            )
            
            # Extract JSON from response (handling potential markdown blocks)
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                subtasks = json.loads(json_match.group(0))
                return subtasks
            else:
                logger.warning("LLM response did not contain a valid JSON list of subtasks.")
                return [{"domain": "general", "instruction": task}]
                
        except Exception as e:
            logger.error(f"Failed to decompose task via LLM: {e}")
            return [{"domain": "error", "instruction": f"Fallback: {task}"}]
