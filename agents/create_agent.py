"""
Create Agent - Assists in creating new AI agents
"""
import asyncio
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class CreateAgent:
    """Agent for creating new AI configurations"""
    
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        
    async def create_agent_config(
        self,
        name: str,
        purpose: str,
        capabilities: list,
        model_preference: str = None
    ) -> Dict[str, Any]:
        """Create a new agent configuration"""
        
        # Determine best model based on purpose
        if not model_preference:
            model_preference = await self._recommend_model(purpose, capabilities)
            
        config = {
            "name": name,
            "purpose": purpose,
            "capabilities": capabilities,
            "model": model_preference,
            "parameters": await self._get_default_parameters(purpose),
            "system_prompt": await self._generate_system_prompt(purpose, capabilities)
        }
        
        return config
        
    async def _recommend_model(
        self,
        purpose: str,
        capabilities: list
    ) -> str:
        """Recommend best model for agent"""
        
        purpose_lower = purpose.lower()
        
        if "code" in purpose_lower or "programming" in purpose_lower:
            return "deepseek-coder"
        elif "reasoning" in purpose_lower or "analysis" in purpose_lower:
            return "qwen2.5"
        elif "creative" in purpose_lower or "writing" in purpose_lower:
            return "llama3.1"
        elif "fast" in purpose_lower or "quick" in purpose_lower:
            return "mistral"
        else:
            return "llama3.1"
            
    async def _get_default_parameters(self, purpose: str) -> Dict[str, Any]:
        """Get default parameters based on purpose"""
        
        if "code" in purpose.lower():
            return {
                "temperature": 0.2,
                "top_p": 0.95,
                "max_tokens": 4096
            }
        elif "creative" in purpose.lower():
            return {
                "temperature": 0.8,
                "top_p": 0.95,
                "max_tokens": 2048
            }
        else:
            return {
                "temperature": 0.7,
                "top_p": 0.9,
                "max_tokens": 2048
            }
            
    async def _generate_system_prompt(
        self,
        purpose: str,
        capabilities: list
    ) -> str:
        """Generate system prompt for agent"""
        
        prompt = f"You are an AI assistant designed for: {purpose}\n\n"
        prompt += "Your capabilities include:\n"
        for cap in capabilities:
            prompt += f"- {cap}\n"
        prompt += "\nProvide helpful, accurate, and concise responses."
        
        return prompt
        
    async def test_agent(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Test an agent configuration"""
        
        test_prompt = "Hello, please introduce yourself and explain what you can do."
        
        result = await self.orchestrator.run_inference(
            prompt=test_prompt,
            model=config["model"],
            parameters=config["parameters"]
        )
        
        return {
            "status": "success",
            "test_output": result["output"],
            "performance": {
                "tokens": result["tokens_used"],
                "time": result["processing_time"]
            }
        }