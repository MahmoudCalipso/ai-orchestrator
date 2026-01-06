"""
Model Registry - Manages model metadata and availability
"""
import logging
import yaml
from typing import Dict, Any, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class ModelRegistry:
    """Registry for managing model information"""
    
    def __init__(self, config_path: str = "config"):
        self.config_path = Path(config_path)
        self.models: Dict[str, Dict[str, Any]] = {}
        self.aliases: Dict[str, str] = {}
        
    async def load_models(self):
        """Load model configurations from file"""
        models_file = self.config_path / "models.yaml"
        
        try:
            with open(models_file, 'r') as f:
                config = yaml.safe_load(f)
                self.models = config.get("models", {})
                self.aliases = config.get("aliases", {})
                
            logger.info(f"Loaded {len(self.models)} models from registry")
            
        except FileNotFoundError:
            logger.warning(f"Models config not found at {models_file}, using defaults")
            self.models = self._get_default_models()
            
        except Exception as e:
            logger.error(f"Failed to load models config: {e}")
            self.models = self._get_default_models()
            
    def _get_default_models(self) -> Dict[str, Dict[str, Any]]:
        """Get default model configurations"""
        return {
            "mistral": {
                "family": "mistral",
                "size": "7b",
                "context_length": 32768,
                "capabilities": ["general", "fast"],
                "specialization": "quick_tasks",
                "memory_requirement": "6gb",
                "recommended_runtime": ["ollama", "llamacpp"]
            },
            "phi3": {
                "family": "phi",
                "size": "3.8b",
                "context_length": 128000,
                "capabilities": ["general", "efficient"],
                "specialization": "resource_efficient",
                "memory_requirement": "4gb",
                "recommended_runtime": ["ollama", "llamacpp"]
            }
        }
        
    def get_model(self, name: str) -> Optional[Dict[str, Any]]:
        """Get model information by name or alias"""
        
        # Check if it's an alias
        if name in self.aliases:
            name = self.aliases[name]
            
        return self.models.get(name)
        
    def list_models(self) -> List[str]:
        """List all available model names"""
        return list(self.models.keys())
        
    def list_models_detailed(self) -> List[Dict[str, Any]]:
        """List all models with detailed information"""
        result = []
        for name, info in self.models.items():
            model_data = {
                "name": name,
                **info,
                "status": "available"
            }
            result.append(model_data)
        return result
        
    def get_models_by_family(self, family: str) -> List[str]:
        """Get all models from a specific family"""
        return [
            name for name, info in self.models.items()
            if info.get("family") == family
        ]
        
    def get_models_by_capability(self, capability: str) -> List[str]:
        """Get all models with a specific capability"""
        return [
            name for name, info in self.models.items()
            if capability in info.get("capabilities", [])
        ]
        
    def get_models_by_specialization(self, specialization: str) -> List[str]:
        """Get all models with a specific specialization"""
        return [
            name for name, info in self.models.items()
            if info.get("specialization") == specialization
        ]
        
    def filter_models(
        self,
        max_memory: Optional[str] = None,
        min_context: Optional[int] = None,
        capabilities: Optional[List[str]] = None,
        runtime: Optional[str] = None
    ) -> List[str]:
        """Filter models based on criteria"""
        
        filtered = []
        
        for name, info in self.models.items():
            # Check memory requirement
            if max_memory:
                mem_req = info.get("memory_requirement", "")
                mem_value = int(''.join(filter(str.isdigit, mem_req)))
                max_value = int(''.join(filter(str.isdigit, max_memory)))
                if mem_value > max_value:
                    continue
                    
            # Check context length
            if min_context:
                if info.get("context_length", 0) < min_context:
                    continue
                    
            # Check capabilities
            if capabilities:
                model_caps = info.get("capabilities", [])
                if not all(cap in model_caps for cap in capabilities):
                    continue
                    
            # Check runtime support
            if runtime:
                if runtime not in info.get("recommended_runtime", []):
                    continue
                    
            filtered.append(name)
            
        return filtered
        
    def resolve_alias(self, name: str) -> str:
        """Resolve model alias to actual model name"""
        return self.aliases.get(name, name)
        
    def add_model(self, name: str, config: Dict[str, Any]):
        """Add a new model to the registry"""
        self.models[name] = config
        logger.info(f"Added model '{name}' to registry")
        
    def remove_model(self, name: str):
        """Remove a model from the registry"""
        if name in self.models:
            del self.models[name]
            logger.info(f"Removed model '{name}' from registry")
            
    def update_model(self, name: str, updates: Dict[str, Any]):
        """Update model configuration"""
        if name in self.models:
            self.models[name].update(updates)
            logger.info(f"Updated model '{name}' in registry")