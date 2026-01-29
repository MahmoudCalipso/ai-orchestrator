"""
Unified LLM Service - Open-Source Models Only
Supports Ollama for local inference with tiered model configuration.
Zero API keys required, full data privacy.
"""
import os
import logging
import asyncio
from typing import Dict, List, Optional, AsyncGenerator
from enum import Enum
import httpx

logger = logging.getLogger(__name__)

class ModelTier(str, Enum):
    """Hardware-based model tiers."""
    MINIMAL = "minimal"      # 16GB RAM
    BALANCED = "balanced"    # 32GB RAM
    FULL = "full"           # 64GB+ RAM
    ULTRA = "ultra"         # 128GB+ RAM

class LLMService:
    """Unified LLM service using Ollama for local inference."""
    
    # Tiered Model Configuration (User-Specified + Enhanced)
    TIERS = {
        "minimal": [
            "qwen2.5-coder:7b",
            "glm4:9b",
            "phi3:3.8b",  # Added: Microsoft's efficient model
        ],
        "balanced": [
            "qwen2.5-coder:14b",
            "qwen2.5-coder:7b",
            "glm4:9b",
            "codellama:13b",
            "mistral:7b",  # Added: General purpose
            "phi3:14b",    # Added: Microsoft Phi-3 medium
        ],
        "full": [
            "qwen2.5-coder:32b",
            "deepseek-r1:32b-q4",
            "qwen2.5-coder:14b",
            "glm4:9b",
            "codellama:34b",      # Added: Larger CodeLlama
            "mixtral:8x7b",       # Added: Mistral MoE
            "starcoder2:15b",     # Added: Code-specific
        ],
        "ultra": [
            "qwen3:235b-q4",
            "deepseek-r1:70b-q4",
            "qwen2.5-coder:32b",
            "glm4:9b",
            "llama3.1:70b",       # Added: Meta's flagship
            "mixtral:8x22b",      # Added: Larger Mixtral
            "deepseek-coder:33b", # Added: DeepSeek code specialist
        ]
    }
    
    # Model capabilities mapping
    MODEL_CAPABILITIES = {
        "code": ["qwen2.5-coder", "codellama", "deepseek-coder", "starcoder2"],
        "chat": ["glm4", "mistral", "llama3.1", "qwen3", "phi3"],
        "reasoning": ["deepseek-r1", "qwen3"],
        "moe": ["mixtral"]  # Mixture of Experts
    }
    
    def __init__(
        self,
        ollama_base_url: str = "http://localhost:11434",
        tier: ModelTier = ModelTier.BALANCED,
        timeout: int = 120
    ):
        self.ollama_base_url = ollama_base_url
        self.tier = tier
        self.timeout = timeout
        self.available_models = self.TIERS[tier.value]
        self.client = httpx.AsyncClient(timeout=timeout)
        
        logger.info(f"LLM Service initialized with tier: {tier}, models: {self.available_models}")
    
    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        system_prompt: Optional[str] = None
    ) -> str:
        """Generate text using Ollama."""
        # Auto-select model if not specified
        if not model:
            model = self.available_models[0]  # Use primary model
        
        # Ensure model is in format expected by Ollama
        if ":" not in model and model in self.available_models:
            model = self.available_models[0]
        
        try:
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            }
            
            if system_prompt:
                payload["system"] = system_prompt
            
            response = await self.client.post(
                f"{self.ollama_base_url}/api/generate",
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            return result.get("response", "")
            
        except httpx.HTTPError as e:
            logger.error(f"Ollama generation failed: {e}")
            # Fallback to next available model
            if len(self.available_models) > 1:
                fallback_model = self.available_models[1]
                logger.info(f"Falling back to {fallback_model}")
                return await self.generate(prompt, fallback_model, temperature, max_tokens, system_prompt)
            raise
    
    async def generate_stream(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        system_prompt: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """Stream text generation using Ollama."""
        if not model:
            model = self.available_models[0]
        
        try:
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": True,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            }
            
            if system_prompt:
                payload["system"] = system_prompt
            
            async with self.client.stream(
                "POST",
                f"{self.ollama_base_url}/api/generate",
                json=payload
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line:
                        import json
                        chunk = json.loads(line)
                        if "response" in chunk:
                            yield chunk["response"]
                            
        except httpx.HTTPError as e:
            logger.error(f"Ollama streaming failed: {e}")
            raise
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> str:
        """Chat completion using Ollama."""
        if not model:
            model = self.available_models[0]
        
        try:
            payload = {
                "model": model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            }
            
            response = await self.client.post(
                f"{self.ollama_base_url}/api/chat",
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            return result.get("message", {}).get("content", "")
            
        except httpx.HTTPError as e:
            logger.error(f"Ollama chat failed: {e}")
            raise
    
    async def list_models(self) -> List[str]:
        """List available models in Ollama."""
        try:
            response = await self.client.get(f"{self.ollama_base_url}/api/tags")
            response.raise_for_status()
            
            result = response.json()
            models = [model["name"] for model in result.get("models", [])]
            return models
            
        except httpx.HTTPError as e:
            logger.error(f"Failed to list Ollama models: {e}")
            return []
    
    async def pull_model(self, model: str) -> bool:
        """Pull a model from Ollama registry."""
        try:
            logger.info(f"Pulling model: {model}")
            
            async with self.client.stream(
                "POST",
                f"{self.ollama_base_url}/api/pull",
                json={"name": model}
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line:
                        import json
                        status = json.loads(line)
                        logger.debug(f"Pull status: {status}")
            
            logger.info(f"Successfully pulled model: {model}")
            return True
            
        except httpx.HTTPError as e:
            logger.error(f"Failed to pull model {model}: {e}")
            return False
    
    async def ensure_models(self) -> bool:
        """Ensure all tier models are available, pull if missing."""
        available = await self.list_models()
        
        for model in self.available_models:
            if model not in available:
                logger.warning(f"Model {model} not found, pulling...")
                success = await self.pull_model(model)
                if not success:
                    logger.error(f"Failed to pull {model}")
                    return False
        
        return True
    
    def get_model_for_task(self, task_type: str) -> str:
        """Get best model for specific task type."""
        task_models = self.MODEL_CAPABILITIES.get(task_type, [])
        
        # Find first available model matching task
        for model_prefix in task_models:
            for available_model in self.available_models:
                if model_prefix in available_model:
                    return available_model
        
        # Fallback to primary model
        return self.available_models[0]
    
    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()

# Global singleton
_llm_service: Optional[LLMService] = None

def get_llm_service(tier: ModelTier = ModelTier.BALANCED) -> LLMService:
    """Get or create LLM service singleton."""
    global _llm_service
    if _llm_service is None:
        ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        _llm_service = LLMService(ollama_base_url=ollama_url, tier=tier)
    return _llm_service
