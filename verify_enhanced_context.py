import asyncio
import sys
import os
from unittest.mock import MagicMock, AsyncMock

# Add project root to path
sys.path.append(os.getcwd())

from schemas.generation_spec import EntityDefinition, EntityField, SecurityConfig, DatabaseConfig, DatabaseType
from services.database.entity_generator import EntityGenerator
from agents.universal_ai_agent import UniversalAIAgent

async def test_enhanced_prompt_construction():
    print("Testing Enhanced Prompt Construction...")
    
    # Mock Orchestrator and LLM
    mock_llm = AsyncMock()
    mock_llm.generate = AsyncMock(return_value="## Solution\n```python\n# Mocked Code\n```")
    
    mock_orchestrator = MagicMock()
    mock_orchestrator.llm = mock_llm
    
    agent = UniversalAIAgent(mock_orchestrator)
    mock_orchestrator.universal_agent = agent
    
    generator = EntityGenerator(mock_orchestrator)
    
    # Complex Request Data
    context = {
        "project_name": "SecureFintechApp",
        "description": "A high-security fintech application for processing micro-loans. All monetary values must be stored as Decimal(18, 2).",
        "requirements": "Implement strict field validation and audit logging for all mutations. Use AES-256 for PII data.",
        "security": {
            "auth_provider": "jwt",
            "enable_rbac": True,
            "enable_audit_logs": True
        },
        "database": {
            "type": "postgresql"
        }
    }
    
    entities = [
        EntityDefinition(
            name="LoanRequest",
            fields=[
                EntityField(name="id", type="integer", primary_key=True),
                EntityField(name="amount", type="decimal", length=18),
                EntityField(name="user_pii", type="string", description="User PII data")
            ]
        )
    ]
    
    # Trigger model generation
    await generator.generate_models(entities, "python", context=context)
    
    # Verify the prompt passed to LLM
    last_call = mock_llm.generate.call_args
    prompt = last_call.kwargs['prompt']
    
    print("\n--- CAPTURED PROMPT ---")
    print(prompt)
    print("-----------------------\n")
    
    # Assertions
    assert "SecureFintechApp" in prompt, "Project name missing from prompt"
    assert "fintech application for processing micro-loans" in prompt, "Description missing from prompt"
    assert "AES-256 for PII data" in prompt, "Requirements missing from prompt"
    assert "auth_provider: jwt" in prompt, "Security config missing from prompt"
    assert "Database Type: postgresql" in prompt, "Database config missing from prompt"
    
    print("Verification Successful: Prompt contains all metadata!")

if __name__ == "__main__":
    asyncio.run(test_enhanced_prompt_construction())
