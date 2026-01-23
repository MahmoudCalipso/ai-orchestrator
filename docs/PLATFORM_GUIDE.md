# 📚 AI Orchestrator: Complete Platform Guide

This guide provides comprehensive documentation for all aspects of the AI Orchestrator platform.

## 📋 Table of Contents
1. [Core Architecture](#core-architecture)
2. [API Reference](#api-reference)
3. [Configuration & Environment](#configuration--environment)
4. [AI Models & Agents](#ai-models--agents)
5. [Storage & Git](#storage--git)

---

## 🏗️ Core Architecture
The AI Orchestrator uses a **4-Database Production Stack** for maximum reliability and performance:
- **PostgreSQL 16**: Primary L1 persistence and relational storage (Users, Projects, Metrics).
- **Redis 7**: L0 caching, session management, and real-time pub/sub.
- **MongoDB 7**: Document storage for project metadata, history, and unstructured data.
- **Qdrant**: High-performance vector database for semantic search and neural memory.

---

## 🚀 API Reference
All endpoints require `X-API-Key` authentication.

### Core AI Actions
| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/api/generate` | `POST` | Generate full projects or complex components. |
| `/api/migrate` | `POST` | Perform stack-to-stack migration with logic healing. |
| `/api/fix` | `POST` | Automatically identify and resolve code bugs. |
| `/api/analyze` | `POST` | Deep code audit for security and quality. |
| `/api/test` | `POST` | AI-driven unit and integration test generation. |
| `/api/optimize` | `POST` | Performance tuning and readability optimization. |
| `/api/explain` | `POST` | Natural language explanation of complex code. |

### Infrastructure Tools
| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/api/figma/analyze` | `POST` | Convert Figma designs to clean code tokens. |
| `/api/kubernetes/generate` | `POST` | AI-refined K8s manifests (Deployment/Service/Ingress). |
| `/api/security/scan` | `POST` | SAST/SCA scan with AI-powered remediation. |

---

## ⚙️ Configuration & Environment
The system is configured via `.env`. Key variables:
- `DATABASE_URL`: PostgreSQL connection string.
- `REDIS_URL`: Redis connection string.
- `OLLAMA_MODEL`: Default local model (e.g., `qwen2.5-coder:7b`).
- `EMBEDDING_MODEL`: Semantic search model (e.g., `nomic-embed-text`).

---

## 🤖 AI Models & Agents
The system leverages local **Ollama** models for maximum privacy and zero cost.
- **Universal AI Agent**: The primary interface for all generic code tasks.
- **Lead Architect**: Orchestrates complex swarms for full-project generation and migration.
- **Specialized Workers**: Dedicated logic for Docker, K8s, and Security passes.

---

---

## ⚡ WebSocket Reference
Real-time streams are served under the `/ws` prefix.

| Endpoint | Protocol | Purpose |
| :--- | :--- | :--- |
| `/ws/ide/terminal/{sid}` | `WS` | Real-time shell access. |
| `/ws/monitoring/stream` | `WS` | System metrics live feed. |
| `/ws/collaboration/{sid}` | `WS` | Multi-user sync stream. |

---

## 📂 Storage & Git
- **StorageManager**: Handles projects >1GB with local persistence and MongoDB metadata.
- **GitCredentialManager**: Securely stores tokens for GitHub, GitLab, and Bitbucket.
- **GitSyncService**: Automates pull/push/merge workflows via AI.
