"""
CORE LLM INFERENCE ENGINE - Open Source Edition (2026)
Strictly focused on Free & Open Source AI models via Ollama.
"""
import logging
import os
import time
import json
from services.monitoring.calt_service import CALTLogger

logger = logging.getLogger(__name__)

class LLMInference:
    """
    LLM Inference Engine
    Optimized for FREE & OPEN SOURCE Models.
    Primary Provider: Ollama (Local/Self-hosted)
    """
    
    def __init__(self, provider: str = "ollama", model: str = None, api_key: str = None):
        # ... existing config ...
        self.provider = "ollama"
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
        self.model = model or os.getenv("OLLAMA_MODEL", "qwen2.5-coder:7b")
        self.calt = CALTLogger()
        
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
        """Generate response with CALT tracking"""
        start_time = time.time()
        target_model = model or self.model
        
        try:
            # ... execution ...
            result = await self._execute_generate(prompt, max_tokens, temperature, system_prompt, target_model)
            
            # CALT Tracking
            duration = time.time() - start_time
            tokens_in = len(prompt.split()) # Rough estimation
            tokens_out = len(result.split())
            self.calt.log_operation("LLM_GENERATE", duration, tokens_in, tokens_out, {"model": target_model})
            
            return result
        except Exception as e:
            logger.error(f"Generate error: {e}")
            return "Error during generation"

    async def _execute_generate(self, prompt, max_tokens, temp, system, model):
        # Actual implementation moved here to keep generate() clean for logging
        from openai import OpenAI
        target_client = OpenAI(base_url=f"{self.base_url}/v1", api_key="ollama")
        
        messages = []
        if system: messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        response = target_client.chat.completions.create(
            model=model, messages=messages, max_tokens=max_tokens, temperature=temp
        )
        return response.choices[0].message.content

    async def generate_streaming(
        self,
        prompt: str,
        max_tokens: int = 8000,
        temperature: float = 0.3,
        system_prompt: str = None,
        model: str = None
    ) -> AsyncGenerator[str, None]:
        """Generate streaming response with CALT tracking"""
        start_time = time.time()
        total_content = []
        
        async for chunk in self._execute_stream(prompt, max_tokens, temperature, system_prompt, model or self.model):
            total_content.append(chunk)
            yield chunk
            
        # CALT Tracking after stream completes
        duration = time.time() - start_time
        tokens_in = len(prompt.split())
        tokens_out = len("".join(total_content).split())
        self.calt.log_operation("LLM_STREAM", duration, tokens_in, tokens_out, {"model": model or self.model})

    async def _execute_stream(self, prompt, max_tokens, temp, system, model):
        from openai import OpenAI
        target_client = OpenAI(base_url=f"{self.base_url}/v1", api_key="ollama")
        
        messages = []
        if system: messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        stream = target_client.chat.completions.create(
            model=model, messages=messages, max_tokens=max_tokens, temperature=temp, stream=True
        )
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

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
