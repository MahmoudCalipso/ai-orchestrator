# AI Orchestrator - Authentication System Setup Guide

## Overview

This guide walks you through setting up the enterprise-grade authentication and multi-tenancy system for AI Orchestrator.

## Prerequisites

- Python 3.12+
- PostgreSQL 15+
- Redis 7+
- Docker (optional, for containerized setup)

## Step 1: Install Dependencies

All required dependencies are already in `requirements.txt`:

```bash
pip install -r requirements.txt
```

Key authentication packages:
- `python-jose[cryptography]` - JWT token handling
- `passlib[bcrypt]` - Password hashing
- `redis` - Token storage and rate limiting
- `sqlalchemy` - Database ORM
- `psycopg2-binary` - PostgreSQL driver

## Step 2: Set Up PostgreSQL Database

### Option A: Local PostgreSQL

```bash
# Create database
createdb ai_orchestrator

# Or using psql
psql -U postgres
CREATE DATABASE ai_orchestrator;
```

### Option B: Docker PostgreSQL

```bash
docker run -d \
  --name ai-orchestrator-db \
  -e POSTGRES_DB=ai_orchestrator \
  -e POSTGRES_USER=ai_user \
  -e POSTGRES_PASSWORD=secure_password \
  -p 5432:5432 \
  postgres:15-alpine
```

## Step 3: Set Up Redis

### Option A: Local Redis

```bash
# Install Redis
# Windows: Download from https://github.com/microsoftarchive/redis/releases
# Linux: sudo apt-get install redis-server
# Mac: brew install redis

# Start Redis
redis-server
```

### Option B: Docker Redis

```bash
docker run -d \
  --name ai-orchestrator-redis \
  -p 6379:6379 \
  redis:7-alpine
```

## Step 4: Generate Security Keys

Run this Python script to generate secure keys:

```python
import secrets
from cryptography.fernet import Fernet

print("=" * 60)
print("AI Orchestrator - Security Keys Generator")
print("=" * 60)
print()

# JWT Secret Key
jwt_secret = secrets.token_urlsafe(32)
print("JWT_SECRET_KEY=" + jwt_secret)
print()

# Master Encryption Key
encryption_key = Fernet.generate_key().decode()
print("MASTER_ENCRYPTION_KEY=" + encryption_key)
print()

print("=" * 60)
print("Copy these values to your .env file")
print("=" * 60)
```

Save this as `generate_keys.py` and run:

```bash
python generate_keys.py
```

## Step 5: Configure Environment Variables

1. Copy the example environment file:

```bash
cp .env.example .env
```

2. Edit `.env` and update the following **critical** variables:

```bash
# Security (use generated keys from Step 4)
JWT_SECRET_KEY=<your-generated-jwt-secret>
MASTER_ENCRYPTION_KEY=<your-generated-encryption-key>

# Database
DATABASE_URL=postgresql://ai_user:secure_password@localhost:5432/ai_orchestrator

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
```

## Step 6: Run Database Migration

Create the authentication and multi-tenancy tables:

```bash
python platform/database_migration.py
```

This creates the following tables:
- `tenants` - Multi-tenancy support
- `users` - User accounts
- `api_keys` - API key management
- `refresh_tokens` - JWT refresh tokens

## Step 7: Verify Setup

Test the database connection:

```python
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv()

engine = create_engine(os.getenv("DATABASE_URL"))
with engine.connect() as conn:
    result = conn.execute("SELECT 1")
    print("✅ Database connection successful!")
```

Test Redis connection:

```python
import redis
import os
from dotenv import load_dotenv

load_dotenv()

r = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=0
)
r.ping()
print("✅ Redis connection successful!")
```

## Step 8: Start the Application

Update `main.py` to include authentication routes:

```python
from fastapi import FastAPI
from platform.auth.routes import router as auth_router

app = FastAPI(title="AI Orchestrator", version="2.0.0")

# Include authentication routes
app.include_router(auth_router)

# ... existing routes ...
```

Start the server:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8080
```

## Step 9: Test Authentication Endpoints

### Register a New User

```bash
curl -X POST http://localhost:8080/api/v2/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123",
    "full_name": "Test User",
    "tenant_name": "My Company"
  }'
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Login

```bash
curl -X POST http://localhost:8080/api/v2/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123"
  }'
```

### Get Current User Info

```bash
curl -X GET http://localhost:8080/api/v2/auth/me \
  -H "Authorization: Bearer <your-access-token>"
```

### Create API Key

```bash
curl -X POST http://localhost:8080/api/v2/auth/api-keys \
  -H "Authorization: Bearer <your-access-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My API Key",
    "expires_in_days": 90
  }'
```

## Step 10: Protect Existing Endpoints

Add authentication to existing endpoints:

```python
from fastapi import Depends
from platform.auth.dependencies import get_current_active_user, require_permission
from platform.auth.models import User
from platform.auth.rbac import Permission

@app.post("/api/generate")
async def generate_code(
    request: GenerationRequest,
    current_user: User = Depends(
        require_permission(Permission.CODE_GENERATE)
    )
):
    # Your existing logic
    pass
```

## Subscription Tiers & Permissions

### Free Tier
- 10 GB storage
- 3 concurrent workbenches
- 100 API requests/minute
- Basic code generation

### Developer Tier ($29/month)
- 50 GB storage
- 10 concurrent workbenches
- 500 API requests/minute
- Code migration
- Figma integration
- Database reverse engineering

### Pro Tier ($99/month)
- 200 GB storage
- Unlimited workbenches
- 2000 API requests/minute
- Swarm agents
- Kubernetes deployment
- Real-time collaboration

### Enterprise Tier ($499/month)
- Unlimited storage
- Unlimited workbenches
- Unlimited API requests
- Dedicated support
- Custom integrations
- On-premise deployment

## Security Best Practices

1. **Never commit `.env` file** - It's already in `.gitignore`
2. **Use strong passwords** - Minimum 8 characters with uppercase, lowercase, and digits
3. **Rotate JWT secrets regularly** - Especially after security incidents
4. **Enable HTTPS in production** - Use Let's Encrypt or similar
5. **Monitor failed login attempts** - Implement rate limiting
6. **Regular security audits** - Review access logs and permissions

## Troubleshooting

### Database Connection Error

```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Solution**: Verify PostgreSQL is running and credentials are correct in `.env`

### Redis Connection Error

```
redis.exceptions.ConnectionError: Error connecting to Redis
```

**Solution**: Verify Redis is running on the specified host/port

### JWT Token Invalid

```
401 Unauthorized: Token validation failed
```

**Solution**: 
- Check if `JWT_SECRET_KEY` matches between token creation and validation
- Verify token hasn't expired
- Ensure Redis is running for refresh token validation

## Next Steps

1. **Set up billing** - Integrate Stripe for subscription management (Phase 2)
2. **Add rate limiting** - Implement Redis-based rate limiter (Phase 3)
3. **Enable monitoring** - Set up OpenTelemetry and Grafana (Phase 6)
4. **Deploy to production** - Use Docker Compose or Kubernetes

## Support

For issues or questions:
- GitHub Issues: https://github.com/your-repo/ai-orchestrator/issues
- Email: ammarmahmoud1996@gmail.com
