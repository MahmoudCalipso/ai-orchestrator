"""
Core Orchestrator - Main orchestration logic
"""
import time
import uuid
import logging
import os
from typing import Dict, Any, Optional, List, AsyncGenerator
from pathlib import Path

from core.router import Router
from core.planner import Planner
from core.registry import ModelRegistry
from core.memory.neural_memory import NeuralMemoryManager
from core.security import SecurityManager
from core.mcp.client import MCPManager
from core.state.blackboard import Blackboard
from core.workbench.manager import WorkbenchManager
from core.console.websocket_gateway import WebSocketGateway
from core.buildtools.universal_build import UniversalBuildSystem, PortForwardingManager
from core.llm.inference import LLMInference
from core.watcher.self_healing import SelfHealingService
from core.storage.manager import StorageManager
from core.lifecycle.project_lifecycle import ProjectLifecycleService
from services.git.credential_manager import GitCredentialManager
from agents.universal_ai_agent import UniversalAIAgent
from agents.lead_architect import LeadArchitectAgent
from runtimes.base import BaseRuntime
from runtimes.ollama import OllamaRuntime
from runtimes.vllm import VLLMRuntime
from runtimes.transformers import TransformersRuntime
from runtimes.llamacpp import LlamaCppRuntime

logger = logging.getLogger(__name__)


