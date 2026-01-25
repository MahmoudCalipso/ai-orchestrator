"""
Lead Architect Agent - Swarm Orchestrator (Ultimate 2026 Edition)
"""
import logging
import json
import re
import asyncio
import ast
from typing import Dict, Any, List, Optional
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
        subtasks = await self._decompose(task, task_type, context)
        
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
        
        # Injected context from previous steps (like audit findings and best practices)
        injected_context = ""
        if domain == "migration" and base_context.get("type") == "migration":
            # Fetch best practices for target stack
            target_stack = base_context.get("target_stack", "python")
            target_arch = base_context.get("target_architecture", "Clean Architecture")
            
            from services.registry.framework_registry import framework_registry
            
            # Dynamic lookup based on project stack
            lang = base_context.get("language", "python")
            fw = base_context.get("framework", "fastapi")
            
            logger.info(f"🚀 AI Power-Up: Fetching best practices for {lang}/{fw}")
            best_practices = framework_registry.get_best_practices(lang, fw)
            
            if best_practices:
                injected_context += "\nSTRICT BEST PRACTICES TO FOLLOW:\n- " + "\n- ".join(best_practices)
            
            injected_context += f"\nTARGET ARCHITECTURE: {target_arch}"
            
        # PHASE 1: GENERATE / MIGRATE / FIX
        logger.info(f"Swarm Phase 1 [{domain}]: Executing with {recommended_model}")
        worker_context = base_context.copy()
        worker_context.update({
            "domain": domain,
            "model": recommended_model,
            "generate_docker": True if domain == "infrastructure" else False
        })
        
        full_instruction = f"{instruction}\n{injected_context}"
        initial_result = await self.orchestrator.universal_agent.act(full_instruction, worker_context)
        
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

    async def _decompose(self, task: str, task_type: str = "general", context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Determine the swarm structure based on the task type"""
        context = context or {}
        
        # Deterministic decomposition for core platform features
        if task_type == "full_project_generation":
            return [
                {"domain": "backend", "instruction": f"Generate backend for: {task}", "model": "coder"},
                {"domain": "frontend", "instruction": f"Generate frontend for: {task}", "model": "coder"},
                {"domain": "database", "instruction": f"Generate DB schema for: {task}", "model": "specialist"},
                {"domain": "infrastructure", "instruction": f"Generate Docker orchestration for: {task}", "model": "smart"}
            ]
        elif task_type in ["migration", "project_migration"]:
            target_arch = context.get("target_architecture", "Clean Architecture")
            return [
                {"domain": "audit", "instruction": f"Perform deep forensic audit and bug detection on: {task}", "model": "smart"},
                {"domain": "architecture", "instruction": f"Plan {target_arch} blueprint and domain mapping for: {task}", "model": "specialist"},
                {"domain": "migration", "instruction": f"Heal bugs and migrate core logic using {target_arch} best practices: {task}", "model": "coder"},
                {"domain": "infrastructure", "instruction": f"Containerize target environment with optimized CI/CD: {task}", "model": "smart"}
            ]
        elif task_type in ["self_healing", "fix"]:
            return [
                {"domain": "audit", "instruction": f"Locate root cause for: {task}", "model": "smart"},
                {"domain": "fix", "instruction": f"Implement secure fix for: {task}", "model": "coder"}
            ]
            
        # Dynamic decomposition fallback
        # Use a direct LLM call instead of orchestrator.run_inference to avoid circular dependency
        prompt = f"Return a JSON list of subtasks (keys: domain, instruction, model) to solve: {task}"
        
        try:
            if hasattr(self.orchestrator, 'llm') and self.orchestrator.llm:
                response = await self.orchestrator.llm.generate(
                    prompt=prompt,
                    model="qwen2.5-coder:7b",
                    max_tokens=2000
                )
                res_str = response if isinstance(response, str) else response.get("solution", "[]")
                match = re.search(r'\[.*\]', res_str, re.DOTALL)
                return json.loads(match.group(0)) if match else [{"domain": "general", "instruction": task, "model": "coder"}]
            return [{"domain": "general", "instruction": task, "model": "coder"}]
        except Exception as e:
            logger.error(f"Dynamic decomposition failed: {e}")
            return [{"domain": "general", "instruction": task, "model": "coder"}]
