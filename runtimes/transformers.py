"""
Transformers Runtime - Direct integration with HuggingFace Transformers
"""
import logging
import yaml
import torch
from typing import Dict, Any, AsyncGenerator, Optional
from pathlib import Path
from runtimes.base import BaseRuntime

logger = logging.getLogger(__name__)


class TransformersRuntime(BaseRuntime):
    """HuggingFace Transformers runtime implementation"""
    
    def __init__(self, config_path: str = "config"):
        super().__init__(config_path)
        self.models = {}
        self.tokenizers = {}
        self.device = None
        
    async def initialize(self) -> bool:
        """Initialize Transformers runtime"""
        try:
            config_file = Path(self.config_path) / "runtimes.yaml"
            with open(config_file, 'r') as f:
                runtimes_config = yaml.safe_load(f)
                self.config = runtimes_config.get("runtimes", {}).get("transformers", {}).get("config", {})
                
            # Set device
            device_config = self.config.get("device", "cuda")
            if device_config == "cuda" and torch.cuda.is_available():
                self.device = "cuda"
            else:
                self.device = "cpu"
                
            self.is_initialized = True
            logger.info(f"Transformers runtime initialized on {self.device}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Transformers runtime: {e}")
            return False
            
    async def shutdown(self):
        """Shutdown Transformers runtime"""
        # Unload all models
        for model_name in list(self.models.keys()):
            await self.unload_model(model_name)
            
        self.is_initialized = False
        logger.info("Transformers runtime shut down")
        
    async def load_model(self, model_name: str) -> Dict[str, Any]:
        """Load a model"""
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
            
            logger.info(f"Loading model {model_name}...")
            
            # Load tokenizer
            tokenizer = AutoTokenizer.from_pretrained(
                model_name,
                trust_remote_code=self.config.get("trust_remote_code", True)
            )
            
            # Load model
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                device_map=self.config.get("device_map", "auto"),
                torch_dtype=getattr(torch, self.config.get("torch_dtype", "float16")),
                trust_remote_code=self.config.get("trust_remote_code", True),
                low_cpu_mem_usage=self.config.get("low_cpu_mem_usage", True)
            )
            
            self.models[model_name] = model
            self.tokenizers[model_name] = tokenizer
            self.loaded_models.add(model_name)
            
            logger.info(f"Model {model_name} loaded successfully")
            return {"status": "loaded", "model": model_name}
            
        except Exception as e:
            logger.error(f"Error loading model {model_name}: {e}")
            return {"status": "error", "message": str(e)}
            
    async def unload_model(self, model_name: str) -> Dict[str, Any]:
        """Unload a model"""
        try:
            if model_name in self.models:
                # Move model to CPU and delete
                if hasattr(self.models[model_name], 'cpu'):
                    self.models[model_name].cpu()
                del self.models[model_name]
                
            if model_name in self.tokenizers:
                del self.tokenizers[model_name]
                
            if model_name in self.loaded_models:
                self.loaded_models.remove(model_name)
                
            # Clear CUDA cache if using GPU
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                
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
            if model not in self.models:
                await self.load_model(model)
                
            model_obj = self.models[model]
            tokenizer = self.tokenizers[model]
            
            # Tokenize input
            inputs = tokenizer(prompt, return_tensors="pt")
            if self.device == "cuda":
                inputs = inputs.to("cuda")
                
            # Generate
            with torch.no_grad():
                outputs = model_obj.generate(
                    **inputs,
                    max_new_tokens=kwargs.get("max_tokens", 2048),
                    temperature=kwargs.get("temperature", 0.7),
                    top_p=kwargs.get("top_p", 0.9),
                    top_k=kwargs.get("top_k", 40),
                    do_sample=kwargs.get("temperature", 0.7) > 0,
                    pad_token_id=tokenizer.eos_token_id
                )
                
            # Decode output
            output_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Remove prompt from output
            if output_text.startswith(prompt):
                output_text = output_text[len(prompt):]
                
            return {
                "output": output_text.strip(),
                "tokens": len(outputs[0]),
                "model": model
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
            if model not in self.models:
                await self.load_model(model)
                
            from transformers import TextIteratorStreamer
            import threading
            import json
            
            model_obj = self.models[model]
            tokenizer = self.tokenizers[model]
            
            inputs = tokenizer(prompt, return_tensors="pt")
            if self.device == "cuda":
                inputs = inputs.to("cuda")
                
            streamer = TextIteratorStreamer(tokenizer, skip_special_tokens=True)
            
            generation_kwargs = {
                **inputs,
                "max_new_tokens": kwargs.get("max_tokens", 2048),
                "temperature": kwargs.get("temperature", 0.7),
                "top_p": kwargs.get("top_p", 0.9),
                "streamer": streamer,
                "do_sample": kwargs.get("temperature", 0.7) > 0
            }
            
            thread = threading.Thread(target=model_obj.generate, kwargs=generation_kwargs)
            thread.start()
            
            for text in streamer:
                yield json.dumps({"text": text})
                
        except Exception as e:
            logger.error(f"Streaming generation error: {e}")
            yield json.dumps({"error": str(e)})
            
    async def health_check(self) -> bool:
        """Check runtime health"""
        try:
            import transformers
            return True
        except:
            return False