# Environment Setup Guide - AI Orchestrator
**After Security Remediation**

## Quick Setup for Development

### 1. Generate Secure API Keys
```powershell
# PowerShell
$randomKey = [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes((New-Guid).ToString() + (Get-Random)))
Write-Host "Generated API Key: sk-$randomKey"
```

### 2. Create .env File
Create a `.env` file in the project root:
```bash
# ==============================
# API & Security
# ==============================
ORCHESTRATOR_API_KEY=sk-your-generated-key-here
DEFAULT_API_KEY=sk-your-generated-key-here

# ==============================
# Optional: LLM Providers
# ==============================
OPENAI_API_KEY=sk-your-openai-key
ANTHROPIC_API_KEY=sk-your-anthropic-key

# ==============================
# Optional: Ollama (Local)
# ==============================
OLLAMA_BASE_URL=http://localhost:11434

# ==============================
# Database (Optional)
# ==============================
DATABASE_URL=postgresql://user:password@localhost/orchestrator
MONGODB_URL=mongodb://localhost:27017

# ==============================
# Redis (Optional)
# ==============================
REDIS_URL=redis://localhost:6379

# ==============================
# Git Integration (Optional)
# ==============================
GITHUB_TOKEN=ghp_your-github-token
GITLAB_TOKEN=glpat-your-gitlab-token
```

### 3. Install Dependencies
```bash
# Upgrade pip
pip install --upgrade pip

# Install all dependencies with security updates
pip install -r requirements.txt --upgrade

# Verify no conflicts
pip check
```

### 4. Set Environment Variables

**Windows PowerShell:**
```powershell
$env:ORCHESTRATOR_API_KEY = "sk-your-secure-key-here"
$env:DEFAULT_API_KEY = "sk-your-secure-key-here"
```

**Windows Command Prompt:**
```cmd
set ORCHESTRATOR_API_KEY=sk-your-secure-key-here
set DEFAULT_API_KEY=sk-your-secure-key-here
```

**Linux/macOS (Bash):**
```bash
export ORCHESTRATOR_API_KEY="sk-your-secure-key-here"
export DEFAULT_API_KEY="sk-your-secure-key-here"
```

### 5. Run Application
```bash
# Make sure environment variables are set first!
python main.py --host 0.0.0.0 --port 8080
```

### 6. Access API
```bash
# Test health endpoint (no auth required)
curl http://localhost:8080/health

# Test authenticated endpoint (requires API key)
curl -H "X-API-Key: sk-your-secure-key-here" http://localhost:8080/models
```

---

## Docker Deployment

### 1. Build Docker Image
```bash
docker build -t ai-orchestrator:latest .
```

### 2. Create docker-compose.yml Override
```yaml
version: '3.8'

services:
  orchestrator:
    image: ai-orchestrator:latest
    environment:
      - ORCHESTRATOR_API_KEY=${ORCHESTRATOR_API_KEY}
      - DEFAULT_API_KEY=${DEFAULT_API_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - OLLAMA_BASE_URL=${OLLAMA_BASE_URL}
    ports:
      - "8080:8080"
    volumes:
      - ./storage:/app/storage
    restart: always

  # Optional: Ollama for local LLM
  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    restart: always

  # Optional: PostgreSQL
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: orchestrator
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: orchestrator
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: always

volumes:
  ollama_data:
  postgres_data:
```

### 3. Run with Docker Compose
```bash
# Set environment variables first
export ORCHESTRATOR_API_KEY="sk-your-key"
export DEFAULT_API_KEY="sk-your-key"
export DB_PASSWORD="secure-db-password"

# Start services
docker-compose up -d

# Check logs
docker-compose logs -f orchestrator
```

---

## CLI Setup

### 1. Set API Key for CLI
```bash
# Option 1: Environment Variable
export ORCHESTRATOR_API_KEY="sk-your-secure-key-here"

# Option 2: Command Line Argument
# python cli.py --api-key "sk-your-secure-key-here" <command>
```

### 2. Use CLI Commands
```bash
# Health check
python cli.py health

# List models
python cli.py models list

# Generate code
python cli.py generate --project-name "MyApp" --description "My application"

# Analyze code
python cli.py analyze --file "path/to/code.py"
```

---

