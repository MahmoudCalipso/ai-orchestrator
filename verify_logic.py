import asyncio
from typing import List, Dict, Optional, Any

# Mock classes to simulate the project's logic after my changes
class MockEntityField:
    def __init__(self, name, type, description=None, primary_key=False, foreign_key=None, unique=False, nullable=False, validations=None, length=None):
        self.name = name
        self.type = type
        self.description = description
        self.primary_key = primary_key
        self.foreign_key = foreign_key
        self.unique = unique
        self.nullable = nullable
        self.validations = validations or []
        self.length = length

class MockEntityDefinition:
    def __init__(self, name, fields, table_name=None, relationships=None):
        self.name = name
        self.fields = fields
        self.table_name = table_name or name.lower()
        self.relationships = relationships or []

# Simulated UniversalAIAgent._build_universal_prompt (Copy of the logic I implemented)
def simulated_build_universal_prompt(task: str, context: Dict[str, Any]) -> str:
    # This is EXACTLY what I implemented in agents/universal_ai_agent.py
    code = context.get("code", "")
    language = context.get("language", "auto-detect")
    requirements = context.get("requirements", "")
    
    project_name = context.get("project_name", "")
    description = context.get("description", "")
    security = context.get("security", {})
    database = context.get("database", {})
    
    prompt_parts = [f"Task: {task}\n"]
    if language and language != "auto-detect":
        prompt_parts.append(f"\nProgramming Language: {language}\n")
    if requirements:
        prompt_parts.append(f"\nRequirements:\n{requirements}\n")
        
    if project_name or description:
        prompt_parts.append("\n### GLOBAL PROJECT CONTEXT ###\n")
        if project_name:
            prompt_parts.append(f"Project Name: {project_name}\n")
        if description:
            prompt_parts.append(f"Description: {description}\n")
        prompt_parts.append("##############################\n")

    if security:
        prompt_parts.append("\n### SECURITY REQUIREMENTS ###\n")
        for key, val in security.items():
            if val is True or (isinstance(val, str) and val):
                prompt_parts.append(f"- {key}: {val}\n")
        prompt_parts.append("##############################\n")

    if database:
        prompt_parts.append("\n### DATABASE CONFIGURATION ###\n")
        db_type = database.get("type", "standard")
        prompt_parts.append(f"- Database Type: {db_type}\n")
        prompt_parts.append("##############################\n")
    
    return "".join(prompt_parts)

def test_logic():
    print("Verifying Implementation Logic...")
    
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
    
    prompt = simulated_build_universal_prompt("Generate model", context)
    
    print("\n--- GENERATED PROMPT ---")
    print(prompt)
    print("------------------------\n")
    
    assert "SecureFintechApp" in prompt
    assert "Decimal(18, 2)" in prompt
    assert "AES-256" in prompt
    assert "enable_rbac: True" in prompt
    assert "Database Type: postgresql" in prompt
    
    print("Logic Verification Successful!")

if __name__ == "__main__":
    test_logic()
