# Troubleshooting Guide

Common issues and solutions for AI Orchestrator.

## Installation Issues

### Python Version Error

**Problem:** `Error: Python 3.11 or higher is required`

**Solution:**
```bash
# Check Python version
python3 --version

# Install Python 3.11+ (Ubuntu/Debian)
sudo apt update
sudo apt install python3.11 python3.11-venv

# Or use pyenv
pyenv install 3.11.0
pyenv global 3.11.0
```

### Dependency Installation Fails

**Problem:** `pip install` fails with compilation errors

**Solution:**
```bash
# Install build dependencies (Ubuntu/Debian)
sudo apt install build-essential python3-dev

# For CUDA support
sudo apt install nvidia-cuda-toolkit

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Try installing again
pip install -r requirements.txt
```

## Runtime Issues

### Ollama Connection Error

**Problem:** `Failed to connect to Ollama`

**Solutions:**

1. **Check if Ollama is running:**
```bash
curl http://localhost:11434/api/tags

# If not running, start it
ollama serve
```

2. **Check Ollama port:**
```bash
# Verify Ollama is on port 11434
netstat -tuln | grep 11434

# If on different port, update config/runtimes.yaml
```

3. **Check firewall:**
```bash
# Allow Ollama port
sudo ufw allow 11434
```

### Model Not Found

**Problem:** `Model 'xyz' not found`

**Solutions:**

1. **List available models:**
```bash
ollama list
```

2. **Pull the model:**
```bash
ollama pull mistral
ollama pull phi3
```

3. **Check model name in config:**
Edit `config/models.yaml` and verify model names match Ollama's naming.

### GPU Not Detected

**Problem:** `No NVIDIA GPU detected`

**Solutions:**

1. **Check GPU:**
```bash
nvidia-smi

# If command not found, install drivers
sudo apt install nvidia-driver-535  # or latest
```

2. **Verify CUDA:**
```bash
nvcc --version

# Install CUDA if needed
sudo apt install nvidia-cuda-toolkit
```

3. **Check Docker GPU support:**
```bash
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
```

4. **Force CPU mode:**
Edit `config/hardware.yaml` and set GPU to disabled.

## Performance Issues

### Slow Inference

**Problem:** Responses take too long

**Solutions:**

1. **Use smaller model:**
```yaml
# In config/policies.yaml, change to faster model
quick_query:
  models: [phi3, mistral]  # Smaller, faster models
```

2. **Enable quantization:**
```yaml
# In config/models.yaml
mistral:
  quantization: [q4_k_m]  # Faster than q8_0
```

3. **Increase GPU layers:**
```yaml
# In config/runtimes.yaml
ollama:
  config:
    gpu_layers: -1  # Use all GPU layers
```

4. **Use vLLM for high throughput:**
Switch to vLLM runtime for better batching.

### High Memory Usage

**Problem:** System runs out of memory

**Solutions:**

1. **Reduce context length:**
```yaml
# In config/models.yaml
model_name:
  context_length: 4096  # Reduce from 32768
```

2. **Use quantized models:**
```bash
# Pull quantized version
ollama pull mistral:7b-q4_K_M
```

3. **Limit concurrent requests:**
```yaml
# In config/policies.yaml
load_balancing:
  max_concurrent_requests: 2  # Reduce from 10
```

4. **Enable model unloading:**
```python
# Automatically unload models after use
await orchestrator.unload_model("model_name")
```

### High CPU Usage

**Problem:** CPU at 100%

**Solutions:**

1. **Reduce thread count:**
```yaml
# In config/runtimes.yaml
llamacpp:
  config:
    n_threads: 4  # Reduce from 8
```

2. **Use GPU instead:**
Ensure models are running on GPU, not CPU.

3. **Limit requests:**
```yaml
# In config/policies.yaml
rate_limiting:
  requests_per_minute: 30  # Reduce from 100
```

## API Issues

### 401 Unauthorized

**Problem:** `Invalid API key`

**Solutions:**

1. **Check API key:**
```bash
# Use the default dev key
curl -H "X-API-Key: dev-key-12345" http://localhost:8080/health
```

2. **Generate new key:**
```python
from core.security import SecurityManager
security = SecurityManager()
key = security.generate_api_key("your-user", "user")
print(key)
```

3. **Disable auth temporarily:**
Edit `main.py` and comment out `Depends(verify_api_key)`.

### 429 Rate Limit Exceeded

**Problem:** `Rate limit exceeded`

**Solutions:**

