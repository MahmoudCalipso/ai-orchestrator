# Configuration Guide - AI Orchestrator

## Overview

This guide covers all configuration options for the AI Orchestrator platform, including environment variables, YAML configuration files, and provider-specific settings.

## Configuration Files

### 1. Storage Configuration (`config/storage.yaml`)

```yaml
storage:
  # Base storage path
  base_path: "./storage"
  
  # Maximum size per project (GB)
  max_project_size: 10
  
  # Total storage quota (GB, 0 = unlimited)
  total_quota: 0
  
  # Archive after days
  archive_after_days: 90
  
  # Cleanup settings
  cleanup_enabled: true
  cleanup_schedule: "0 2 * * 0"  # Weekly at 2 AM Sunday
  
  # Backup configuration
  backup:
    enabled: true
    frequency: "daily"
    retention_days: 30
    compression: true
    destination: "./backups"
```

### 2. Workflow Configuration (`config/workflows.yaml`)

```yaml
workflows:
  # Project generation workflow
  generation:
    enabled: true
    max_concurrent: 5
    timeout_minutes: 60
    default_language: "python"
    default_framework: "fastapi"
  
  # Migration workflow
  migration:
    enabled: true
    max_concurrent: 3
    timeout_minutes: 120
    preserve_comments: true
    generate_tests: true
  
  # Bug fix workflow
  bug_fix:
    enabled: true
    auto_create_pr: true
    require_tests: true
    auto_merge: false
  
  # Update workflow
  update:
    enabled: true
    schedule: "0 0 * * 1"  # Weekly on Monday
    auto_create_pr: true
    security_only: false
  
  # Storage cleanup workflow
  cleanup:
    enabled: true
    schedule: "0 2 1 * *"  # Monthly on 1st at 2 AM
    archive_threshold_days: 90
    delete_threshold_days: 180
```

### 3. LLM Configuration (`config/llm.yaml`)

```yaml
llm:
  # Default provider (openai, anthropic, ollama, azure)
  default_provider: "openai"
  
  # Provider configurations
  providers:
    openai:
      model: "gpt-4-turbo-preview"
      temperature: 0.7
      max_tokens: 4096
      timeout: 60
    
    anthropic:
      model: "claude-3-opus-20240229"
      temperature: 0.7
      max_tokens: 4096
      timeout: 60
    
    ollama:
      base_url: "http://localhost:11434"
      model: "codellama:34b"
      temperature: 0.7
      timeout: 120
    
    azure:
      endpoint: "https://your-resource.openai.azure.com"
      deployment_name: "gpt-4"
      api_version: "2024-02-15-preview"
  
  # Fallback configuration
  fallback:
    enabled: true
    order: ["openai", "anthropic", "ollama"]
  
  # Rate limiting
  rate_limit:
    requests_per_minute: 60
    tokens_per_minute: 90000
```

### 4. Security Configuration (`config/security.yaml`)

```yaml
security:
  # API authentication
  api:
    enabled: true
    key_header: "X-API-Key"
    require_https: false  # Set to true in production
  
  # JWT configuration
  jwt:
    secret_key: "${JWT_SECRET_KEY}"
    algorithm: "HS256"
    expiration_minutes: 60
  
  # RBAC
  rbac:
    enabled: true
    default_role: "user"
    roles:
      admin:
        - "*"
      developer:
        - "api:generate"
        - "api:migrate"
        - "api:fix"
        - "api:analyze"
      viewer:
        - "api:analyze"
  
  # Credential encryption
  encryption:
    enabled: true
    algorithm: "AES-256-GCM"
    key: "${ENCRYPTION_KEY}"
  
  # Vulnerability scanning
  scanning:
    enabled: true
    schedule: "0 3 * * *"  # Daily at 3 AM
    severity_threshold: "medium"
```

### 5. Kubernetes Configuration (`config/kubernetes.yaml`)

```yaml
kubernetes:
  # Default configuration
  enabled: true
  kubeconfig: "${KUBECONFIG}"
  
  # Trial environment
  trial:
    namespace: "ai-orchestrator-trial"
    resource_limits:
      cpu: "1000m"
      memory: "2Gi"
    auto_cleanup_hours: 24
  
  # Production environment
  production:
    namespace: "ai-orchestrator-prod"
    resource_limits:
      cpu: "4000m"
      memory: "8Gi"
    replicas: 3
    auto_scaling:
      enabled: true
      min_replicas: 2
      max_replicas: 10
      target_cpu_percent: 70
  
  # Ingress configuration
  ingress:
    enabled: true
    class: "nginx"
    tls_enabled: true
    cert_manager: true
```

