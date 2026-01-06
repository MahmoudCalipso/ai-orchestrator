"""
Ollama Runtime - Integration with Ollama
"""
import logging
import httpx
import yaml
import json
from typing import Dict, Any, AsyncGenerator
from pathlib import Path
from runtimes.base import BaseRuntime

logger = logging.getLogger(__name__)


class OllamaRuntime(BaseRuntime):
    """Ollama runtime implementation"""
    
    def __init__(self, config_path: str = "config"):
        super().__init__(config_path)
        self.client = None
        self.base_url = None
        
    async def initialize(self) -> bool:
        """Initialize Ollama runtime"""
        try:
            # Load config
            config_file = Path(self.config_path) / "runtimes.yaml"
            with open(config_file, 'r') as f:
                runtimes_config = yaml.safe_load(f)
                self.config = runtimes_config.get("runtimes", {}).get("ollama", {}).get("config", {})
                
            host = self.config.get("host", "localhost")
            port = self.config.get("port", 11434)
            self.base_url = f"http://{host}:{port}"
            
            self.client = httpx.AsyncClient(timeout=self.config.get("timeout", 300))
            
            # Test connection
            healthy = await self.health_check()
            if healthy:
                self.is_initialized = True
                logger.info("Ollama runtime initialized successfully")
                return True
            else:
                logger.warning("Ollama runtime is not healthy")
                return False
                
        except Exception as e:
            logger.error(f"Failed to initialize Ollama runtime: {e}")
            return False
            
    async def shutdown(self):
        """Shutdown Ollama runtime"""
        if self.client:
            await self.client.aclose()
        self.is_initialized = False
        logger.info("Ollama runtime shut down")
        
    async def load_model(self, model_name: str) -> Dict[str, Any]:
        """Load a model in Ollama"""
        try:
            # In Ollama, models are loaded on-demand, but we can pull them
            response = await self.client.post(
                f"{self.base_url}/api/pull",
                json={"name": model_name},
                timeout=600.0
            )
            
            if response.status_code == 200:
                self.loaded_models.add(model_name)
                return {"status": "loaded", "model": model_name}
            else:
                logger.error(f"Failed to load model: {response.text}")
                return {"status": "error", "message": response.text}
                
        except Exception as e:
            logger.error(f"Error loading model {model_name}: {e}")
            return {"status": "error", "message": str(e)}
            
    async def unload_model(self, model_name: str) -> Dict[str, Any]:
        """Unload a model from Ollama"""
        # Ollama doesn't have explicit unload, just remove from tracking
        if model_name in self.loaded_models:
            self.loaded_models.remove(model_name)
            
        return {"status": "unloaded", "model": model_name}
        
    async def generate(
        self,
        model: str,
        prompt: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate text using Ollama"""
        try:
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": kwargs.get("temperature", 0.7),
                    "top_p": kwargs.get("top_p", 0.9),
                    "top_k": kwargs.get("top_k", 40),
                    "num_predict": kwargs.get("max_tokens", 2048),
                }
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/generate",
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                
                output = result.get("response", "")
                
                return {
                    "output": output,
                    "tokens": self._count_tokens(output),
                    "model": model,
                    "done": result.get("done", True)
                }
            else:
                raise RuntimeError(f"Ollama generation failed: {response.text}")
                
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
                "stream": True,
                "options": {
                    "temperature": kwargs.get("temperature", 0.7),
                    "top_p": kwargs.get("top_p", 0.9),
                }
            }
            
            async with self.client.stream(
                "POST",
                f"{self.base_url}/api/generate",
                json=payload
            ) as response:
                async for line in response.aiter_lines():
                    if line:
                        try:
                            chunk = json.loads(line)
                            if "response" in chunk:
                                yield json.dumps({"text": chunk["response"]})
                        except json.JSONDecodeError:
                            continue
                            
        except Exception as e:
            logger.error(f"Streaming generation error: {e}")
            yield json.dumps({"error": str(e)})
            
    async def health_check(self) -> bool:
        """Check Ollama health"""
        try:
            response = await self.client.get(f"{self.base_url}/api/tags")
            return response.status_code == 200
        except:
            return False