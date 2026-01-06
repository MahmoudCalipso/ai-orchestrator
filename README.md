# AI Orchestrator

A production-ready AI model orchestration system that intelligently routes requests across multiple models and runtimes (Ollama, vLLM, Transformers, llama.cpp).

## Features

- **Intelligent Routing**: Automatically selects the best model and runtime based on task type, complexity, and resource availability
- **Multiple Runtimes**: Support for Ollama, vLLM, HuggingFace Transformers, and llama.cpp
- **Load Balancing**: Built-in load balancing with circuit breakers and rate limiting
- **Fallback Strategies**: Automatic fallback to alternative models/runtimes on failure
- **Resource Management**: Smart GPU/CPU/memory allocation and monitoring
- **Streaming Support**: Real-time streaming inference for all runtimes
- **Security**: API key authentication, rate limiting, and audit logging
- **RESTful API**: Complete REST API with health checks and metrics

## Quick Start

### Prerequisites

- Python 3.11+
- NVIDIA GPU (optional, but recommended)
- Docker and Docker Compose (for containerized deployment)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd ai-orchestrator
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure your models and runtimes:
   - Edit `config/models.yaml` to define available models
   - Edit `config/runtimes.yaml` to configure runtimes
   - Edit `config/policies.yaml` to set routing policies
   - Edit `config/hardware.yaml` to match your hardware

4. Run the orchestrator:
```bash
python main.py
```

The API will be available at `http://localhost:8080`

### Docker Deployment

```bash
docker-compose up -d
```

This starts:
- AI Orchestrator (port 8080)
- Ollama (port 11434)
- Redis (port 6379)
- PostgreSQL (port 5432)

## API Usage

### Run Inference

```bash
curl -X POST http://localhost:8080/inference \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-key-12345" \
  -d '{
    "prompt": "Write a Python function to calculate fibonacci numbers",
    "task_type": "code_generation",
    "parameters": {
      "temperature": 0.2,
      "max_tokens": 1024
    }
  }'
```

### List Available Models

```bash
curl http://localhost:8080/models \
  -H "X-API-Key: dev-key-12345"
```

### Health Check

```bash
curl http://localhost:8080/health
```

### System Status

```bash
curl http://localhost:8080/status \
  -H "X-API-Key: dev-key-12345"
```

### Streaming Inference

```bash
curl -X POST http://localhost:8080/inference/stream \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-key-12345" \
  -d '{
    "prompt": "Tell me a story",
    "task_type": "creative_writing"
  }'
```

## Configuration

### Models (config/models.yaml)

Define available models with their specifications:

```yaml
models:
  mistral:
    family: mistral
    size: 7b
    context_length: 32768
    capabilities: [general, fast]
    memory_requirement: 6gb
    recommended_runtime: [ollama, llamacpp]
```

### Runtimes (config/runtimes.yaml)

Configure runtime servers:

```yaml
runtimes:
  ollama:
    host: localhost
    port: 11434
    timeout: 300
```

### Policies (config/policies.yaml)

Set routing and resource policies:

```yaml
policies:
  routing:
    by_task_type:
      code_generation:
        models: [deepseek-coder, codellama]
        temperature: 0.2
```

### Hardware (config/hardware.yaml)

Define your hardware configuration:

```yaml
hardware:
  gpus:
    - id: gpu_0
      type: nvidia
      model: RTX_4090
      memory: 24gb
```

## Architecture

```
┌─────────────────────────────────────────┐
│           FastAPI REST API              │
├─────────────────────────────────────────┤
│           Orchestrator Core             │
│  ┌──────────┬─────────┬──────────────┐  │
│  │  Router  │ Planner │   Registry   │  │
│  └──────────┴─────────┴──────────────┘  │
├─────────────────────────────────────────┤
│            Runtime Layer                │
│  ┌────────┬──────┬────────┬──────────┐  │
│  │ Ollama │ vLLM │ Trans. │ LlamaCpp │  │
│  └────────┴──────┴────────┴──────────┘  │
├─────────────────────────────────────────┤
│         Infrastructure Layer            │
│  ┌────────┬────────┬──────────────────┐ │
│  │ Memory │Security│    Monitoring    │ │
│  └────────┴────────┴──────────────────┘ │
└─────────────────────────────────────────┘
```

## Task Types

The orchestrator supports various task types with automatic model selection:

- `code_generation`: Generate code snippets and applications
- `code_review`: Review and analyze code
- `reasoning`: Complex reasoning and problem-solving
- `quick_query`: Fast responses for simple questions
- `creative_writing`: Stories, articles, creative content
- `data_analysis`: Analyze and interpret data
- `documentation`: Generate documentation
- `chat`: General conversation

## Advanced Features

### Custom Model Routes

```python
from core.orchestrator import Orchestrator

orchestrator = Orchestrator()
await orchestrator.initialize()

# Run with specific model
result = await orchestrator.run_inference(
    prompt="Your prompt here",
    model="deepseek-coder",
    task_type="code_generation"
)
```

### Task Migration

Migrate running tasks between models/runtimes:

```bash
curl -X POST http://localhost:8080/migrate \
  -H "X-API-Key: dev-key-12345" \
  -d '{
    "task_id": "task-123",
    "target_model": "qwen2.5",
    "target_runtime": "vllm"
  }'
```

### Load/Unload Models

```bash
# Load a model
curl -X POST http://localhost:8080/models/mistral/load \
  -H "X-API-Key: dev-key-12345"

# Unload a model
curl -X POST http://localhost:8080/models/mistral/unload \
  -H "X-API-Key: dev-key-12345"
```

## Monitoring

### Metrics Endpoint

```bash
curl http://localhost:8080/metrics \
  -H "X-API-Key: dev-key-12345"
```

Returns:
- Total requests
- Success/failure rates
- Average processing time
- Token usage
- Resource utilization

## Security

- API key authentication
- Rate limiting per user
- Audit logging
- Input validation
- Output sanitization

## Development

### Running Tests

```bash
pytest
```

### Code Structure

```
ai-orchestrator/
├── main.py                 # Application entry point
├── config/                 # Configuration files
├── core/                   # Core orchestration logic
│   ├── orchestrator.py
│   ├── router.py
│   ├── planner.py
│   ├── registry.py
│   ├── memory.py
│   └── security.py
├── runtimes/              # Runtime implementations
│   ├── base.py
│   ├── ollama.py
│   ├── vllm.py
│   ├── transformers.py
│   └── llamacpp.py
├── agents/                # Agent utilities
├── schemas/               # Data schemas
└── requirements.txt       # Dependencies
```

## Troubleshooting

### Ollama not connecting
- Ensure Ollama is running: `ollama serve`
- Check configuration in `config/runtimes.yaml`

### GPU out of memory
- Reduce batch size in runtime config
- Use smaller models or quantized versions
- Adjust `gpu_memory_fraction` in config

### Slow inference
- Enable vLLM for high-throughput workloads
- Use quantized models (Q4, Q5)
- Check hardware profile matches your GPU

## License

MIT License

## Contributing

Contributions welcome! Please submit pull requests or open issues.

## Support

For questions and support, please open an issue on GitHub.