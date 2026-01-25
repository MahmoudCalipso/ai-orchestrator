# 🚀 AI Orchestrator - Simple Docker Deployment Guide

## 📋 Quick Start

### 1. Essential Services Only (Recommended to Start)
```bash
docker-compose up -d
```
**Includes:** PostgreSQL, Redis, CloudBeaver UI

---

### 2. Add Databases
```bash
docker-compose --profile databases up -d
```
**Adds:** MongoDB, Qdrant

---

### 3. Add AI Models (Choose Your Tier)

#### 🐧 Bash (Linux/macOS)
```bash
# Minimal tier (16GB RAM)
MODEL_TIER=minimal docker-compose --profile ai up -d

# Balanced tier (32GB RAM)
MODEL_TIER=balanced docker-compose --profile ai up -d
```

#### 🪟 PowerShell (Windows)
```powershell
# Minimal tier (16GB RAM)
$env:MODEL_TIER="minimal"; docker-compose --profile ai up -d

# Balanced tier (32GB RAM)
$env:MODEL_TIER="balanced"; docker-compose --profile ai up -d
```
**Adds:** Ollama + Auto-downloads models

---

### 4. Full Stack (Everything)

#### 🐧 Bash
```bash
MODEL_TIER=minimal docker-compose --profile full up -d --build
```

#### 🪟 PowerShell
```powershell
$env:MODEL_TIER="minimal"; docker-compose --profile full up -d --build
```

---

## 🎯 Model Tiers

| Tier | RAM | Models | Download Size |
|------|-----|--------|---------------|
| **minimal** | 16GB | qwen2.5-coder:7b, glm4:9b | ~12GB |
| **balanced** | 32GB | qwen2.5-coder:14b, glm4:9b, codellama:13b | ~30GB |
| **full** | 64GB | qwen2.5-coder:32b, deepseek-r1:32b-q4 | ~60GB |
| **ultra** | 128GB | qwen3:235b-q4, deepseek-r1:70b-q4 | ~180GB |

---

## 📦 What's Included

### Base (Always Runs)
- ✅ PostgreSQL (Port 5432)
- ✅ Redis (Port 6379)

### Profile: `databases`
- ✅ CloudBeaver UI (Port 8978)
- ✅ MongoDB (Port 27017)
- ✅ Qdrant (Port 6333)

### Profile: `ai`
- ✅ Ollama (Port 11434)
- ✅ Model Downloader (runs once)

### Profile: `app`
- ✅ AI Orchestrator (Port 8000)

### Profile: `full`
- ✅ Everything above

---

## 🛠️ Common Commands

### View Running Services
```bash
docker-compose ps
```

### View Logs
```bash
# All containers
docker-compose logs -f

# Just the model downloader (to see download progress)
docker-compose logs -f model-downloader
```

### Stop Everything
```bash
docker-compose --profile full down
```

### Restart
```bash
docker-compose restart
```

### Clean Everything
```bash
docker-compose --profile full down -v
docker system prune -f
```

---

## 🔧 Change Model Tier

### Download Different Models
```bash
# Stop current Ollama
docker-compose stop ollama model-downloader

# Download new tier
MODEL_TIER=balanced docker-compose up model-downloader

# Restart Ollama
docker-compose start ollama
```

---

## ✅ Access Points

- **CloudBeaver**: http://localhost:8978 (admin/admin)
- **AI Orchestrator**: http://localhost:8000
- **Ollama API**: http://localhost:11434

---

## 📝 Configuration

Edit `.env` file:
```env
# Database
POSTGRES_PASSWORD=your_password
MONGO_PASSWORD=your_password

# Model Tier (minimal, balanced, full, ultra)
MODEL_TIER=minimal

# Ports (optional)
POSTGRES_PORT=5432
REDIS_PORT=6379
CLOUDBEAVER_PORT=8978
```

---

## 🎯 Recommended Workflow

1. **Start with essentials**: `docker-compose up -d`
2. **Add databases if needed**: `docker-compose --profile databases up -d`
3. **Add AI when ready**: `MODEL_TIER=minimal docker-compose --profile ai up -d`
4. **Build your app**: `docker-compose --profile app up -d --build`
