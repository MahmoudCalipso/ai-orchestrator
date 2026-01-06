"""
Lead Architect Agent
Orchestrates the swarm of specialized workers
"""
import logging
from typing import List, Dict, Any, Optional
from agents.base import BaseAgent
from agents.specialists import JavaExpertAgent, AngularExpertAgent, FlutterExpertAgent

logger = logging.getLogger(__name__)

class LeadArchitectAgent(BaseAgent):
    """The central intelligence that decomposes tasks and manages workers"""
    
    def __init__(self, orchestrator):
        super().__init__(
            name="LeadArchitect",
            role="System Architect",
            system_prompt="""You are the Lead Architect of an AI Migration Factory.
            Your job is to receive high-level migration requests, decompose them into technical subtasks,
            delegate those tasks to specialized agents (Java, Angular, Flutter), and aggregate the results.
            You have access to a Blackboard state store to track progress."""
        )
        self.orchestrator = orchestrator
        self.workers: Dict[str, Any] = {
            "java": JavaExpertAgent(orchestrator),
            "angular": AngularExpertAgent(orchestrator),
            "flutter": FlutterExpertAgent(orchestrator)
        }

    async def act(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        logger.info(f"Lead Architect decomposing task: {task[:100]}")
        
        # 1. Decompose task (Simulated logic)
        subtasks = self._decompose(task)
        results = {}
        
        # 2. Delegate to workers
        for subtask in subtasks:
            domain = subtask.get("domain")
            if domain in self.workers:
                worker = self.workers[domain]
                logger.info(f"Delegating technical task to {worker.name}...")
                results[domain] = await worker.act(subtask["instruction"])
            else:
                logger.warning(f"No worker available for domain: {domain}")
        
        # 3. Aggregate
        return {
            "status": "success",
            "aggregate_output": "Migration plan and initial code generated.",
            "worker_results": results
        }

    def _decompose(self, task: str) -> List[Dict[str, str]]:
        """Simulate task decomposition into subtasks for agents"""
        # In real scenario, this would be an LLM call
        return [
            {"domain": "java", "instruction": "Analyze legacy Java controllers"},
            {"domain": "angular", "instruction": "Map AngularJS routes to Angular"}
        ]