1. **Increase rate limit:**
```yaml
# In config/policies.yaml
rate_limiting:
  requests_per_minute: 200  # Increase from 100
```

2. **Use different API key:**
Each API key has separate rate limits.

### 500 Internal Server Error

**Problem:** Server returns 500 error

**Solutions:**

1. **Check logs:**
```bash
tail -f logs/errors.log
```

2. **Check runtime health:**
```bash
curl http://localhost:8080/status -H "X-API-Key: dev-key-12345"
```

3. **Restart orchestrator:**
```bash
./run.sh
```

## Docker Issues

### Container Won't Start

**Problem:** Docker container exits immediately

**Solutions:**

1. **Check logs:**
```bash
docker-compose logs ai-orchestrator
```

2. **Check GPU access:**
```bash
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
```

3. **Remove GPU requirement:**
If no GPU, edit `docker-compose.yml` and remove the GPU sections.

### Port Already in Use

**Problem:** `Port 8080 already in use`

**Solutions:**

1. **Use different port:**
```bash
docker-compose down
# Edit docker-compose.yml, change port to 8081:8080
docker-compose up -d
```

2. **Find process using port:**
```bash
lsof -i :8080
# Kill the process
kill -9 <PID>
```

## Configuration Issues

### Invalid YAML Syntax

**Problem:** `Error parsing config file`

**Solutions:**

1. **Validate YAML:**
```bash
python -c "import yaml; yaml.safe_load(open('config/models.yaml'))"
```

2. **Check indentation:**
YAML uses spaces, not tabs. Use 2 spaces per level.

3. **Use example configs:**
```bash
# Reset to defaults
git checkout config/
```

### Model Not Loading

**Problem:** Model fails to load

**Solutions:**

1. **Check model exists:**
```bash
ollama list | grep model-name
```

2. **Check memory:**
```bash
free -h
nvidia-smi  # For GPU memory
```

3. **Check model path:**
For llama.cpp, verify model file exists:
```bash
ls -lh models/*.gguf
```

## Network Issues

### Cannot Connect to Orchestrator

**Problem:** `Connection refused`

**Solutions:**

1. **Check service is running:**
```bash
curl http://localhost:8080/health

# If not running
./run.sh
```

2. **Check firewall:**
```bash
sudo ufw status
sudo ufw allow 8080
```

3. **Check binding:**
Service might be bound to 127.0.0.1 instead of 0.0.0.0.
Edit `main.py` or use `--host 0.0.0.0`.

## Development Issues

### Import Errors

**Problem:** `ModuleNotFoundError`

**Solutions:**

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Check virtual environment:**
```bash
which python
# Should point to venv/bin/python

# Activate venv
source venv/bin/activate
```

3. **Add to PYTHONPATH:**
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Tests Failing

**Problem:** Pytest failures

**Solutions:**

1. **Run specific test:**
```bash
pytest tests/test_orchestrator.py::test_name -v
```

2. **Check test dependencies:**
```bash
pip install pytest pytest-asyncio pytest-cov
```

3. **Skip integration tests:**
```bash
pytest -m "not integration"
```

## Logging and Debugging

### Enable Debug Logging

```bash
# Set in .env
LOG_LEVEL=DEBUG

# Or in code
import logging
logging.basicConfig(level=logging.DEBUG)
```

### View Logs

```bash
# Application logs
tail -f logs/orchestrator.log

# Error logs
tail -f logs/errors.log

# Access logs
tail -f logs/access.log

# Docker logs
docker-compose logs -f
```

### Monitor System

```bash
# Use monitoring script
python scripts/monitor.py

# Or check status
curl http://localhost:8080/status -H "X-API-Key: dev-key-12345" | python -m json.tool
```

## Getting Help

If you're still experiencing issues:

1. **Check logs:**
```bash
tail -100 logs/errors.log
```

2. **Run health check:**
```bash
curl http://localhost:8080/health | python -m json.tool
```

3. **Create issue on GitHub:**
Include:
- Python version
- OS and version
- GPU info (if applicable)
- Error logs
- Steps to reproduce

4. **Community support:**
- GitHub Discussions
- Discord server (if available)

## Quick Diagnostic Commands

```bash
# Full system check
make health

# Check all components
python -c "
import asyncio
from core.orchestrator import Orchestrator
async def check():
    orch = Orchestrator()
    await orch.initialize()
    health = await orch.get_health_status()
    print(health)
    await orch.shutdown()
asyncio.run(check())
"

# Test inference
curl -X POST http://localhost:8080/inference \
  -H "X-API-Key: dev-key-12345" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "test", "task_type": "chat"}'
```