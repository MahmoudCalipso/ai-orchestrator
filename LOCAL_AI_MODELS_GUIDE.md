# AI Orchestrator - Local AI Models Setup Guide

## 🚀 Using Open-Source AI Models (No API Keys Required!)

Your AI Orchestrator can run **100% locally** using open-source models via **Ollama**.

**Benefits:**
- ✅ **No API keys** required
- ✅ **Unlimited usage** (no costs)
- ✅ **Complete privacy** (data stays local)
- ✅ **No internet** required (after download)
- ✅ **Memory optimized** (configurable)

---

## 📦 Step 1: Install Ollama

### Windows
```powershell
# Download and install Ollama
winget install Ollama.Ollama

# Or download from: https://ollama.ai/download
```

### Verify Installation
```powershell
ollama --version
```

---

## 🤖 Step 2: Download AI Models

### Recommended Models for Coding

#### 1. **CodeLlama 13B** (Recommended - Best Balance)
```powershell
ollama pull codellama:13b
```
- **Size:** ~7GB
- **RAM:** 8GB required
- **Best for:** Code generation, migration, fixing
- **Speed:** Fast

#### 2. **DeepSeek Coder 6.7B** (Fastest)
```powershell
ollama pull deepseek-coder:6.7b
```
- **Size:** ~3.8GB
- **RAM:** 4GB required
- **Best for:** Quick code tasks
- **Speed:** Very fast

#### 3. **CodeLlama 34B** (Best Quality)
```powershell
ollama pull codellama:34b
```
- **Size:** ~19GB
- **RAM:** 20GB required
- **Best for:** Complex migrations, large projects
- **Speed:** Slower but highest quality

#### 4. **Phind CodeLlama 34B** (Code-Specialized)
```powershell
ollama pull phind-codellama:34b
```
- **Size:** ~19GB
- **RAM:** 20GB required
- **Best for:** Advanced coding tasks
- **Speed:** Slower but excellent results

### General Purpose Models

#### 5. **Mistral 7B** (Fast & Smart)
```powershell
ollama pull mistral:7b
```
- **Size:** ~4.1GB
- **RAM:** 4GB required
- **Best for:** General tasks, explanations
- **Speed:** Very fast

#### 6. **Llama 2 13B** (Balanced)
```powershell
ollama pull llama2:13b
```
- **Size:** ~7GB
- **RAM:** 8GB required
- **Best for:** General AI tasks
- **Speed:** Fast

---

## ⚙️ Step 3: Configure AI Orchestrator

### Create `.env` file
```powershell
# Copy example configuration
Copy-Item .env.example .env

# Edit .env file
notepad .env
```

### Set Ollama as Default Provider
```bash
# In .env file
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=codellama:13b
```

---

## 🎯 Step 4: Memory Optimization

### For Low Memory Systems (8GB RAM)
```bash
# In .env file
OLLAMA_MODEL=deepseek-coder:6.7b  # Smaller model
OLLAMA_NUM_CTX=2048  # Smaller context window
OLLAMA_LOW_VRAM=true  # Enable low VRAM mode
```

### For Medium Memory Systems (16GB RAM)
```bash
# In .env file
OLLAMA_MODEL=codellama:13b  # Balanced model
OLLAMA_NUM_CTX=4096  # Standard context
OLLAMA_NUM_GPU=1  # Use GPU if available
```

### For High Memory Systems (32GB+ RAM)
```bash
# In .env file
OLLAMA_MODEL=codellama:34b  # Best quality
OLLAMA_NUM_CTX=8192  # Large context
OLLAMA_NUM_GPU=1  # Use GPU
```

---

## 🚀 Step 5: Start AI Orchestrator

```powershell
# Start Ollama (if not running)
ollama serve

# In another terminal, start AI Orchestrator
.\start.ps1
```

---

## 📊 Model Comparison

| Model | Size | RAM | Speed | Quality | Best For |
|-------|------|-----|-------|---------|----------|
| **deepseek-coder:6.7b** | 3.8GB | 4GB | ⚡⚡⚡⚡⚡ | ⭐⭐⭐⭐ | Quick tasks |
| **codellama:13b** | 7GB | 8GB | ⚡⚡⚡⚡ | ⭐⭐⭐⭐⭐ | **Recommended** |
| **mistral:7b** | 4.1GB | 4GB | ⚡⚡⚡⚡⚡ | ⭐⭐⭐⭐ | General use |
| **codellama:34b** | 19GB | 20GB | ⚡⚡⚡ | ⭐⭐⭐⭐⭐ | Complex tasks |
| **mixtral:8x7b** | 26GB | 26GB | ⚡⚡ | ⭐⭐⭐⭐⭐ | Best quality |

