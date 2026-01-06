"""
Migration Agent - Handles task migration between models and runtimes
"""
import logging
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class MigrationAgent:
    """Agent for migrating running tasks between models/runtimes"""
    
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.migration_history = []
        
    async def migrate_task(
        self,
        task_id: str,
        target_model: Optional[str] = None,
        target_runtime: Optional[str] = None,
        preserve_state: bool = True
    ) -> Dict[str, Any]:
        """Migrate a task to a different model or runtime"""
        
        try:
            logger.info(f"Starting migration for task {task_id}")
            
            # Get current task state
            task_state = await self._get_task_state(task_id)
            if not task_state:
                return {
                    "status": "error",
                    "message": f"Task {task_id} not found"
                }
            
            # Determine target configuration
            current_model = task_state.get("model")
            current_runtime = task_state.get("runtime")
            
            target_model = target_model or current_model
            target_runtime = target_runtime or current_runtime
            
            # Validate target
            validation = await self._validate_target(target_model, target_runtime)
            if not validation["valid"]:
                return {
                    "status": "error",
                    "message": validation["reason"]
                }
            
            # Create checkpoint if preserving state
            checkpoint = None
            if preserve_state:
                checkpoint = await self._create_checkpoint(task_state)
            
            # Pause current task
            await self._pause_task(task_id)
            
            # Load target model if needed
            target_runtime_obj = self.orchestrator.runtimes.get(target_runtime)
            if not await target_runtime_obj.is_model_loaded(target_model):
                await target_runtime_obj.load_model(target_model)
            
            # Restore state to new model
            if checkpoint:
                await self._restore_checkpoint(
                    checkpoint,
                    target_model,
                    target_runtime
                )
            
            # Update task configuration
            await self._update_task(task_id, target_model, target_runtime)
            
            # Resume task
            await self._resume_task(task_id)
            
            # Record migration
            migration_record = {
                "task_id": task_id,
                "timestamp": datetime.now().isoformat(),
                "from": {
                    "model": current_model,
                    "runtime": current_runtime
                },
                "to": {
                    "model": target_model,
                    "runtime": target_runtime
                },
                "preserved_state": preserve_state,
                "status": "success"
            }
            
            self.migration_history.append(migration_record)
            
            logger.info(f"Migration completed successfully for task {task_id}")
            
            return {
                "status": "success",
                "migration": migration_record
            }
            
        except Exception as e:
            logger.error(f"Migration failed for task {task_id}: {e}")
            
            migration_record = {
                "task_id": task_id,
                "timestamp": datetime.now().isoformat(),
                "status": "failed",
                "error": str(e)
            }
            
            self.migration_history.append(migration_record)
            
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def _get_task_state(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get current state of a task"""
        return self.orchestrator.active_tasks.get(task_id)
    
    async def _validate_target(
        self,
        model: str,
        runtime: str
    ) -> Dict[str, Any]:
        """Validate target model and runtime"""
        
        # Check if runtime exists
        if runtime not in self.orchestrator.runtimes:
            return {
                "valid": False,
                "reason": f"Runtime '{runtime}' not available"
            }
        
        # Check if runtime is healthy
        runtime_obj = self.orchestrator.runtimes[runtime]
        if not await runtime_obj.health_check():
            return {
                "valid": False,
                "reason": f"Runtime '{runtime}' is not healthy"
            }
        
        # Check if model exists in registry
        model_info = self.orchestrator.registry.get_model(model)
        if not model_info:
            return {
                "valid": False,
                "reason": f"Model '{model}' not found in registry"
            }
        
        # Check if runtime supports this model
        recommended_runtimes = model_info.get("recommended_runtime", [])
        if runtime not in recommended_runtimes:
            return {
                "valid": False,
                "reason": f"Runtime '{runtime}' not recommended for model '{model}'"
            }
        
        return {"valid": True}
    
    async def _create_checkpoint(self, task_state: Dict[str, Any]) -> Dict[str, Any]:
        """Create a checkpoint of task state"""
        
        checkpoint = {
            "task_id": task_state.get("task_id"),
            "context": task_state.get("context", {}),
            "conversation_history": task_state.get("conversation_history", []),
            "parameters": task_state.get("parameters", {}),
            "created_at": datetime.now().isoformat()
        }
        
        # Store checkpoint in memory
        await self.orchestrator.memory.store(
            key=f"checkpoint:{checkpoint['task_id']}",
            value=checkpoint,
            ttl=3600  # 1 hour
        )
        
        return checkpoint
    
    async def _restore_checkpoint(
        self,
        checkpoint: Dict[str, Any],
        target_model: str,
        target_runtime: str
    ):
        """Restore checkpoint to new model/runtime"""
        
        # In a real implementation, this would restore the conversation state
        # For now, we just log the restoration
        logger.info(f"Restoring checkpoint for task {checkpoint['task_id']}")
    
    async def _pause_task(self, task_id: str):
        """Pause a running task"""
        
        if task_id in self.orchestrator.active_tasks:
            self.orchestrator.active_tasks[task_id]["status"] = "paused"
            logger.info(f"Task {task_id} paused")
    
    async def _resume_task(self, task_id: str):
        """Resume a paused task"""
        
        if task_id in self.orchestrator.active_tasks:
            self.orchestrator.active_tasks[task_id]["status"] = "running"
            logger.info(f"Task {task_id} resumed")
    
    async def _update_task(
        self,
        task_id: str,
        target_model: str,
        target_runtime: str
    ):
        """Update task configuration"""
        
        if task_id in self.orchestrator.active_tasks:
            self.orchestrator.active_tasks[task_id]["model"] = target_model
            self.orchestrator.active_tasks[task_id]["runtime"] = target_runtime
            logger.info(f"Task {task_id} updated to use {target_model} on {target_runtime}")
    
    async def get_migration_history(
        self,
        limit: int = 10
    ) -> list:
        """Get migration history"""
        return self.migration_history[-limit:]
    
    async def analyze_migration_patterns(self) -> Dict[str, Any]:
        """Analyze migration patterns to optimize routing"""
        
        if not self.migration_history:
            return {
                "total_migrations": 0,
                "success_rate": 0,
                "common_sources": [],
                "common_targets": []
            }
        
        successful = [m for m in self.migration_history if m.get("status") == "success"]
        
        # Count source models
        source_models = {}
        for migration in successful:
            source = migration.get("from", {}).get("model")
            if source:
                source_models[source] = source_models.get(source, 0) + 1
        
        # Count target models
        target_models = {}
        for migration in successful:
            target = migration.get("to", {}).get("model")
            if target:
                target_models[target] = target_models.get(target, 0) + 1
        
        return {
            "total_migrations": len(self.migration_history),
            "successful_migrations": len(successful),
            "success_rate": len(successful) / len(self.migration_history),
            "common_sources": sorted(
                source_models.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5],
            "common_targets": sorted(
                target_models.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
        }