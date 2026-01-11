"""
LlamaCpp Runtime - Integration with llama.cpp Python bindings
"""
import logging
import yaml
import json
from typing import Dict, Any, AsyncGenerator
from pathlib import Path
from runtimes.base import BaseRuntime

logger = logging.getLogger(__name__)


class LlamaCppRuntime(BaseRuntime):
    """llama.cpp runtime implementation"""
    
    def __init__(self, config_path: str = "config"):
        super().__init__(config_path)
        self.llama_models = {}
        
    async def initialize(self) -> bool:
        """Initialize llama.cpp runtime"""
        try:
            config_file = Path(self.config_path) / "runtimes.yaml"
            with open(config_file, 'r') as f:
                runtimes_config = yaml.safe_load(f)
                self.config = runtimes_config.get("runtimes", {}).get("llamacpp", {}).get("config", {})
                
            self.is_initialized = True
            logger.info("llama.cpp runtime initialized")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize llama.cpp runtime: {e}")
            return False
            
    async def shutdown(self):
        """Shutdown llama.cpp runtime"""
        for model_name in list(self.llama_models.keys()):
            await self.unload_model(model_name)
            
        self.is_initialized = False
        logger.info("llama.cpp runtime shut down")
        
    async def load_model(self, model_name: str) -> Dict[str, Any]:
        """Load a GGUF model"""
        try:
            from llama_cpp import Llama
            
            logger.info(f"Loading model {model_name}...")
            
            # Assume model file is in models directory
            model_path = Path("models") / f"{model_name}.gguf"
            
            if not model_path.exists():
                return {"status": "error", "message": f"Model file not found: {model_path}"}
                
            llama = Llama(
                model_path=str(model_path),
                n_ctx=self.config.get("n_ctx", 8192),
                n_batch=self.config.get("n_batch", 512),
                n_threads=self.config.get("n_threads", 8),
                n_gpu_layers=self.config.get("n_gpu_layers", -1),
                use_mmap=self.config.get("use_mmap", True),
                use_mlock=self.config.get("use_mlock", False),
                verbose=self.config.get("verbose", False)
            )
            
            self.llama_models[model_name] = llama
            self.loaded_models.add(model_name)
            
            logger.info(f"Model {model_name} loaded successfully")
            return {"status": "loaded", "model": model_name}
            
        except Exception as e:
            logger.error(f"Error loading model {model_name}: {e}")
            return {"status": "error", "message": str(e)}
            
    async def unload_model(self, model_name: str) -> Dict[str, Any]:
        """Unload a model"""
        try:
            if model_name in self.llama_models:
                del self.llama_models[model_name]
                
            if model_name in self.loaded_models:
                self.loaded_models.remove(model_name)
                
            logger.info(f"Model {model_name} unloaded")
            return {"status": "unloaded", "model": model_name}
            
        except Exception as e:
            logger.error(f"Error unloading model {model_name}: {e}")
            return {"status": "error", "message": str(e)}
            
    async def generate(
        self,
        model: str,
        prompt: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate text"""
        try:
            if model not in self.llama_models:
                await self.load_model(model)
                
            llama = self.llama_models[model]
            
            output = llama(
                prompt,
                max_tokens=kwargs.get("max_tokens", 2048),
                temperature=kwargs.get("temperature", 0.7),
                top_p=kwargs.get("top_p", 0.9),
                top_k=kwargs.get("top_k", 40),
                repeat_penalty=kwargs.get("repetition_penalty", 1.0),
                stop=kwargs.get("stop_sequences", []),
                echo=False
            )
            
            generated_text = output["choices"][0]["text"]
            
            return {
                "output": generated_text,
                "tokens": output["usage"]["total_tokens"],
                "model": model,
                "finish_reason": output["choices"][0].get("finish_reason")
            }
            
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
            if model not in self.llama_models:
                await self.load_model(model)
                
            llama = self.llama_models[model]
            
            stream = llama(
                prompt,
                max_tokens=kwargs.get("max_tokens", 2048),
                temperature=kwargs.get("temperature", 0.7),
                top_p=kwargs.get("top_p", 0.9),
                top_k=kwargs.get("top_k", 40),
                stream=True,
                echo=False
            )
            
            for output in stream:
                if "choices" in output and output["choices"]:
                    text = output["choices"][0].get("text", "")
                    if text:
                        yield json.dumps({"text": text})
                        
        except Exception as e:
            logger.error(f"Streaming generation error: {e}")
            yield json.dumps({"error": str(e)})
            
    async def health_check(self) -> bool:
        """Check runtime health"""
        try:
            return True
        except:
            return False