## Environment Variables

### Core Settings

```powershell
# Application
$env:APP_ENV="development"  # development, staging, production
$env:APP_PORT="8080"
$env:APP_HOST="0.0.0.0"
$env:LOG_LEVEL="INFO"  # DEBUG, INFO, WARNING, ERROR

# LLM Provider
$env:LLM_PROVIDER="openai"  # openai, anthropic, ollama, azure
$env:LLM_MODEL="gpt-4-turbo-preview"

# OpenAI
$env:OPENAI_API_KEY="sk-..."
$env:OPENAI_ORG_ID="org-..."  # Optional

# Anthropic
$env:ANTHROPIC_API_KEY="sk-ant-..."

# Azure OpenAI
$env:AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com"
$env:AZURE_OPENAI_API_KEY="..."
$env:AZURE_OPENAI_DEPLOYMENT="gpt-4"

# Ollama
$env:OLLAMA_BASE_URL="http://localhost:11434"
$env:OLLAMA_MODEL="codellama:34b"
```

### Storage Settings

```powershell
# Storage paths
$env:STORAGE_BASE_PATH="./storage"
$env:STORAGE_MAX_PROJECT_SIZE="10"  # GB
$env:STORAGE_TOTAL_QUOTA="0"  # GB, 0 = unlimited

# Backup
$env:STORAGE_BACKUP_ENABLED="true"
$env:STORAGE_BACKUP_DESTINATION="./backups"
$env:STORAGE_BACKUP_RETENTION_DAYS="30"
```

### Git Integration

```powershell
# GitHub
$env:GITHUB_TOKEN="ghp_..."
$env:GITHUB_OWNER="your-username"

# GitLab
$env:GITLAB_TOKEN="glpat-..."
$env:GITLAB_URL="https://gitlab.com"

# Bitbucket
$env:BITBUCKET_USERNAME="your-username"
$env:BITBUCKET_APP_PASSWORD="..."

# Azure DevOps
$env:AZURE_DEVOPS_PAT="..."
$env:AZURE_DEVOPS_ORG="your-org"
```

### Database Settings

```powershell
# PostgreSQL
$env:POSTGRES_HOST="localhost"
$env:POSTGRES_PORT="5432"
$env:POSTGRES_USER="postgres"
$env:POSTGRES_PASSWORD="password"
$env:POSTGRES_DB="ai_orchestrator"

# Redis
$env:REDIS_HOST="localhost"
$env:REDIS_PORT="6379"
$env:REDIS_PASSWORD=""  # Optional
$env:REDIS_DB="0"
```

### Security Settings

```powershell
# API Security
$env:API_KEY="your-api-key-here"
$env:REQUIRE_API_KEY="true"

# JWT
$env:JWT_SECRET_KEY="your-secret-key-here"
$env:JWT_EXPIRATION_MINUTES="60"

# Encryption
$env:ENCRYPTION_KEY="your-encryption-key-here"
```

### Kubernetes Settings

```powershell
# Kubernetes
$env:KUBECONFIG="C:\Users\YourUser\.kube\config"
$env:K8S_NAMESPACE="ai-orchestrator"
$env:K8S_CONTEXT="docker-desktop"  # or your cluster context
```

### Figma Integration

```powershell
# Figma
$env:FIGMA_ACCESS_TOKEN="figd_..."
$env:FIGMA_TEAM_ID="your-team-id"
```

## Configuration Priority

Configuration values are loaded in the following order (later overrides earlier):

1. **Default values** (hardcoded in application)
2. **YAML configuration files** (`config/*.yaml`)
3. **Environment variables** (`.env` file or system environment)
4. **Command-line arguments** (if applicable)

### Example: LLM Provider Selection

```python
# 1. Default in code
provider = "openai"

# 2. Override from config/llm.yaml
# default_provider: "anthropic"
provider = "anthropic"

# 3. Override from environment variable
# $env:LLM_PROVIDER="ollama"
provider = "ollama"

# Final value: "ollama"
```

## Configuration Validation

### Validate Configuration