class Orchestrator:
    """Main orchestrator class for managing AI inference"""
    
    def __init__(self, config_path: str = "config"):
        self.config_path = Path(config_path)
        self.start_time = time.time()
        
        # Core components
        self.registry = ModelRegistry(config_path)
        self.router = Router(config_path)
        self.planner = Planner(config_path)
        self.memory = NeuralMemoryManager()
        self.security = SecurityManager()
        
        # LLM Engine (Default to free local Ollama)
        self.llm = LLMInference(
            provider=os.getenv("LLM_PROVIDER", "ollama"),
            model=os.getenv("LLM_MODEL", "qwen2.5-coder:7b")
        )
        
        # UNIVERSAL AI AGENT (Main Agent)
        self.universal_agent = UniversalAIAgent(orchestrator=self)
        logger.info("✓ Universal AI Agent initialized - Works with ANY language")
        
        # MCP and Agent Swarm
        self.mcp_manager = MCPManager()
        self.blackboard = Blackboard()
        self.storage = StorageManager()
        self.git_credentials = GitCredentialManager()
        self.lifecycle = ProjectLifecycleService(self)
        self.lead_architect = LeadArchitectAgent(self)
        
        # Universal Architecture
        self.workbench_manager = WorkbenchManager()
        self.websocket_gateway = WebSocketGateway(self.workbench_manager)
        self.build_system = UniversalBuildSystem()
        self.port_manager = PortForwardingManager()
        
        # Vision 2026: Self-Healing
        self.self_healing = SelfHealingService(self)
        
        # Runtime instances
        self.runtimes: Dict[str, BaseRuntime] = {}
        
        # Active tasks
        self.active_tasks: Dict[str, Dict[str, Any]] = {}
        
        # Metrics
        self.metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_tokens": 0,
            "total_processing_time": 0.0
        }
        
    async def initialize(self):
        """Initialize the orchestrator"""
        logger.info("Initializing orchestrator...")
        
        # Load configurations
        await self.registry.load_models()
        await self.router.load_policies()
        
        # Initialize runtimes
        await self._initialize_runtimes()
        
        # Initialize memory manager
        await self.memory.initialize()
        
        # Initialize Blackboard
        await self.blackboard.initialize()
        
        # Initialize MCP Servers (placeholder for dynamic config)
        await self.mcp_manager.register_server("system", "node", ["-e", "console.log('system tool')"])
        
        logger.info("Orchestrator initialized successfully")
        
    async def _initialize_runtimes(self):
        """Initialize all available runtimes"""
        runtime_classes = {
            "ollama": OllamaRuntime,
            "vllm": VLLMRuntime,
            "transformers": TransformersRuntime,
            "llamacpp": LlamaCppRuntime
        }
        
        for name, runtime_class in runtime_classes.items():
            try:
                runtime = runtime_class(self.config_path)
                if await runtime.initialize():
                    self.runtimes[name] = runtime
                    logger.info(f"Runtime '{name}' initialized successfully")
                else:
                    logger.warning(f"Runtime '{name}' failed to initialize")
            except Exception as e:
                logger.error(f"Failed to initialize runtime '{name}': {e}")
                
    async def shutdown(self):
        """Shutdown the orchestrator"""
        logger.info("Shutting down orchestrator...")
        
        # Shutdown all runtimes
        for name, runtime in self.runtimes.items():
            try:
                await runtime.shutdown()
                logger.info(f"Runtime '{name}' shut down")
            except Exception as e:
                logger.error(f"Error shutting down runtime '{name}': {e}")
                
        # Shutdown memory manager
        await self.memory.shutdown()
        
        logger.info("Orchestrator shut down complete")
        
    async def run_inference(
        self,
        prompt: str,
        task_type: str = "chat",
        model: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Run inference with automatic routing"""
        request_id = str(uuid.uuid4())
        start_time = time.time()
        
        try:
            self.metrics["total_requests"] += 1
            
            # PHASE 1: Use Lead Architect for swarm orchestration
            logger.info(f"Delegating inference to LeadArchitect: task={task_type}")
            swarm_result = await self.lead_architect.act(prompt, context)
            
            # If the swarm produced code/output, we can either return it directly
            # or continue with the legacy model-specific path if needed.
            # For this refactor, we transition to Swarm-first.
            
            return {
                "request_id": request_id,
                "status": "success",
                "swarm_output": swarm_result,
                "processing_time": time.time() - start_time
            }

            # LEGACY PATH (Disabled for Swarm transition)
            # Create execution plan
            plan = await self.planner.create_plan(
                task_type=task_type,
                model=model,
                context=context
            )
            
            # Route to appropriate model and runtime
            routing_decision = await self.router.route(
                task_type=task_type,
                model=model or plan.get("recommended_model"),
                context=context
            )
            
            selected_model = routing_decision["model"]
            selected_runtime = routing_decision["runtime"]
            
            # Get runtime instance
            runtime = self.runtimes.get(selected_runtime)
            if not runtime:
                raise RuntimeError(f"Runtime '{selected_runtime}' not available")
                
            # Check if runtime is healthy
            if not await runtime.health_check():
                # Try fallback
                fallback = await self.router.get_fallback(selected_model, selected_runtime)
                selected_model = fallback["model"]
                selected_runtime = fallback["runtime"]
                runtime = self.runtimes.get(selected_runtime)
                
            # Load model if needed
            if not await runtime.is_model_loaded(selected_model):
                await runtime.load_model(selected_model)
                
            # Prepare parameters
            params = parameters or {}
            
            # Run inference
            logger.info(f"Running inference: model={selected_model}, runtime={selected_runtime}")
            
            result = await runtime.generate(
                model=selected_model,
                prompt=prompt,
                **params
            )
            
            # Process result
            processing_time = time.time() - start_time
            
            # Update metrics
            self.metrics["successful_requests"] += 1
            self.metrics["total_tokens"] += result.get("tokens", 0)
            self.metrics["total_processing_time"] += processing_time
            
            # Store in memory if needed
            if context and context.get("save_to_memory"):
                await self.memory.store(
                    key=request_id,
                    value={
                        "prompt": prompt,
                        "output": result.get("output"),
                        "model": selected_model,
                        "timestamp": time.time()
                    }
                )
            
            return {
                "request_id": request_id,
                "model": selected_model,
                "runtime": selected_runtime,
                "output": result.get("output", ""),
                "tokens_used": result.get("tokens", 0),
                "processing_time": processing_time,
                "metadata": {
                    "plan": plan,
                    "routing": routing_decision
                }
            }
            
        except Exception as e:
            self.metrics["failed_requests"] += 1
            logger.error(f"Inference failed: {e}", exc_info=True)
            raise
            
    async def run_inference_stream(
        self,
        prompt: str,
        task_type: str = "chat",
        model: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> AsyncGenerator[str, None]:
        """Run streaming inference"""
        request_id = str(uuid.uuid4())
        
        try:
            # Route to model
            routing_decision = await self.router.route(
                task_type=task_type,
                model=model,
                context=context
            )
            
            selected_model = routing_decision["model"]
            selected_runtime = routing_decision["runtime"]
            
            runtime = self.runtimes.get(selected_runtime)
            if not runtime:
                raise RuntimeError(f"Runtime '{selected_runtime}' not available")
                
            # Load model if needed
            if not await runtime.is_model_loaded(selected_model):
                await runtime.load_model(selected_model)
                
            # Stream generation
            params = parameters or {}
            
            async for chunk in runtime.generate_stream(
                model=selected_model,
                prompt=prompt,
                **params
            ):
                yield chunk
                
        except Exception as e:
            logger.error(f"Streaming inference failed: {e}")
            yield f'{{"error": "{str(e)}"}}'
            
    async def load_model(self, model_name: str) -> Dict[str, Any]:
        """Load a specific model"""
        try:
            model_info = self.registry.get_model(model_name)
            if not model_info:
                raise ValueError(f"Model '{model_name}' not found in registry")
                
            # Determine best runtime for this model
            recommended_runtimes = model_info.get("recommended_runtime", [])
            runtime_name = None
            
            for rt in recommended_runtimes:
                if rt in self.runtimes:
                    runtime_name = rt
                    break
                    
            if not runtime_name:
                raise RuntimeError(f"No available runtime for model '{model_name}'")
                
            runtime = self.runtimes[runtime_name]
            result = await runtime.load_model(model_name)
            
            return {
                "model": model_name,
                "runtime": runtime_name,
                "status": "loaded",
                "details": result
            }
            
        except Exception as e:
            logger.error(f"Failed to load model '{model_name}': {e}")
            raise
            
    async def unload_model(self, model_name: str) -> Dict[str, Any]:
        """Unload a specific model"""
        try:
            # Find which runtime has this model loaded
            for runtime_name, runtime in self.runtimes.items():
                if await runtime.is_model_loaded(model_name):
                    result = await runtime.unload_model(model_name)
                    return {
                        "model": model_name,
                        "runtime": runtime_name,
                        "status": "unloaded",
                        "details": result
                    }
                    
            return {
                "model": model_name,
                "status": "not_loaded"
            }
            
        except Exception as e:
            logger.error(f"Failed to unload model '{model_name}': {e}")
            raise
            
    async def migrate_task(
        self,
        task_id: str,
        target_model: Optional[str] = None,
        target_runtime: Optional[str] = None
    ) -> Dict[str, Any]:
        """Migrate a running task to different model/runtime"""
        # Implementation for task migration
        # This would involve checkpointing, model loading, and state transfer
        pass
        
    async def get_health_status(self) -> Dict[str, Any]:
        """Get health status"""
        runtime_status = {}
        for name, runtime in self.runtimes.items():
            runtime_status[name] = await runtime.health_check()
            
        return {
            "status": "healthy" if any(runtime_status.values()) else "unhealthy",
            "version": "1.0.0",
            "uptime": time.time() - self.start_time,
            "models_loaded": sum(
                len(await rt.get_loaded_models())
                for rt in self.runtimes.values()
            ),
            "runtimes_available": [
                name for name, healthy in runtime_status.items() if healthy
            ]
        }
        
    async def get_system_status(self) -> Dict[str, Any]:
        """Get detailed system status"""
        models_status = {}
        for model_name in self.registry.list_models():
            for runtime in self.runtimes.values():
                if await runtime.is_model_loaded(model_name):
                    models_status[model_name] = "loaded"
                    break
            else:
                models_status[model_name] = "available"
                
        runtime_details = {}
        for name, runtime in self.runtimes.items():
            runtime_details[name] = {
                "healthy": await runtime.health_check(),
                "loaded_models": await runtime.get_loaded_models()
            }
            
        return {
            "status": "running",
            "uptime": time.time() - self.start_time,
            "models": models_status,
            "runtimes": runtime_details,
            "resources": await self._get_resource_usage(),
            "metrics": self.metrics
        }
        
    async def list_available_models(self) -> List[Dict[str, Any]]:
        """List all available models"""
        return self.registry.list_models_detailed()
        
    async def get_model_info(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific model"""
        return self.registry.get_model(model_name)
        
    async def get_metrics(self) -> Dict[str, Any]:
        """Get system metrics"""
        return {
            **self.metrics,
            "average_processing_time": (
                self.metrics["total_processing_time"] / self.metrics["total_requests"]
                if self.metrics["total_requests"] > 0 else 0
            ),
            "success_rate": (
                self.metrics["successful_requests"] / self.metrics["total_requests"]
                if self.metrics["total_requests"] > 0 else 0
            )
        }
        
    async def _get_resource_usage(self) -> Dict[str, Any]:
        """Get current resource usage"""
        import psutil
        
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            gpu_info = [
                {
                    "id": gpu.id,
                    "name": gpu.name,
                    "load": gpu.load * 100,
                    "memory_used": gpu.memoryUsed,
                    "memory_total": gpu.memoryTotal,
                    "temperature": gpu.temperature
                }
                for gpu in gpus
            ]
        except:
            gpu_info = []
            
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent,
            "gpus": gpu_info
        }