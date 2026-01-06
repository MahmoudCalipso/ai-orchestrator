"""
Planner - Creates execution plans for tasks
"""
import logging
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class Planner:
    """Creates and manages execution plans"""
    
    def __init__(self, config_path: str = "config"):
        self.config_path = Path(config_path)
        
    async def create_plan(
        self,
        task_type: str,
        model: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create an execution plan for a task"""
        
        plan = {
            "task_type": task_type,
            "complexity": await self._assess_complexity(task_type, context),
            "recommended_model": await self._recommend_model(task_type, context),
            "estimated_tokens": await self._estimate_tokens(context),
            "estimated_time": await self._estimate_time(task_type, context),
            "resources_required": await self._estimate_resources(task_type, model)
        }
        
        return plan
        
    async def _assess_complexity(
        self,
        task_type: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Assess task complexity"""
        
        complex_tasks = ["reasoning", "data_analysis", "code_review"]
        simple_tasks = ["chat", "quick_query"]
        
        if task_type in complex_tasks:
            return "complex"
        elif task_type in simple_tasks:
            return "simple"
        else:
            return "moderate"
            
    async def _recommend_model(
        self,
        task_type: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Recommend best model for task"""
        
        task_model_map = {
            "code_generation": "deepseek-coder",
            "code_review": "qwen2.5",
            "reasoning": "qwen2.5",
            "quick_query": "mistral",
            "creative_writing": "llama3.1",
            "data_analysis": "qwen2.5",
            "documentation": "llama3.1",
            "chat": "mistral"
        }
        
        return task_model_map.get(task_type, "mistral")
        
    async def _estimate_tokens(
        self,
        context: Optional[Dict[str, Any]] = None
    ) -> int:
        """Estimate token usage"""
        
        if not context:
            return 2048
            
        # Simple estimation based on input length
        prompt_length = len(context.get("prompt", ""))
        estimated = (prompt_length // 4) + 1000  # Rough estimate
        
        return min(estimated, 8192)
        
    async def _estimate_time(
        self,
        task_type: str,
        context: Optional[Dict[str, Any]] = None
    ) -> float:
        """Estimate processing time in seconds"""
        
        complexity_time = {
            "simple": 5.0,
            "moderate": 15.0,
            "complex": 30.0
        }
        
        complexity = await self._assess_complexity(task_type, context)
        return complexity_time.get(complexity, 15.0)
        
    async def _estimate_resources(
        self,
        task_type: str,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """Estimate required resources"""
        
        from core.registry import ModelRegistry
        
        registry = ModelRegistry(self.config_path)
        await registry.load_models()
        
        if model:
            model_info = registry.get_model(model)
            if model_info:
                return {
                    "memory": model_info.get("memory_requirement"),
                    "gpu": True,
                    "context_window": model_info.get("context_length")
                }
                
        return {
            "memory": "6gb",
            "gpu": True,
            "context_window": 4096
        }