## Monitor Script Setup

### 1. Start Monitoring
```bash
# With environment variable
export ORCHESTRATOR_API_KEY="sk-your-secure-key-here"
python scripts/monitor.py

# With command line argument
python scripts/monitor.py --api-key "sk-your-secure-key-here"

# With custom interval (every 10 seconds)
python scripts/monitor.py --interval 10

# Run once and exit
python scripts/monitor.py --once
```

---

## Production Deployment Checklist

### Pre-Deployment
- [ ] Generate secure API keys (don't use examples)
- [ ] Update .env with production values
- [ ] Set up environment variables securely
- [ ] Update CONFIGURATION_GUIDE.md for your team
- [ ] Test API key access locally
- [ ] Verify all tests pass

### Infrastructure
- [ ] Set up Docker/Kubernetes if using containers
- [ ] Configure HTTPS/SSL certificates
- [ ] Set up firewall rules
- [ ] Configure secrets management (Vault, AWS Secrets Manager)
- [ ] Set up monitoring and logging
- [ ] Configure backup strategy

### Security
- [ ] Enable HTTPS only
- [ ] Set strong JWT secrets
- [ ] Configure rate limiting
- [ ] Enable audit logging
- [ ] Set up security headers
- [ ] Configure CORS properly

### Operational
- [ ] Set up health check monitoring
- [ ] Configure auto-restart on failure
- [ ] Set up log rotation
- [ ] Configure alerting
- [ ] Document runbooks
- [ ] Schedule security updates

---

## Troubleshooting

### Issue: "API key required" Error
**Solution**: Make sure environment variables are set:
```bash
echo $ORCHESTRATOR_API_KEY  # Check if set
# If empty, set it:
export ORCHESTRATOR_API_KEY="sk-your-key-here"
```

### Issue: "Invalid API key" Error
**Solution**: Verify the API key is correct and matches what was set

### Issue: Pydantic Warnings
**Solution**: Already fixed in this update. Ensure you have the latest code.

### Issue: Dependency Conflicts
**Solution**: Run `pip check` and install correct versions:
```bash
pip install torch>=2.8.0 transformers>=4.53.0 cryptography>=44.0.1 requests>=2.32.4
```

### Issue: Import Errors
**Solution**: Reinstall dependencies:
```bash
pip install -r requirements.txt --force-reinstall --upgrade
```

---

## Environment Variables Reference

### Required
- `ORCHESTRATOR_API_KEY` - API key for authentication
- `DEFAULT_API_KEY` - Default key if no key provided

### Optional LLM Providers
- `OPENAI_API_KEY` - For OpenAI models
- `ANTHROPIC_API_KEY` - For Anthropic Claude models
- `OLLAMA_BASE_URL` - For local Ollama server

### Optional Database
- `DATABASE_URL` - PostgreSQL connection string
- `MONGODB_URL` - MongoDB connection string
- `REDIS_URL` - Redis connection string

### Optional Cloud
- `GITHUB_TOKEN` - GitHub API token
- `GITLAB_TOKEN` - GitLab API token
- `AWS_ACCESS_KEY_ID` - AWS credentials
- `AWS_SECRET_ACCESS_KEY` - AWS credentials

### Optional Features
- `LOG_LEVEL` - Logging level (DEBUG, INFO, WARNING, ERROR)
- `CORS_ORIGINS` - Allowed CORS origins
- `WORKER_THREADS` - Number of worker threads

---

## Security Best Practices

1. **Never commit .env file**
   ```bash
   echo ".env" >> .gitignore
   ```

2. **Use strong API keys**
   - Minimum 32 characters
   - Use `secrets` module or similar
   - Rotate regularly

3. **Secure environment variables**
   - Use secrets management systems in production
   - Never log API keys
   - Encrypt at rest if stored

4. **Monitor access**
   - Enable audit logging
   - Review access patterns
   - Alert on suspicious activity

5. **Keep dependencies updated**
   ```bash
   pip list --outdated
   pip install --upgrade <package>
   ```

---

## Support

For issues or questions:
1. Check the DEEP_PROJECT_ANALYSIS_REPORT.md
2. Review SECURITY_REMEDIATION_COMPLETED.md
3. Check application logs
4. Review API documentation at `/docs`

