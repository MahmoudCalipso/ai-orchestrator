# AI Orchestrator - Universal AI Coding Platform

## 🎯 What is This?

A **Universal AI Orchestrator** with a powerful AI agent that can:
- Generate code in **ANY programming language**
- Migrate code between **ANY tech stacks**
- Fix bugs in **ANY codebase**
- Analyze and optimize **ANY project**
- Works with Java, Python, Go, JavaScript, C#, Rust, Kotlin, Swift, Dart, PHP, Ruby, and more!

**Key Feature:** Language-agnostic AI agent powered by LLM intelligence (no hardcoded patterns).

---

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Docker Desktop
- OpenAI API Key (or other LLM provider)

### Setup (One-Time)
```powershell
# Run setup script
.\setup.ps1
```

### Start the AI Orchestrator
```powershell
# Set your OpenAI API key
$env:OPENAI_API_KEY='your-api-key-here'

# Start the server
.\start.ps1
```

### Access the API
- **API Server:** http://localhost:8080
- **API Documentation:** http://localhost:8080/docs
- **Health Check:** http://localhost:8080/health

---

## 💡 Usage Examples

### Example 1: Generate Code
```python
POST /api/generate
{
  "language": "rust",
  "requirements": "Create a web server with JWT authentication"
}
```

### Example 2: Migrate Code
```python
POST /api/migrate
{
  "source_code": "<Java code>",
  "source_stack": "Java 8 Spring Boot",
  "target_stack": "Go 1.22 Gin"
}
```

### Example 3: Fix Code
```python
POST /api/fix
{
  "code": "<buggy code>",
  "issue": "Memory leak in loop",
  "language": "python"
}
```

### Example 4: Analyze Project
```python
POST /api/analyze
{
  "project_path": "/path/to/project"
}
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│         Universal AI Agent                   │
│  (Works with ANY language)                   │
│  - Code Generation                           │
│  - Code Migration                            │
│  - Code Fixing                               │
│  - Code Analysis                             │
│  - Code Testing                              │
│  - Code Optimization                         │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│         LLM Inference Engine                 │
│  - OpenAI (GPT-4)                           │
│  - Anthropic (Claude)                        │
│  - Ollama (Local)                            │
│  - Azure OpenAI                              │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│         Infrastructure                       │
│  - Docker Workbenches                        │
│  - MCP Integration                           │
│  - WebSocket Console                         │
│  - Universal Build System                    │
└─────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
d:\Projects\IA-ORCH\
├── agents/                      # AI Agents
│   ├── universal_ai_agent.py   # ⭐ Main AI Agent
│   ├── advanced_code_analyzer.py
│   ├── project_scanner.py
│   └── lead_architect.py
│
├── core/                        # Core Infrastructure
│   ├── orchestrator.py         # Main orchestrator
│   ├── llm/
│   │   └── inference.py        # LLM engine
│   ├── workbench/
│   │   ├── manager.py          # Docker management
│   │   └── blueprint.py        # Tech stack definitions
│   ├── mcp/                    # MCP integration
│   ├── state/                  # Shared state
│   ├── console/                # WebSocket console
│   └── buildtools/             # Build system
│
├── runtimes/                    # Runtime engines
├── config/                      # Configuration
├── main.py                      # FastAPI server
├── requirements.txt             # Dependencies
├── docker-compose.yml           # Docker services
├── setup.ps1                    # Setup script
└── start.ps1                    # Start script
```

---

## 🔧 Configuration

### Environment Variables
```powershell
# LLM Provider (openai, anthropic, ollama, azure)
$env:LLM_PROVIDER='openai'

# LLM Model
$env:LLM_MODEL='gpt-4-turbo-preview'

# OpenAI API Key
$env:OPENAI_API_KEY='your-api-key-here'

# Anthropic API Key (if using Claude)
$env:ANTHROPIC_API_KEY='your-api-key-here'
```

### Docker Services
The orchestrator uses Docker Compose for:
- **Redis** - State management
- **PostgreSQL** - Data persistence
- **Prometheus** - Metrics
- **Grafana** - Monitoring

---

## 🎓 Capabilities

### Supported Languages
Java, Python, Go, JavaScript, TypeScript, C#, C++, Rust, Kotlin, Swift, Dart, PHP, Ruby, Scala, Haskell, and more!

### Supported Frameworks
Spring Boot, Django, FastAPI, React, Angular, Vue, Flutter, .NET, Rails, Laravel, Express, Gin, Echo, and more!

### Supported Operations
- **Code Generation** - Create new code from requirements
- **Code Migration** - Migrate between any tech stacks
- **Code Fixing** - Fix bugs, security issues, performance problems
- **Code Analysis** - Deep code analysis and recommendations
- **Code Testing** - Generate comprehensive test suites
- **Code Optimization** - Improve performance and efficiency
- **Code Documentation** - Auto-generate documentation
- **Code Review** - Expert code review with feedback

---

## 📚 Documentation

- **QUICKSTART.md** - Quick start guide
- **SOLUTION_AUDIT.md** - Complete system audit
- **TROUBLESHOOTING.md** - Common issues and solutions
- **implementation_plan.md** - PaaS platform architecture

---

## 🤝 API Endpoints

### Core Endpoints
- `POST /api/generate` - Generate code
- `POST /api/migrate` - Migrate code
- `POST /api/fix` - Fix code issues
- `POST /api/analyze` - Analyze code
- `POST /api/test` - Generate tests
- `POST /api/optimize` - Optimize code
- `POST /api/document` - Generate documentation
- `POST /api/review` - Code review

### Infrastructure Endpoints
- `POST /workbench/create` - Create Docker workbench
- `GET /workbench/list` - List workbenches
- `WS /console/{workbench_id}` - WebSocket terminal
- `GET /health` - Health check
- `GET /status` - System status
- `GET /metrics` - Prometheus metrics

---

## 🎯 Use Cases

### 1. Code Modernization
Migrate legacy applications to modern tech stacks:
- Java 8 → Java 21
- AngularJS → Angular 18
- Android → Flutter
- Python 2 → Python 3

### 2. Multi-Language Projects
Work with polyglot codebases:
- Backend: Java Spring Boot
- Frontend: React TypeScript
- Mobile: Flutter
- Scripts: Python

### 3. Code Quality
Improve code quality across all languages:
- Security scanning
- Performance optimization
- Best practices enforcement
- Automated testing

### 4. Developer Productivity
Accelerate development:
- Auto-generate boilerplate
- Fix bugs automatically
- Generate documentation
- Code review assistance

---

## 🏆 Key Features

✅ **Universal** - Works with ANY programming language
✅ **Intelligent** - Uses LLM reasoning, not hardcoded patterns
✅ **Powerful** - Handles complex migrations and transformations
✅ **Fast** - Parallel processing with Docker workbenches
✅ **Secure** - Isolated containers, credential encryption
✅ **Scalable** - Kubernetes-ready architecture
✅ **Extensible** - Plugin system via MCP

---

## 🚀 What's Next?

The AI Orchestrator is the foundation for a **Commercial PaaS Platform**:
- Git repository integration
- Automated project analysis
- Demo deployments
- Payment processing
- Client portal

See `implementation_plan.md` for the complete roadmap.

---

## 📝 License

Proprietary - All rights reserved

---

**Built with ❤️ using Universal AI**