---

## 🔧 Advanced Configuration

### Use Multiple Models
```python
# The orchestrator can switch between models
# Set in .env:
OLLAMA_MODEL=codellama:13b  # Default

# Or specify per request:
POST /api/generate
{
  "requirements": "Create a web server",
  "language": "python",
  "model": "deepseek-coder:6.7b"  # Override default
}
```

### GPU Acceleration
```bash
# In .env file
OLLAMA_NUM_GPU=1  # Use 1 GPU
# OLLAMA_NUM_GPU=0  # CPU only
```

### Context Window Size
```bash
# Larger = more memory, better context
OLLAMA_NUM_CTX=2048  # Small (2K tokens)
OLLAMA_NUM_CTX=4096  # Medium (4K tokens)
OLLAMA_NUM_CTX=8192  # Large (8K tokens)
```

---

## 📋 Quick Start Commands

```powershell
# 1. Install Ollama
winget install Ollama.Ollama

# 2. Download recommended model
ollama pull codellama:13b

# 3. Start Ollama
ollama serve

# 4. Configure AI Orchestrator
Copy-Item .env.example .env
# Edit .env: Set LLM_PROVIDER=ollama

# 5. Start AI Orchestrator
.\start.ps1

# 6. Test
curl -X POST http://localhost:8080/api/generate `
  -H "X-API-Key: dev-key-12345" `
  -H "Content-Type: application/json" `
  -d '{"requirements": "Create hello world", "language": "python"}'
```

---

## 🎯 Model Management

### List Downloaded Models
```powershell
ollama list
```

### Remove Model (Free Space)
```powershell
ollama rm codellama:34b
```

### Update Model
```powershell
ollama pull codellama:13b
```

### Check Model Info
```powershell
ollama show codellama:13b
```

---

## 💡 Tips for Best Performance

### 1. **Choose Right Model**
- **4GB RAM:** Use `deepseek-coder:6.7b` or `mistral:7b`
- **8GB RAM:** Use `codellama:13b` (recommended)
- **16GB+ RAM:** Use `codellama:34b` or `mixtral:8x7b`

### 2. **Optimize Context**
- Reduce `OLLAMA_NUM_CTX` if running out of memory
- Increase for better understanding of large codebases

### 3. **Use GPU**
- Set `OLLAMA_NUM_GPU=1` if you have NVIDIA GPU
- Dramatically faster inference

### 4. **Batch Operations**
- Process multiple files in one request
- Reduces model loading overhead

---

## 🔄 Switching Between Providers

You can use **both local and cloud models**:

```bash
# In .env file

# Option 1: Local only (no API keys)
LLM_PROVIDER=ollama
OLLAMA_MODEL=codellama:13b

# Option 2: OpenAI (requires API key)
LLM_PROVIDER=openai
OPENAI_API_KEY=your-key

# Option 3: Hybrid (local as default, OpenAI as fallback)
LLM_PROVIDER=ollama
OLLAMA_MODEL=codellama:13b
OPENAI_API_KEY=your-key  # Used if Ollama fails
```

---

## ✅ Verification

### Test Local Model
```powershell
# Test Ollama directly
ollama run codellama:13b "Write a Python hello world"

# Test via AI Orchestrator
curl -X POST http://localhost:8080/api/generate `
  -H "X-API-Key: dev-key-12345" `
  -H "Content-Type: application/json" `
  -d '{"requirements": "Create hello world", "language": "python"}'
```

---

## 🎉 You're Ready!

**No API keys needed!**
**Unlimited usage!**
**Complete privacy!**
**Memory optimized!**

Your AI Orchestrator now runs **100% locally** with open-source models! 🚀

---

## 📚 Additional Resources

- **Ollama Models:** https://ollama.ai/library
- **Model Performance:** https://ollama.ai/blog/performance
- **GPU Support:** https://github.com/ollama/ollama/blob/main/docs/gpu.md
