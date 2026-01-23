"""
CORE LLM INFERENCE ENGINE - Open Source Edition (2026)
Strictly focused on Free & Open Source AI models via Ollama.
"""
import logging
import os
import json
from typing import List, Dict, Any, Optional, AsyncGenerator
from openai import OpenAI

logger = logging.getLogger(__name__)

class LLMInference:
    """
    LLM Inference Engine
    Optimized for FREE & OPEN SOURCE Models.
    Primary Provider: Ollama (Local/Self-hosted)
    """
    
    def __init__(self, provider: str = "ollama", model: str = None, api_key: str = None):
        """
        Initialize LLM Inference Engine
        
        Args:
            provider: LLM provider (Defaults to ollama)
            model: Model name (e.g., qwen2.5-coder:7b)
            api_key: Not needed for open source models
        """
        # Hard default to Ollama for privacy and cost-efficiency
        self.provider = "ollama"
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
        self.model = model or os.getenv("OLLAMA_MODEL", "qwen2.5-coder:7b")
        
        # Initialize client (Ollama uses OpenAI-compatible API)
        try:
            self.client = OpenAI(
                base_url=f"{self.base_url}/v1",
                api_key="ollama"  # placeholder
            )
            logger.info(f"✓ Open-Source LLM initialized - Model: {self.model} (via Ollama)")
        except Exception as e:
            logger.error(f"Failed to initialize Open-Source LLM client: {e}")
            self.client = None

    async def generate(
        self,
        prompt: str,
        max_tokens: int = 8000,
        temperature: float = 0.3,
        system_prompt: str = None,
        model: str = None
    ) -> str:
        """Generate response from Open-Source LLM"""
        target_model = model or self.model
        
        if self.client is None:
            return self._mock_generate(prompt)
        
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            messages.append({"role": "user", "content": prompt})
            
            response = self.client.chat.completions.create(
                model=target_model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"LLM generation error (Ollama): {e}")
            return self._mock_generate(prompt)

    async def generate_streaming(
        self,
        prompt: str,
        max_tokens: int = 8000,
        temperature: float = 0.3,
        system_prompt: str = None,
        model: str = None
    ) -> AsyncGenerator[str, None]:
        """Generate streaming response from Open-Source LLM"""
        target_model = model or self.model
        
        if self.client is None:
            yield self._mock_generate(prompt)
            return
        
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            messages.append({"role": "user", "content": prompt})
            
            stream = self.client.chat.completions.create(
                model=target_model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            logger.error(f"Streaming error (Ollama): {e}")
            yield self._mock_generate(prompt)

    async def get_embeddings(self, text: str, model: str = None) -> List[float]:
        """Generate semantic embeddings via Open-Source model"""
        target_model = model or os.getenv("EMBEDDING_MODEL", "nomic-embed-text")
        
        if self.client is None:
            import random
            return [random.uniform(-1, 1) for _ in range(1536)]
            
        try:
            response = self.client.embeddings.create(
                input=text,
                model=target_model
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Embedding generation error (Ollama): {e}")
            import random
            return [random.uniform(-1, 1) for _ in range(1536)]

    def _mock_generate(self, prompt: str) -> str:
        """Mock fallback for offline mode"""
        return "## Analysis\nOpen Source Model is currently unavailable. Using fallback response.\n"

    def get_available_models(self) -> List[str]:
        """Get recommended open source models"""
        return [
            "qwen2.5-coder:7b",
            "qwen2.5-coder:32b",
            "deepseek-coder-v2:16b",
            "llama3.1:8b",
            "mistral-nemo:12b",
            "nomic-embed-text:latest"
        ]
