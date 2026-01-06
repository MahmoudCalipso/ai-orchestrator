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
3. [Workbench Management](#workbench-management)
4. [Migration Endpoints](#migration-endpoints)
5. [Model Management](#model-management)

---

## System Endpoints

### GET `/`
**Description:** Root endpoint  
**Authentication:** None  
**Response:**
```json
{
  "service": "AI Orchestrator",
  "version": "1.0.0",
  "status": "running"
}
```

### GET `/health`
**Description:** Health check endpoint  
**Authentication:** None  
**Response:**
```json
{
  "status": "healthy",
  "uptime": 3600,
  "components": {
    "llm": "healthy",
    "docker": "healthy",
    "redis": "healthy"
  }
}
```

### GET `/status`
**Description:** Detailed system status  
**Authentication:** Required  
**Response:**
```json
{
  "status": "operational",
  "active_workbenches": 3,
  "active_tasks": 5,
  "memory_usage": "45%",
  "cpu_usage": "30%"
}
```

### GET `/metrics`
**Description:** Prometheus metrics  
**Authentication:** Required  
**Response:** Prometheus format metrics

---

## Universal AI Agent Endpoints

### POST `/api/generate`
**Description:** Generate code in ANY programming language  
**Authentication:** Required

**Request Body:**
```json
{
  "requirements": "Create a REST API with authentication",
  "language": "python",
  "framework": "fastapi"
}
```

**Response:**
```json
{
  "status": "success",
  "result": {
    "task": "Generate production-ready code based on the requirements",
    "solution": "## Analysis\n...\n## Solution\n```python\n...\n```",
    "agent": "UniversalAIAgent"
  }
}
```

**Example (cURL):**
```bash
curl -X POST http://localhost:8080/api/generate \
  -H "X-API-Key: your-key" \
  -H "Content-Type: application/json" \
  -d '{
    "requirements": "Create a web server with JWT authentication",
    "language": "go",
    "framework": "gin"
  }'
```

---

### POST `/api/migrate`
**Description:** Migrate code from ANY stack to ANY stack  
**Authentication:** Required

**Request Body:**
```json
{
  "code": "public class UserController { ... }",
  "source_stack": "Java 8 Spring Boot",
  "target_stack": "Go 1.22 Gin"
}
```

**Response:**
```json
{
  "status": "success",
  "result": {
    "task": "Migrate this code from Java 8 Spring Boot to Go 1.22 Gin",
    "solution": "## Analysis\n...\n## Solution\n```go\n...\n```",
    "agent": "UniversalAIAgent"
  }
}
```

**Supported Migrations:**
- Java → Go, Python, C#, Rust, etc.
- Python → Go, Java, TypeScript, etc.
- JavaScript → TypeScript, Go, Rust, etc.
- **ANY language to ANY language**

---

### POST `/api/fix`
**Description:** Fix code issues in ANY language  
**Authentication:** Required

**Request Body:**
```json
{
  "code": "def process_data(items):\n    for item in items:\n        result.append(item * 2)",
  "issue": "NameError: name 'result' is not defined",
  "language": "python"
}
```

**Response:**
```json
{
  "status": "success",
  "result": {
    "task": "Fix the following issue in the code: NameError",
    "solution": "## Analysis\nThe variable 'result' is not initialized...\n## Solution\n```python\ndef process_data(items):\n    result = []\n    for item in items:\n        result.append(item * 2)\n    return result\n```",
    "agent": "UniversalAIAgent"
  }
}
```

---

### POST `/api/analyze`
**Description:** Analyze code in ANY language  
**Authentication:** Required

**Request Body:**
```json
{
  "code": "function processUser(user) { ... }",
  "language": "javascript",
  "analysis_type": "comprehensive"
}
```

**Analysis Types:**
- `comprehensive` - Full analysis (security, performance, quality)
- `security` - Security vulnerabilities only
- `performance` - Performance issues only

**Response:**
```json
{
  "status": "success",
  "result": {
    "task": "Perform a comprehensive analysis",
    "solution": "## Analysis\n### Security Issues\n- SQL Injection risk...\n### Performance Issues\n- N+1 query problem...",
    "agent": "UniversalAIAgent"
  }
}
```

---

### POST `/api/test`
**Description:** Generate tests for ANY language  
**Authentication:** Required

**Request Body:**
```json
{
  "code": "def calculate_total(items): ...",
  "language": "python",
  "test_framework": "pytest"
}
```

**Response:**
```json
{
  "status": "success",
  "result": {
    "task": "Generate comprehensive unit tests",
    "solution": "## Solution\n```python\nimport pytest\n\ndef test_calculate_total():\n    ...\n```",
    "agent": "UniversalAIAgent"
  }
}
```

---

### POST `/api/optimize`
**Description:** Optimize code in ANY language  
**Authentication:** Required

**Request Body:**
```json
{
  "code": "for i in range(len(items)): ...",
  "language": "python",
  "optimization_goal": "performance"
}
```

**Optimization Goals:**
- `performance` - Improve execution speed
- `memory` - Reduce memory usage
- `readability` - Improve code clarity

**Response:**
```json
{
  "status": "success",
  "result": {
    "task": "Optimize this code for performance",
    "solution": "## Analysis\nCurrent: O(n²)\nOptimized: O(n)\n## Solution\n```python\nfor item in items:\n    ...\n```",
    "agent": "UniversalAIAgent"
  }
}
```

---

### POST `/api/document`
**Description:** Generate documentation for ANY language  
**Authentication:** Required

**Request Body:**
```json
{
  "code": "class UserService { ... }",
  "language": "java",
  "doc_style": "comprehensive"
}
```

**Documentation Styles:**
- `comprehensive` - Full documentation
- `api` - API documentation only
- `user` - User-facing documentation

---

### POST `/api/review`
**Description:** Review code in ANY language  
**Authentication:** Required

**Request Body:**
```json
{
  "code": "function processPayment(amount) { ... }",
  "language": "javascript"
}
```

**Response:**
```json
{
  "status": "success",
  "result": {
    "task": "Perform a thorough code review",
    "solution": "## Strengths\n- Good error handling\n## Issues\n- Missing input validation\n- Security: No amount limit check",
    "agent": "UniversalAIAgent"
  }
}
```

---

### POST `/api/explain`
**Description:** Explain code in ANY language  
**Authentication:** Required

**Request Body:**
```json
{
  "code": "const memoize = fn => { ... }",
  "language": "javascript"
}
```

---

### POST `/api/refactor`
**Description:** Refactor code in ANY language  
**Authentication:** Required

**Request Body:**
```json
{
  "code": "def process_data(data): ...",
  "refactoring_goal": "Extract methods for better readability",
  "language": "python"
}
```

---

### POST `/api/project/analyze`
**Description:** Analyze entire project  
**Authentication:** Required

**Request Body:**
```json
{
  "project_path": "/path/to/project"
}
```

**Response:**
```json
{
  "status": "success",
  "result": {
    "tech_stack": "Java 8 Spring Boot",
    "dependencies": [...],
    "security_issues": [...],
    "recommendations": [...]
  }
}
```

---

### POST `/api/project/migrate`
**Description:** Migrate entire project  
**Authentication:** Required

**Request Body:**
```json
{
  "project_path": "/path/to/project",
  "source_stack": "Java 8 Spring Boot",
  "target_stack": "Go 1.22 Gin"
}
```

---

### POST `/api/project/add-feature`
**Description:** Add feature to project  
**Authentication:** Required

**Request Body:**
```json
{
  "project_path": "/path/to/project",
  "feature_description": "Add user authentication with JWT"
}
```

---

## Workbench Management

### POST `/workbench/create`
**Description:** Create isolated Docker workbench  
**Authentication:** Required

**Request Body:**
```json
{
  "stack": "python-3.12",
  "project_name": "my-project"
}
```

**Supported Stacks:**
- `java-21`, `java-17-spring`
- `dotnet-9`, `dotnet-8`
- `go-1.22`
- `python-3.12`, `python-fastapi`
- `node-20`, `rust-1.75`
- `angular-18`, `react-18`, `vue-3`
- `flutter-3.16`, `react-native`
- `electron`, `tauri`

**Response:**
```json
{
  "status": "success",
  "workbench_id": "wb-abc123",
  "stack": "python-3.12"
}
```

---

### GET `/workbench/list`
**Description:** List all active workbenches  
**Authentication:** Required

**Response:**
```json
{
  "workbenches": [
    {
      "id": "wb-abc123",
      "stack": "python-3.12",
      "status": "running",
      "created_at": "2026-01-06T18:00:00Z"
    }
  ]
}
```

---

### WS `/console/{workbench_id}`
**Description:** WebSocket live terminal  
**Authentication:** Required (via query param)

**Connection:**
```javascript
const ws = new WebSocket('ws://localhost:8080/console/wb-abc123?api_key=your-key');

ws.onmessage = (event) => {
  console.log('Output:', event.data);
};

ws.send('ls -la\n');
```

---

## Migration Endpoints

### POST `/migration/start`
**Description:** Start universal migration  
**Authentication:** Required

**Request Body:**
```json
{
  "source_stack": "java-8",
  "target_stack": "go-1.22",
  "project_path": "/path/to/project"
}
```

**Response:**
```json
{
  "status": "success",
  "workbench_id": "wb-xyz789",
  "preview_url": "https://preview-xyz789.localhost:8080",
  "build_script": "#!/bin/bash\n..."
}
```

---

## Model Management

### GET `/models`
**Description:** List available models  
**Authentication:** Required

**Response:**
```json
[
  {
    "name": "gpt-4-turbo-preview",
    "provider": "openai",
    "status": "available"
  }
]
```

---

### GET `/models/{model_name}`
**Description:** Get model information  
**Authentication:** Required

---

### POST `/inference`
**Description:** Run inference  
**Authentication:** Required

**Request Body:**
```json
{
  "prompt": "Explain quantum computing",
  "model": "gpt-4-turbo-preview",
  "task_type": "text-generation",
  "parameters": {
    "temperature": 0.7,
    "max_tokens": 1000
  }
}
```

---

## Error Responses

All endpoints return standard error responses:

```json
{
  "detail": "Error message here"
}
```

**Status Codes:**
- `200` - Success
- `400` - Bad Request
- `401` - Unauthorized (missing/invalid API key)
- `404` - Not Found
- `500` - Internal Server Error

---

## Rate Limiting

Currently no rate limiting. Will be added in future versions.

---

## Examples

### Python Example
```python
import requests

API_KEY = "your-api-key"
BASE_URL = "http://localhost:8080"

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

# Generate code
response = requests.post(
    f"{BASE_URL}/api/generate",
    headers=headers,
    json={
        "requirements": "Create a web server",
        "language": "python",
        "framework": "fastapi"
    }
)

print(response.json())
```

### JavaScript Example
```javascript
const API_KEY = 'your-api-key';
const BASE_URL = 'http://localhost:8080';

async function generateCode() {
  const response = await fetch(`${BASE_URL}/api/generate`, {
    method: 'POST',
    headers: {
      'X-API-Key': API_KEY,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      requirements: 'Create a web server',
      language: 'node',
      framework: 'express'
    })
  });
  
  const data = await response.json();
  console.log(data);
}
```

---

## WebSocket Example

```javascript
const ws = new WebSocket('ws://localhost:8080/console/wb-abc123?api_key=your-key');

ws.onopen = () => {
  console.log('Connected to terminal');
  ws.send('echo "Hello World"\n');
};

ws.onmessage = (event) => {
  console.log('Terminal output:', event.data);
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};
```

---

## Summary

**Total Endpoints:** 25+

**Categories:**
- System: 4 endpoints
- Universal AI Agent: 13 endpoints
- Workbench Management: 3 endpoints
- Migration: 1 endpoint
- Model Management: 4 endpoints

**All endpoints support ANY programming language!** 🚀
