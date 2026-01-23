# 🐳 IA-ORCHESTRATOR 2026 - DOCKER DEPLOYMENT GUIDE
## Enterprise-Grade Container Deployment

**Version:** 2.0.0  
**Status:** Production Ready  
**Security Level:** Enterprise Grade

---

## 🚀 QUICK START

### Prerequisites
- Docker 24.0+ with BuildKit enabled
- Docker Compose 2.20+
- 16GB+ RAM (32GB recommended)
- NVIDIA GPU (optional, for AI models)

### One-Command Deployment

```bash
# 1. Clone and setup
git clone <your-repo>
cd IA-ORCH

# 2. Create environment file
cp .env.example .env

# 3. Generate secure keys
python3 -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_urlsafe(32))" >> .env
python3 -c "from cryptography.fernet import Fernet; print('MASTER_ENCRYPTION_KEY=' + Fernet.generate_key().decode())" >> .env

# 4. Set passwords in .env
# Edit .env and set: POSTGRES_PASSWORD, MONGO_PASSWORD, REDIS_PASSWORD

# 5. Start everything
docker-compose up -d

# 6. Download AI models (choose tier)
MODEL_TIER=balanced docker-compose up model-downloader
```

**Access Points:**
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

---

## 📦 WHAT'S INCLUDED

### Services

| Service | Port | Description |
|---------|------|-------------|
| **ai-orchestrator** | 8000 | Main API application |
| **postgres** | 5432 | Primary database |
| **redis** | 6379 | Cache & real-time |
| **mongodb** | 27017 | Document store |
| **qdrant** | 6333 | Vector database |
| **ollama** | 11434 | AI model engine |

### Security Features

✅ **Non-root containers** - All services run as unprivileged users  
✅ **Read-only filesystems** - Where possible  
✅ **Resource limits** - CPU and memory constraints  
✅ **Health checks** - Automatic restart on failure  
✅ **Network isolation** - Private bridge network  
✅ **Secret management** - Environment-based configuration  
✅ **No hardcoded credentials** - All from .env

---

## 🔧 CONFIGURATION

### Environment Variables

Create `.env` from `.env.example`:

```bash
# Security (REQUIRED - Generate unique values)
JWT_SECRET_KEY=<generate-with-command-above>
MASTER_ENCRYPTION_KEY=<generate-with-command-above>

# Database Passwords (REQUIRED - Change these!)
POSTGRES_PASSWORD=your_secure_postgres_password
MONGO_PASSWORD=your_secure_mongo_password
REDIS_PASSWORD=your_secure_redis_password

# CORS (REQUIRED for production)
ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com

# Model Tier (optional, default: balanced)
MODEL_TIER=balanced  # Options: minimal, balanced, full, ultra
```

### Model Tiers

| Tier | RAM Required | Models | Use Case |
|------|--------------|--------|----------|
| **minimal** | 16GB | qwen2.5-coder:7b, glm4:9b | Development, testing |
| **balanced** | 32GB | qwen2.5-coder:14b, codellama:13b | Recommended for production |
| **full** | 64GB | qwen2.5-coder:32b, deepseek-r1:32b | High performance |
| **ultra** | 128GB+ | qwen3:235b, deepseek-r1:70b | Maximum quality |

---

## 🎯 DEPLOYMENT COMMANDS

### Basic Operations

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Restart services
docker-compose restart

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f ai-orchestrator

# Check status
docker-compose ps

# Check health
curl http://localhost:8000/health
```

### Model Management

```bash
# Download minimal models (16GB RAM)
MODEL_TIER=minimal docker-compose up model-downloader

# Download balanced models (32GB RAM) - Recommended
MODEL_TIER=balanced docker-compose up model-downloader

# Download full power models (64GB+ RAM)
MODEL_TIER=full docker-compose up model-downloader

# List downloaded models
curl http://localhost:11434/api/tags

# Pull specific model manually
docker-compose exec ollama ollama pull qwen2.5-coder:7b
```

### Database Operations

```bash
# Run migrations
docker-compose exec ai-orchestrator alembic upgrade head

# PostgreSQL shell
docker-compose exec postgres psql -U orchestrator -d ai_orchestrator

# Backup database
docker-compose exec -T postgres pg_dump -U orchestrator ai_orchestrator > backup.sql

# Restore database
docker-compose exec -T postgres psql -U orchestrator ai_orchestrator < backup.sql

# Redis CLI
docker-compose exec redis redis-cli

# MongoDB shell
docker-compose exec mongodb mongosh -u orchestrator -p
```

### Debugging

```bash
# Shell into main container
docker-compose exec ai-orchestrator /bin/bash

# View resource usage
docker stats

