"""
Base Agent Implementation
Defines the core interface for all agents in the swarm
"""
import logging
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """Abstract base class for all agents"""
    
    def __init__(
        self,
        name: str,
        role: str,
        system_prompt: str,
        model: str = "auto",
        tools: List[Dict[str, Any]] = None
    ):
        self.name = name
        self.role = role
        self.system_prompt = system_prompt
        self.model = model
        self.tools = tools or []
        self.memory: List[Dict[str, str]] = []
        
    def add_to_memory(self, role: str, content: str):
        """Add a message to the agent's short-term memory"""
        self.memory.append({"role": role, "content": content})
        # Keep memory bounded
        if len(self.memory) > 20:
            self.memory = self.memory[-20:]

    @abstractmethod
    async def act(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a task and return results"""
        pass

    def get_full_prompt(self, current_input: str) -> List[Dict[str, str]]:
        """Construct the full message list for the LLM"""
        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend(self.memory)
        messages.append({"role": "user", "content": current_input})
        return messages

class WorkerAgent(BaseAgent):
    """Standard worker agent with specific domain expertise"""
    
    def __init__(
        self,
        name: str,
        role: str,
        domain: str,
        system_prompt: str,
        orchestrator=None
    ):
        super().__init__(name, role, system_prompt)
        self.domain = domain
        self.orchestrator = orchestrator # Reference to parent for tool access if needed

    async def act(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        logger.info(f"Agent {self.name} ({self.domain}) acting on task: {task[:50]}...")
        
        # In a real implementation, this would call the Orchestrator's inference engine
        # with the agent's specific system prompt and tools.
        # For now, we simulate the interaction pattern.
        
        return {
            "agent": self.name,
            "domain": self.domain,
            "status": "completed",
            "output": f"Simulated output from {self.name} for domain {self.domain}"
        }
