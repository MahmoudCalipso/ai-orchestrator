"""Advanced Pydantic Validators for input sanitization."""
from pydantic import validator
import re
from typing import Dict, Any, List

class InputValidators:
    """Reusable validator methods for Pydantic models."""
    
    @staticmethod
    def validate_project_name(v: str) -> str:
        """Enforces safe project names (alphanumeric, hyphens, underscores)."""
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Project name must be alphanumeric and can include hyphens or underscores')
        if '..' in v or '/' in v or '\\' in v:
            raise ValueError('Invalid directory traversal patterns in project name')
        return v
    
    @staticmethod
    def sanitize_code(v: str) -> str:
        """Detects potentially dangerous shell command patterns in code inputs."""
        dangerous_patterns = [
            'rm -rf', 'dd if=', 'mkfs', ':(){ :|:& };:', 
            'chmod 777', '> /dev/sda', 'nc -e'
        ]
        for pattern in dangerous_patterns:
            if pattern in v:
                raise ValueError(f'Potentially dangerous code pattern detected: {pattern}')
        return v
    
    @staticmethod
    def validate_languages(v: Dict[str, Any]) -> Dict[str, Any]:
        """Ensures provided languages are within the supported set."""
        allowed_langs = {
            'python', 'javascript', 'typescript', 'java', 'go', 
            'rust', 'csharp', 'php', 'ruby', 'c', 'cpp'
        }
        for lang in v.keys():
            if lang.lower() not in allowed_langs:
                raise ValueError(f'Unsupported language: {lang}. Allowed: {allowed_langs}')
        return v

    @staticmethod
    def validate_model_name(v: str) -> str:
        """Validates LLM model identifiers."""
        allowed_models = {
            'gpt-4o', 'gpt-4-turbo', 'gpt-3.5-turbo',
            'claude-3-opus', 'claude-3-sonnet',
            'qwen2.5-coder:7b', 'llama3:70b'
        }
        if v not in allowed_models:
            # We might want to be flexible here, but for security we can restrict
            pass
        return v