```powershell
# Validate all configuration files
python -m core.config.validate

# Validate specific configuration
python -m core.config.validate --config storage

# Check for missing required variables
python -m core.config.validate --check-env
```

### Configuration Schema

The platform validates configuration against JSON schemas:

```python
from core.config import ConfigValidator

validator = ConfigValidator()

# Validate storage config
validator.validate_storage_config("config/storage.yaml")

# Validate all configs
validator.validate_all()
```

## Advanced Configuration

### Custom Configuration Loader

```python
from core.config import ConfigLoader

# Load with custom path
config = ConfigLoader(config_dir="./custom-config")

# Load specific config
storage_config = config.load("storage")

# Get value with fallback
max_size = config.get("storage.max_project_size", default=10)
```

### Dynamic Configuration Updates

```python
from core.config import ConfigManager

config_mgr = ConfigManager()

# Update configuration at runtime
await config_mgr.update("workflows.generation.max_concurrent", 10)

# Reload configuration
await config_mgr.reload()

# Watch for configuration changes
config_mgr.watch(on_change=lambda key, value: print(f"{key} changed to {value}"))
```

### Environment-Specific Configuration

```yaml
# config/storage.development.yaml
storage:
  base_path: "./storage-dev"
  max_project_size: 1  # Smaller for dev

# config/storage.production.yaml
storage:
  base_path: "/data/storage"
  max_project_size: 100  # Larger for production
```

Load based on environment:

```powershell
$env:APP_ENV="production"
python main.py  # Loads config/storage.production.yaml
```

## Configuration Templates

### Development Environment

```powershell
# .env.development
APP_ENV=development
LOG_LEVEL=DEBUG
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
STORAGE_BASE_PATH=./storage-dev
REQUIRE_API_KEY=false
```

### Production Environment

```powershell
# .env.production
APP_ENV=production
LOG_LEVEL=INFO
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
STORAGE_BASE_PATH=/data/storage
REQUIRE_API_KEY=true
REQUIRE_HTTPS=true
JWT_SECRET_KEY=...
ENCRYPTION_KEY=...
```

### Docker Environment

```yaml
# docker-compose.yml
services:
  ai-orchestrator:
    environment:
      - APP_ENV=production
      - LLM_PROVIDER=openai
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - POSTGRES_HOST=postgres
      - REDIS_HOST=redis
      - STORAGE_BASE_PATH=/data/storage
    volumes:
      - ./storage:/data/storage
      - ./config:/app/config
```

## Troubleshooting

### Issue: Configuration Not Loading

```powershell
# Check configuration file syntax
python -m core.config.validate --config storage

# Verify file exists
ls config/storage.yaml

# Check file permissions
icacls config/storage.yaml
```

### Issue: Environment Variable Not Applied

```powershell
# Verify environment variable is set
echo $env:LLM_PROVIDER

# Check configuration priority
python -m core.config.debug --key llm.provider

# Reload environment
$env:LLM_PROVIDER="ollama"
```

### Issue: Invalid Configuration Value

```powershell
# Validate configuration
python -m core.config.validate

# Check logs for validation errors
cat logs/app.log | Select-String "config"

# Reset to defaults
python -m core.config.reset --config storage
```

## Best Practices

1. **Use Environment Variables for Secrets**
   - Never commit API keys or passwords to version control
   - Use `.env` files (add to `.gitignore`)
   - Use secret management tools in production

2. **Validate Configuration on Startup**
   - Enable configuration validation
   - Fail fast if configuration is invalid
   - Log configuration issues clearly

3. **Document Custom Configuration**
   - Add comments to YAML files
   - Document environment variables
   - Provide example configurations

4. **Use Environment-Specific Configs**
   - Separate dev/staging/production configs
   - Use appropriate defaults for each environment
   - Test configuration changes in dev first

5. **Monitor Configuration Changes**
   - Log configuration updates
   - Audit configuration access
   - Version control configuration files

---

**For more information, see:**
- [STORAGE_GUIDE.md](STORAGE_GUIDE.md) - Storage configuration
- [LOCAL_AI_MODELS_GUIDE.md](LOCAL_AI_MODELS_GUIDE.md) - LLM configuration
- [GIT_CONFIGURATION_GUIDE.md](GIT_CONFIGURATION_GUIDE.md) - Git integration
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues
