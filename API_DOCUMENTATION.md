# AI Orchestrator - Complete API Documentation

## 🚀 Base URL
```
http://localhost:8080
```

## 🔐 Authentication
All endpoints (except `/` and `/health`) require an API key in the header:
```
X-API-Key: your-api-key-here
```

---

## 📋 Table of Contents

1. [System Endpoints](#system-endpoints)
2. [Universal AI Agent Endpoints](#universal-ai-agent-endpoints)
3. [Application Generation](#application-generation)
4. [Application Migration](#application-migration)
5. [Database Management](#database-management)
6. [Registry & Models](#registry--models)
7. [Figma Integration](#figma-integration)
8. [Security & Tools](#security--tools)
9. [Workbench Management](#workbench-management)

---

## System Endpoints

### GET `/`
- **Description:** Root endpoint
- **Response:** `{"service": "AI Orchestrator", "status": "running"}`

### GET `/health`
- **Description:** Health check
- **Response:** `{"status": "healthy", ...}`

---

## Universal AI Agent Endpoints

### POST `/api/generate`
**Description:** Generate code or full applications. Supports simple code snippets or complex full-stack projects.

**Request Body (Complex Project):**
```json
{
  "project_name": "MyECommerce",
  "project_types": ["web", "mobile"],
  "languages": {
    "backend": "Rust",
    "frontend": "Angular",
    "mobile": "Flutter"
  },
  "database": {
     "type": "postgresql",
     "database_name": "mydb"
  },
  "template": {
    "linkPath": "https://themeforest.net/...",
    "figmaFile": "key123"
  },
  "entities": [
    {
      "name": "Product",
      "fields": [{"name": "name", "type": "string"}, {"name": "price", "type": "decimal"}]
    }
  ],
  "git": {
    "create_repo": true,
    "provider": "github"
  },
  "kubernetes": {
     "enabled": true,
     "environment": "production"
  }
}
```

**Request Body (Simple Snippet):**
```json
{
  "requirements": "Create a function to reverse a string",
  "language": "python"
}
```

---

### POST `/api/migrate`
**Description:** Migrate applications or code snippets between stacks.

**Request Body:**
```json
{
  "source_path": "/path/to/legacy-app",
  "source_stack": "Java 8 Spring Boot",
  "target_stack": "Go 1.22 Gin",
  "target_architecture": "clean_architecture",
  "git": {
     "create_repo": true
  }
}
```

---

## Database Management

### POST `/api/database/analyze`
**Description:** Analyze an existing database to extract entity definitions.

**Request Body:**
```json
{
  "type": "postgresql",
  "host": "localhost",
  "port": 5432,
  "database_name": "legacy_db",
  "username": "user",
  "password": "password"
}
```

### POST `/api/entity/generate`
**Description:** Generate code models and APIs from entity definitions.

**Request Body:**
```json
{
  "language": "python",
  "framework": "fastapi",
  "entities": [...]
}
```

---

## Registry & Models

### GET `/api/registry/languages`
**Description:** List all supported languages, frameworks, and packages.

### GET `/models`
**Description:** List available AI models for inference.

---

## Figma Integration

### POST `/api/figma/analyze`
**Description:** Analyze a Figma design file.

**Request Body:**
```json
{
  "file_key": "abc12345",
  "token": "figd_..."
}
```

---

## Security & Tools

### POST `/api/security/scan`
**Description:** Scan project for vulnerabilities.

**Request Body:**
```json
{
  "project_path": "/path/to/project",
  "type": "all"  // code, dependencies, or all
}
```

### POST `/api/kubernetes/generate`
**Description:** Generate Kubernetes manifests.

**Request Body:**
```json
{
  "app_name": "my-app",
  "image": "my-registry/my-app:v1",
  "config": {
    "replicas": 3,
    "namespace": "prod"
  }
}
```

### POST `/git/repositories/init`
**Description:** Initialize a Git repository.

**Request Body:**
```json
{
  "path": "/path/to/project"
}
```

---

## Workbench Management

### POST `/workbench/create`
**Description:** Create an isolated Docker workbench for development.
