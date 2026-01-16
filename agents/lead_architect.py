"""
Lead Architect Agent - Swarm Orchestrator (Ultimate 2026 Edition)
"""
import logging
import json
import re
import asyncio
from typing import List, Dict, Any
from agents.base import BaseAgent

logger = logging.getLogger(__name__)

class LeadArchitectAgent(BaseAgent):
    """The central intelligence that decomposes tasks and manages workers with multi-pass refinement"""
    
    def __init__(self, orchestrator):
        super().__init__(
            name="LeadArchitect",
            role="System Architect",
            system_prompt="Expert in decomposing complex tasks into a swarm of specialized AI agents."
        )
        self.orchestrator = orchestrator

    async def act(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Orchestrate the swarm to solve any task with ultimate quality control"""
        logger.info(f"Lead Architect orchestrating task: {task[:50]}...")
        context = context or {}
        task_type = context.get("type", "general")
        
        # 1. Decompose the task into specialized domains
        subtasks = await self._decompose(task, task_type)
        
        # 2. VISION 2026: Execute all subtasks in PARALLEL using asyncio.gather
        logger.info(f"🚀 Swarm Parallelization: Executing {len(subtasks)} subtasks simultaneously")
        
        # Create parallel tasks
        parallel_tasks = []
        for subtask in subtasks:
            if subtask.get("instruction"):
                parallel_tasks.append(self._execute_subtask_with_review(subtask, context))
        
        # Execute all subtasks in parallel
        results_list = await asyncio.gather(*parallel_tasks, return_exceptions=True)
        
        # Aggregate results
        results = {}
        for i, result in enumerate(results_list):
            if isinstance(result, Exception):
                logger.error(f"Subtask {i} failed: {result}")
                continue
            
            domain = result.get("domain", f"task_{i}")
            results[domain] = result
        
        logger.info(f"✅ Parallel execution complete: {len(results)} domains processed")
        
        return {
            "status": "success",
            "type": task_type,
            "decomposition": subtasks,
            "worker_results": results,
            "agent": "LeadArchitect[SwarmMode-Parallel]"
        }
    
    async def _execute_subtask_with_review(self, subtask: Dict[str, Any], base_context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single subtask with build + review pass (helper for parallel execution)"""
        domain = subtask.get("domain", "general")
        instruction = subtask.get("instruction")
        recommended_model = subtask.get("model", "coder")
        
        # PHASE 1: GENERATE / MIGRATE / FIX
        logger.info(f"Swarm Phase 1 [{domain}]: Executing with {recommended_model}")
        worker_context = base_context.copy()
        worker_context.update({
            "domain": domain,
            "model": recommended_model,
            "generate_docker": True if domain == "infrastructure" else False
        })
        
        initial_result = await self.orchestrator.universal_agent.act(instruction, worker_context)
        
        # PHASE 2: REVIEW & REFINE (Ultimate Quality Pass)
        logger.info(f"Swarm Phase 2 [{domain}]: Peer review refinement...")
        review_instruction = f"Review and REFINE this {domain} solution for 2026 standards. Ensure security, efficiency, and zero placeholders. Code: {initial_result.get('solution')}"
        
        review_context = worker_context.copy()
        review_context.update({
            "model": "specialist",
            "is_review": True
        })
        
        final_result = await self.orchestrator.universal_agent.act(review_instruction, review_context)
        
        # Merge results
        final_result["infrastructure"] = initial_result.get("infrastructure", {})
        final_result["domain"] = domain
        
        return final_result

    async def _decompose(self, task: str, task_type: str = "general") -> List[Dict[str, Any]]:
        """Determine the swarm structure based on the task type"""
        
        # Deterministic decomposition for core platform features
        if task_type == "full_project_generation":
            return [
                {"domain": "backend", "instruction": f"Generate backend for: {task}", "model": "coder"},
                {"domain": "frontend", "instruction": f"Generate frontend for: {task}", "model": "coder"},
                {"domain": "database", "instruction": f"Generate DB schema for: {task}", "model": "specialist"},
                {"domain": "infrastructure", "instruction": f"Generate Docker orchestration for: {task}", "model": "smart"}
            ]
        elif task_type in ["migration", "project_migration"]:
            return [
                {"domain": "analysis", "instruction": f"Deep analysis of legacy source: {task}", "model": "smart"},
                {"domain": "migration", "instruction": f"Modernize and migrate core logic: {task}", "model": "coder"},
                {"domain": "infrastructure", "instruction": f"Containerize target environment: {task}", "model": "smart"}
            ]
        elif task_type in ["self_healing", "fix"]:
            return [
                {"domain": "audit", "instruction": f"Locate root cause for: {task}", "model": "smart"},
                {"domain": "fix", "instruction": f"Implement secure fix for: {task}", "model": "coder"}
            ]
            
        # Dynamic decomposition fallback
        prompt = f"Return a JSON list of subtasks (keys: domain, instruction, model) to solve: {task}"
        response = await self.orchestrator.run_inference(prompt, model="smart")
        try:
            res_str = response.get("solution", "[]")
            match = re.search(r'\[.*\]', res_str, re.DOTALL)
            return json.loads(match.group(0)) if match else [{"domain": "general", "instruction": task, "model": "coder"}]
        except:
            return [{"domain": "general", "instruction": task, "model": "coder"}]
