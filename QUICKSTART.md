# AI Orchestrator - Quick Start Guide

Get your AI Orchestrator up and running in 5 minutes!

## Prerequisites

- **Python 3.11+** installed
- **Git** for cloning the repository
- **NVIDIA GPU** (optional but recommended)
- **Ollama** installed (optional - for Ollama runtime)

## Step 1: Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd ai-orchestrator

# Make setup script executable
chmod +x setup.sh

# Run setup
./setup.sh
```

This will:
- Create a virtual environment
- Install all dependencies
- Create necessary directories
- Set up configuration files

## Step 2: Configuration

### Basic Setup (Minimal)

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. The default configuration works out of the box with Ollama!

### Advanced Setup (Optional)

Edit configuration files in the `config/` directory:

**config/models.yaml** - Define your models
**config/runtimes.yaml** - Configure runtimes
**config/policies.yaml** - Set routing policies
**config/hardware.yaml** - Hardware specifications

## Step 3: Install and Start Ollama (Recommended)

### Install Ollama

**macOS/Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Or visit:** https://ollama.ai/download

### Start Ollama Server

```bash
ollama serve
```

### Pull Models

In a new terminal:
```bash
# Pull a fast, lightweight model
ollama pull mistral

# Optional: Pull more models
ollama pull phi3
ollama pull deepseek-coder
```

## Step 4: Start the Orchestrator

### Method 1: Using the run script (Recommended)

```bash
chmod +x run.sh
./run.sh
```

### Method 2: Direct Python

```bash
source venv/bin/activate
python main.py
```

### Method 3: Docker

```bash
docker-compose up -d
```

## Step 5: Verify Installation

Open your browser or use curl:

```bash
# Health check
curl http://localhost:8080/health

# List models
curl http://localhost:8080/models \
  -H "X-API-Key: dev-key-12345"
```

You should see JSON responses indicating the system is running!

## Step 6: Make Your First Request

### Using curl:

```bash
curl -X POST http://localhost:8080/inference \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-key-12345" \
  -d '{
    "prompt": "Write a hello world program in Python",
    "task_type": "code_generation"
  }'
```

### Using Python:

```python
import requests

response = requests.post(
    "http://localhost:8080/inference",
    headers={"X-API-Key": "dev-key-12345"},
    json={
        "prompt": "Explain quantum computing in simple terms",
        "task_type": "chat"
    }
)

print(response.json()["output"])
```

### Using JavaScript:

```javascript
fetch('http://localhost:8080/inference', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-API-Key': 'dev-key-12345'
    },
    body: JSON.stringify({
        prompt: 'What is machine learning?',
        task_type: 'chat'
    })
})
.then(r => r.json())
.then(data => console.log(data.output));
```

## Common Task Types

```bash
# Code Generation
{
  "prompt": "Create a REST API in FastAPI",
  "task_type": "code_generation"
}

# Code Review
{
  "prompt": "Review this code: [your code]",
  "task_type": "code_review"
}

# Creative Writing
{
  "prompt": "Write a short story about space",
  "task_type": "creative_writing"
}

# Quick Query
{
  "prompt": "What is the capital of France?",
  "task_type": "quick_query"
}

# Data Analysis
{
  "prompt": "Analyze this dataset: [data]",
  "task_type": "data_analysis"
}
```

## Testing Streaming

```bash
curl -X POST http://localhost:8080/inference/stream \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-key-12345" \
  -d '{
    "prompt": "Count from 1 to 10",
    "task_type": "chat"
  }'
```

## API Documentation

Once running, visit:
- **Swagger UI:** http://localhost:8080/docs
- **ReDoc:** http://localhost:8080/redoc

## Monitoring

### System Status
```bash
curl http://localhost:8080/status \
  -H "X-API-Key: dev-key-12345"
```

### Metrics
```bash
curl http://localhost:8080/metrics \
  -H "X-API-Key: dev-key-12345"
```

## Troubleshooting

### Port Already in Use
```bash
./run.sh --port 8081
```

### Ollama Connection Error
```bash
# Check Ollama is running
curl http://localhost:11434/api/tags

# If not, start it
ollama serve
```

### Model Not Found
```bash
# Pull the model first
ollama pull mistral
```

### GPU Not Detected
- Verify NVIDIA drivers: `nvidia-smi`
- The system will automatically fall back to CPU

### Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

## Next Steps

1. **Explore the API** - Check out all endpoints in the Swagger UI
2. **Add More Models** - Pull additional models with Ollama
3. **Customize Routing** - Edit `config/policies.yaml` for custom routing
4. **Set Up vLLM** - For high-performance inference
5. **Configure Hardware** - Optimize for your GPU setup
6. **Enable Monitoring** - Set up Prometheus/Grafana

## Key Files

```
ai-orchestrator/
├── main.py                 # Start here
├── config/
│   ├── models.yaml        # Model definitions
│   ├── runtimes.yaml      # Runtime config
│   ├── policies.yaml      # Routing policies
│   └── hardware.yaml      # Hardware specs
├── .env                   # Environment variables
├── setup.sh              # Setup script
└── run.sh                # Run script
```

## Quick Commands Cheat Sheet

```bash
# Setup
./setup.sh

# Start server
./run.sh

# Start with reload (development)
./run.sh --reload

# Change port
./run.sh --port 8081

# Health check
curl http://localhost:8080/health

# List models
curl http://localhost:8080/models -H "X-API-Key: dev-key-12345"

# Run inference
curl -X POST http://localhost:8080/inference \
  -H "X-API-Key: dev-key-12345" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello!", "task_type": "chat"}'

# Docker
docker-compose up -d
docker-compose logs -f
docker-compose down
```

## Support

- **Documentation:** Check README.md for detailed information
- **API Reference:** Visit http://localhost:8080/docs after starting
- **Issues:** Open an issue on GitHub
- **Configuration:** All configs in `config/` directory

## Success! 🎉

You now have a fully functional AI orchestration system running locally. Start building amazing AI applications!

### Example Use Cases

1. **Code Assistant** - Generate, review, and debug code
2. **Content Generation** - Create articles, stories, documentation
3. **Data Analysis** - Analyze datasets and generate insights
4. **Chatbot Backend** - Power conversational AI applications
5. **Multi-Model Routing** - Intelligently route requests to best model

Happy orchestrating! 🚀