# Inspect container
docker inspect ia-orchestrator

# View container logs with timestamps
docker-compose logs -f --timestamps ai-orchestrator
```

---

## 🔒 SECURITY HARDENING

### Production Checklist

- [ ] Change all default passwords in `.env`
- [ ] Generate unique JWT and encryption keys
- [ ] Set `ALLOWED_ORIGINS` to your actual domains
- [ ] Enable HTTPS with reverse proxy (nginx/traefik)
- [ ] Set up firewall rules
- [ ] Enable Docker content trust
- [ ] Regular security updates
- [ ] Monitor logs for suspicious activity
- [ ] Set up automated backups
- [ ] Configure log rotation

### Recommended nginx Configuration

```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 📊 MONITORING

### Health Checks

```bash
# API health
curl http://localhost:8000/health

# Ollama health
curl http://localhost:11434/api/tags

# PostgreSQL health
docker-compose exec postgres pg_isready -U orchestrator

# Redis health
docker-compose exec redis redis-cli ping

# All services status
docker-compose ps
```

### Metrics

```bash
# View resource usage
docker stats --no-stream

# View logs
docker-compose logs --tail=100 -f

# Check disk usage
docker system df
```

---

## 🔄 UPDATES & MAINTENANCE

### Updating the Application

```bash
# Pull latest code
git pull

# Rebuild images
docker-compose build --no-cache

# Restart with new images
docker-compose up -d

# Run migrations
docker-compose exec ai-orchestrator alembic upgrade head
```

### Cleanup

```bash
# Stop and remove containers
docker-compose down

# Remove volumes (⚠️ deletes data!)
docker-compose down -v

# Clean Docker system
docker system prune -af

# Remove unused volumes
docker volume prune -f
```

---

## 🐛 TROUBLESHOOTING

### Common Issues

**Issue: Container won't start**
```bash
# Check logs
docker-compose logs ai-orchestrator

# Check if port is in use
netstat -tulpn | grep 8000

# Restart service
docker-compose restart ai-orchestrator
```

**Issue: Database connection failed**
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Check PostgreSQL logs
docker-compose logs postgres

# Verify credentials in .env
cat .env | grep POSTGRES
```

**Issue: Models not downloading**
```bash
# Check Ollama logs
docker-compose logs ollama

# Manually pull model
docker-compose exec ollama ollama pull qwen2.5-coder:7b

# Check disk space
df -h
```

**Issue: Out of memory**
```bash
# Check memory usage
docker stats

# Reduce model tier in .env
MODEL_TIER=minimal

# Increase Docker memory limit in Docker Desktop settings
```

---

## 🚀 PRODUCTION DEPLOYMENT

### AWS/Cloud Deployment

```bash
# 1. Set up EC2 instance (t3.2xlarge or larger)
# 2. Install Docker and Docker Compose
# 3. Clone repository
# 4. Configure .env with production values
# 5. Set up SSL certificates
# 6. Configure security groups
# 7. Deploy

docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Kubernetes Deployment

```bash
# Convert docker-compose to Kubernetes manifests
kompose convert

# Apply to cluster
kubectl apply -f .

# Check status
kubectl get pods
```

---

## 📈 PERFORMANCE TUNING

### Resource Allocation

Edit `docker-compose.yml` to adjust resources:

```yaml
deploy:
  resources:
    limits:
      cpus: '8'
      memory: 16G
    reservations:
      cpus: '4'
      memory: 8G
```

### Database Optimization

PostgreSQL tuning in `docker-compose.yml`:

```yaml
command: >
  postgres
  -c shared_buffers=512MB
  -c effective_cache_size=2GB
  -c max_connections=200
```

---

## 📞 SUPPORT

### Getting Help

- Documentation: `/docs` in this repository
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health
- Logs: `docker-compose logs -f`

### Reporting Issues

Include:
1. Docker version: `docker --version`
2. Docker Compose version: `docker-compose --version`
3. OS and version
4. Error logs: `docker-compose logs`
5. Configuration (without secrets)

---

## ✅ POST-DEPLOYMENT CHECKLIST

- [ ] All services running: `docker-compose ps`
- [ ] Health check passing: `curl http://localhost:8000/health`
- [ ] Models downloaded: `curl http://localhost:11434/api/tags`
- [ ] Database accessible: `docker-compose exec postgres pg_isready`
- [ ] API docs accessible: http://localhost:8000/docs
- [ ] Logs clean: `docker-compose logs --tail=50`
- [ ] Backups configured
- [ ] Monitoring set up
- [ ] SSL configured (production)
- [ ] Firewall rules set

---

**🎉 Your IA-Orchestrator is now deployed and ready to dominate 2026!**
