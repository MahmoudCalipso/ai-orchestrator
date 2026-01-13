import asyncio
import json
import yaml
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock

# 1. Test Model Discovery
async def test_model_discovery():
    print("Testing Model Discovery Logic...")
    from services.registry.model_discovery import ModelDiscoveryService
    
    # Use a temp config for testing
    temp_config = "config/test_models.yaml"
    with open(temp_config, "w") as f:
        yaml.dump({"models": {}}, f)
        
    discovery = ModelDiscoveryService(config_path=temp_config)
    result = await discovery.search_and_install_best_models()
    
    print(f"Discovery Result: {result}")
    assert result["found"] > 0
    assert "deepseek-v3.2-speciale" in result["installed"]
    
    with open(temp_config, "r") as f:
        registry = yaml.safe_load(f)
        assert "deepseek-v3.2-speciale" in registry["models"]
    
    import os
    os.remove(temp_config)
    print("Model Discovery: SUCCESS")

# 2. Test Swarm Decomposition (Migration & Fix)
async def test_swarm_decomposition():
    print("\nTesting Swarm Decomposition for Migration and Fix...")
    from agents.lead_architect import LeadArchitectAgent
    
    mock_orch = MagicMock()
    architect = LeadArchitectAgent(mock_orch)
    
    # Test Migration
    mig_subtasks = await architect._decompose("Migrate Java to Go", "migration")
    print(f"Migration Subtasks: {[s['domain'] for s in mig_subtasks]}")
    assert any(s['domain'] == "migration" for s in mig_subtasks)
    assert any(s['model'] == "coder" for s in mig_subtasks)
    
    # Test Fix
    fix_subtasks = await architect._decompose("NullPointer in Auth.py", "self_healing")
    print(f"Fix Subtasks: {[s['domain'] for s in fix_subtasks]}")
    assert any(s['domain'] == "audit" for s in fix_subtasks)
    assert any(s['domain'] == "fix" for s in fix_subtasks)
    
    print("Swarm Decomposition: SUCCESS")

# 3. Test Persona/Role Construction
async def test_agent_personas():
    print("\nTesting Agent Persona Construction...")
    from agents.universal_ai_agent import UniversalAIAgent
    
    mock_orch = MagicMock()
    agent = UniversalAIAgent(mock_orch)
    
    # Migration persona
    mig_prompt = agent._build_universal_prompt("Migrate code", {"source_stack": "Java", "target_stack": "Go", "domain": "migration"})
    assert "LEGACY MODERNIZATION & MIGRATION EXPERT" in mig_prompt
    
    # Fix persona
    fix_prompt = agent._build_universal_prompt("Fix bug", {"type": "self_healing", "domain": "self_healing"})
    assert "SR. RELIABILITY ENGINEER & DEBUGGING SPECIALIST" in fix_prompt
    
    print("Agent Personas: SUCCESS")

async def run_all():
    await test_model_discovery()
    await test_swarm_decomposition()
    await test_agent_personas()
    print("\n--- ALL ULTIMATE TESTS PASSED ---")

if __name__ == "__main__":
    asyncio.run(run_all())
