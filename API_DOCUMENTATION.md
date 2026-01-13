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
2. [AI Agent Endpoints](#ai-agent-endpoints)
3. [Project Lifecycle](#project-lifecycle)
4. [IDE Services](#ide-services)
5. [Monitoring](#monitoring)
6. [Collaboration](#collaboration)
7. [Workspace Management](#workspace-management)
8. [Storage Management](#storage-management)
9. [Git Integration](#git-integration)
10. [Database & Figma](#database--figma)
11. [Infrastructure](#infrastructure)

---

## System Endpoints

### GET `/`
- **Description:** Root endpoint to verify service status.
- **Response:** `{"service": "AI Orchestrator", "version": "1.0.0", "status": "running"}`

### GET `/health`
- **Description:** Comprehensive health check of the orchestrator and runtimes.
- **Response:** `{"status": "healthy", ...}`

### GET `/status`
- **Description:** Detailed system metrics and resource usage.
- **Security:** Requires API Key.

### GET `/models`
- **Description:** List all available AI models.

---

## AI Agent Endpoints

### POST `/api/generate`
- **Description:** Generate code or full applications.
- **Capabilities:** Database integration, Figma conversion, etc.

### POST `/api/migrate`
- **Description:** Migrate applications between stacks (e.g., Java -> Go).

### POST `/api/fix`
- **Description:** Automatically identify and resolve code issues.

### POST `/api/analyze`
- **Description:** Analyze code quality and security.

### POST `/api/test`
- **Description:** Generate unit and integration tests.

### POST `/api/optimize`
- **Description:** Optimize code for performance or readability.

### POST `/api/refactor`
- **Description:** Apply architectural or logic refactorings.

### POST `/api/explain`
- **Description:** Multi-language code explanation.

---

## IDE Services

### POST `/api/ide/workspace`
- **Description:** Create an isolated IDE workspace.

### GET `/api/ide/files/{workspace_id}`
- **Description:** List files in a workspace.

### GET/POST/DELETE `/api/ide/files/{workspace_id}/{path}`
- **Description:** File operations within a workspace.

### WebSocket `/api/ide/terminal/{session_id}`
- **Description:** Real-time terminal access.

---

## Monitoring

### GET `/api/monitoring/metrics`
- **Description:** History of system and project metrics.

### WebSocket `/api/monitoring/stream`
- **Description:** Live system metrics stream.

### GET `/api/monitoring/builds`
- **Description:** Track active and completed builds.

---

## Collaboration

### POST `/api/collaboration/session`
- **Description:** Create a multi-user collaboration session.

### WebSocket `/api/collaboration/{session_id}`
- **Description:** Real-time sync for code editing and cursors.

---

## Workspace Management

### POST `/api/workspace`
- **Description:** Create a team workspace for RBAC.

### GET `/api/workspace/{workspace_id}`
- **Description:** Retrieve workspace info and members.

### POST `/api/workspace/{workspace_id}/members`
- **Description:** Invite members with specific roles (Admin/Developer/Viewer).

---

## Storage Management

### GET `/api/storage/stats`
- **Description:** Total storage usage and capacity.

### GET `/api/storage/projects`
- **Description:** List all projects stored locally (>1GB support).

### POST `/api/storage/archive/{project_id}`
- **Description:** Move project to long-term compressed storage.

### POST `/api/storage/cleanup`
- **Description:** Run vacuum tasks and clear cache.

---

## Git Integration

### GET `/git/providers`
- **Description:** Status of GitHub, GitLab, and Bitbucket integrations.

### POST/DELETE `/git/config/{provider}`
- **Description:** Manage credentials and tokens securely.

---

## Infrastructure

### POST `/api/kubernetes/generate`
- **Description:** Generate K8s Deployment, Service, and Ingress manifests.

---

**Note:** For detailed request/response schemas, refer to the [Swagger UI](http://localhost:8080/docs).
