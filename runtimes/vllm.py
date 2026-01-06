"""
vLLM Runtime - Integration with vLLM
"""
import logging
import httpx
import yaml
import json
from typing import Dict, Any, AsyncGenerator
from pathlib import Path
from runtimes.base import BaseRuntime

logger = logging.getLogger(__name__)


class VLLMRuntime(BaseRuntime):
    """vLLM runtime implementation"""
    
    def __init__(self, config_path: str = "config"):
        super().__init__(config_path)
        self.client = None
        self.base_url = None
        
    async def initialize(self) -> bool:
        """Initialize vLLM runtime"""
        try:
            config_file = Path(self.config_path) / "runtimes.yaml"
            with open(config_file, 'r') as f:
                runtimes_config = yaml.safe_load(f)
                self.config = runtimes_config.get("runtimes", {}).get("vllm", {}).get("config", {})
                
            host = self.config.get("host", "localhost")
            port = self.config.get("port", 8000)
            self.base_url = f"http://{host}:{port}"
            
            self.client = httpx.AsyncClient(timeout=self.config.get("timeout", 600))
            
            healthy = await self.health_check()
            if healthy:
                self.is_initialized = True
                logger.info("vLLM runtime initialized successfully")
                return True
            else:
                logger.warning("vLLM runtime is not healthy")
                return False
                
        except Exception as e:
            logger.error(f"Failed to initialize vLLM runtime: {e}")
            return False
            
    async def shutdown(self):
        """Shutdown vLLM runtime"""
        if self.client:
            await self.client.aclose()
        self.is_initialized = False
        logger.info("vLLM runtime shut down")
        
    async def load_model(self, model_name: str) -> Dict[str, Any]:
        """Load model (vLLM loads on server start)"""
        # vLLM typically runs with one model loaded at server start
        # Track as loaded if server is running
        self.loaded_models.add(model_name)
        return {"status": "loaded", "model": model_name}
        
    async def unload_model(self, model_name: str) -> Dict[str, Any]:
        """Unload model"""
        if model_name in self.loaded_models:
            self.loaded_models.remove(model_name)
        return {"status": "unloaded", "model": model_name}
        
    async def generate(
        self,
        model: str,
        prompt: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate text using vLLM"""
        try:
            payload = {
                "model": model,
                "prompt": prompt,
                "max_tokens": kwargs.get("max_tokens", 2048),
                "temperature": kwargs.get("temperature", 0.7),
                "top_p": kwargs.get("top_p", 0.9),
                "stream": False
            }
            
            response = await self.client.post(
                f"{self.base_url}/v1/completions",
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                choice = result["choices"][0]
                output = choice["text"]
                
                return {
                    "output": output,
                    "tokens": result.get("usage", {}).get("total_tokens", 0),
                    "model": model,
                    "finish_reason": choice.get("finish_reason")
                }
            else:
                raise RuntimeError(f"vLLM generation failed: {response.text}")
                
        except Exception as e:
            logger.error(f"Generation error: {e}")
            raise
            
    async def generate_stream(
        self,
        model: str,
        prompt: str,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Generate text with streaming"""
        try:
            payload = {
                "model": model,
                "prompt": prompt,
                "max_tokens": kwargs.get("max_tokens", 2048),
                "temperature": kwargs.get("temperature", 0.7),
                "top_p": kwargs.get("top_p", 0.9),
                "stream": True
            }
            
            async with self.client.stream(
                "POST",
                f"{self.base_url}/v1/completions",
                json=payload
            ) as response:
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]  # Remove "data: " prefix
                        if data.strip() == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data)
                            if chunk["choices"]:
                                text = chunk["choices"][0].get("text", "")
                                if text:
                                    yield json.dumps({"text": text})
                        except json.JSONDecodeError:
                            continue
                            
        except Exception as e:
            logger.error(f"Streaming generation error: {e}")
            yield json.dumps({"error": str(e)})
            
    async def health_check(self) -> bool:
        """Check vLLM health"""
        try:
            response = await self.client.get(f"{self.base_url}/health")
            return response.status_code == 200
        except:
            return False