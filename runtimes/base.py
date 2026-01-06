"""
Base Runtime - Abstract base class for all runtimes
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, AsyncGenerator
import logging

logger = logging.getLogger(__name__)


class BaseRuntime(ABC):
    """Abstract base class for inference runtimes"""
    
    def __init__(self, config_path: str = "config"):
        self.config_path = config_path
        self.config = {}
        self.loaded_models = set()
        self.is_initialized = False
        
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the runtime"""
        pass
        
    @abstractmethod
    async def shutdown(self):
        """Shutdown the runtime"""
        pass
        
    @abstractmethod
    async def load_model(self, model_name: str) -> Dict[str, Any]:
        """Load a model"""
        pass
        
    @abstractmethod
    async def unload_model(self, model_name: str) -> Dict[str, Any]:
        """Unload a model"""
        pass
        
    @abstractmethod
    async def generate(
        self,
        model: str,
        prompt: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate text"""
        pass
        
    @abstractmethod
    async def generate_stream(
        self,
        model: str,
        prompt: str,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Generate text with streaming"""
        pass
        
    @abstractmethod
    async def health_check(self) -> bool:
        """Check if runtime is healthy"""
        pass
        
    async def is_model_loaded(self, model_name: str) -> bool:
        """Check if model is loaded"""
        return model_name in self.loaded_models
        
    async def get_loaded_models(self) -> List[str]:
        """Get list of loaded models"""
        return list(self.loaded_models)
        
    def _count_tokens(self, text: str) -> int:
        """Rough token count estimation"""
        return len(text.split()) * 1.3  # Approximate
        
    async def get_runtime_info(self) -> Dict[str, Any]:
        """Get runtime information"""
        return {
            "name": self.__class__.__name__,
            "initialized": self.is_initialized,
            "loaded_models": list(self.loaded_models),
            "config": self.config
        }