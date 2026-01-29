import os
import secrets
from pathlib import Path

def update_env_file(env_file: Path, updates: dict):
    if env_file.exists():
        lines = env_file.read_text().splitlines()
    else:
        lines = []
    
    updated_keys = set()
    for i, line in enumerate(lines):
        if '=' in line and not line.strip().startswith('#'):
            key = line.split('=')[0].strip()
            if key in updates:
                lines[i] = f"{key}={updates[key]}"
                updated_keys.add(key)
    
    for key, value in updates.items():
        if key not in updated_keys:
            lines.append(f"{key}={value}")
    
    env_file.write_text('\n'.join(lines) + '\n')
    print(f"Updated {env_file}")

if __name__ == "__main__":
    project_root = Path(__file__).parent.parent
    env_file = project_root / ".env"
    
    updates = {
        "JWT_SECRET_KEY": secrets.token_urlsafe(32),
        "JWT_ALGORITHM": "HS256",
        "ACCESS_TOKEN_EXPIRE_MINUTES": "60",
        "DEFAULT_API_KEY": f"dev-key-{secrets.token_hex(8)}",
        "MASTER_ENCRYPTION_KEY": secrets.token_urlsafe(32),
        "REDIS_HOST": "localhost",
        "REDIS_PORT": "6379",
        "DATABASE_URL": f"postgresql://orchestrator:{secrets.token_urlsafe(16)}@localhost:5432/ai_orchestrator",
        "LLM_PROVIDER": "ollama",
        "LLM_MODEL": "qwen2.5-coder:7b",
        "MODEL_TIER": "minimal",
        "API_PORT": "8000",
        "APP_ENV": "production",
        "LOG_LEVEL": "INFO",
        "ALLOWED_ORIGINS": "*"
    }
    
    update_env_file(env_file, updates)
    print("Essential environment variables initialized.")
