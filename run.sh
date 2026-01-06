#!/bin/bash

# AI Orchestrator Run Script

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "=========================================="
echo "AI Orchestrator Startup"
echo "=========================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${RED}Error: Virtual environment not found${NC}"
    echo "Run setup.sh first: ./setup.sh"
    exit 1
fi

# Activate virtual environment
echo -e "\n${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠ .env file not found, using defaults${NC}"
fi

# Parse command line arguments
HOST="0.0.0.0"
PORT="8080"
RELOAD=false
WORKERS=1

while [[ $# -gt 0 ]]; do
    case $1 in
        --host)
            HOST="$2"
            shift 2
            ;;
        --port)
            PORT="$2"
            shift 2
            ;;
        --reload)
            RELOAD=true
            shift
            ;;
        --workers)
            WORKERS="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--host HOST] [--port PORT] [--reload] [--workers N]"
            exit 1
            ;;
    esac
done

# Pre-flight checks
echo -e "\n${YELLOW}Running pre-flight checks...${NC}"

# Check Python
python3 --version
echo -e "${GREEN}✓ Python${NC}"

# Check config files
if [ -f "config/models.yaml" ]; then
    echo -e "${GREEN}✓ models.yaml${NC}"
else
    echo -e "${RED}✗ models.yaml not found${NC}"
    exit 1
fi

# Check for Ollama
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Ollama is running${NC}"
else
    echo -e "${YELLOW}⚠ Ollama is not running${NC}"
    echo "Start Ollama with: ollama serve"
fi

# Start the orchestrator
echo -e "\n${GREEN}Starting AI Orchestrator...${NC}"
echo "Host: $HOST"
echo "Port: $PORT"
echo "Workers: $WORKERS"
echo "Reload: $RELOAD"
echo ""

if [ "$RELOAD" = true ]; then
    python main.py --host "$HOST" --port "$PORT" --reload --workers "$WORKERS"
else
    python main.py --host "$HOST" --port "$PORT" --workers "$WORKERS"
fi