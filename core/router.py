"""
Router - Intelligent request routing
"""
import logging
import yaml
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class Router:
    """Intelligent request router"""
    
    def __init__(self, config_path: str = "config"):
        self.config_path = Path(config_path)
        self.policies = {}
        self.routing_cache = {}
        
    async def load_policies(self):
        """Load routing policies from config"""
        policies_file = self.config_path / "policies.yaml"
        
        try:
            with open(policies_file, 'r') as f:
                config = yaml.safe_load(f)
                self.policies = config.get("policies", {})
            logger.info("Routing policies loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load routing policies: {e}")
            self.policies = self._get_default_policies()
            
    def _get_default_policies(self) -> Dict[str, Any]:
        """Get default routing policies"""
        return {
            "routing": {
                "by_task_type": {
                    "code_generation": {
                        "models": ["deepseek-coder", "codellama"],
                        "temperature": 0.2
                    },
                    "chat": {
                        "models": ["mistral", "phi3"],
                        "temperature": 0.7
                    }
                }
            }
        }
        
    async def route(
        self,
        task_type: str,
        model: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Route request to appropriate model and runtime"""
        
        # If model is explicitly specified, use it
        if model:
            selected_model = model
        else:
            # Select based on task type
            task_policies = self.policies.get("routing", {}).get("by_task_type", {})
            task_config = task_policies.get(task_type, {})
            
            models = task_config.get("models", ["mistral"])
            selected_model = models[0]  # Select first available
            
        # Determine runtime
        runtime = await self._select_runtime(selected_model, context)
        
        # Get parameters
        parameters = await self._get_parameters(task_type, context)
        
        return {
            "model": selected_model,
            "runtime": runtime,
            "parameters": parameters
        }
        
    async def _select_runtime(
        self,
        model: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Select best runtime for the model"""
        
        # Load model info to get recommended runtimes
        from core.registry import ModelRegistry
        registry = ModelRegistry(self.config_path)
        await registry.load_models()
        
        model_info = registry.get_model(model)
        if not model_info:
            return "ollama"  # Default
            
        recommended = model_info.get("recommended_runtime", ["ollama"])
        
        # Check context for runtime preference
        if context and "preferred_runtime" in context:
            preferred = context["preferred_runtime"]
            if preferred in recommended:
                return preferred
                
        return recommended[0]
        
    async def _get_parameters(
        self,
        task_type: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Get inference parameters based on task type"""
        
        task_policies = self.policies.get("routing", {}).get("by_task_type", {})
        task_config = task_policies.get(task_type, {})
        
        parameters = {
            "temperature": task_config.get("temperature", 0.7),
            "top_p": task_config.get("top_p", 0.9),
            "max_tokens": task_config.get("max_tokens", 2048)
        }
        
        # Override with context if provided
        if context and "parameters" in context:
            parameters.update(context["parameters"])
            
        return parameters
        
    async def get_fallback(
        self,
        model: str,
        runtime: str
    ) -> Dict[str, str]:
        """Get fallback model and runtime"""
        
        fallback_config = self.policies.get("fallback", {})
        
        # Try to find alternative model from same family
        from core.registry import ModelRegistry
        registry = ModelRegistry(self.config_path)
        await registry.load_models()
        
        model_info = registry.get_model(model)
        if model_info:
            family = model_info.get("family")
            alternative_models = registry.get_models_by_family(family)
            
            for alt_model in alternative_models:
                if alt_model != model:
                    alt_info = registry.get_model(alt_model)
                    if alt_info:
                        recommended_runtimes = alt_info.get("recommended_runtime", [])
                        for rt in recommended_runtimes:
                            if rt != runtime:
                                return {
                                    "model": alt_model,
                                    "runtime": rt
                                }
        
        # Default fallback to fast model
        return {
            "model": "mistral",
            "runtime": "ollama"
        }