#!/bin/bash

# AI Orchestrator Setup Script

set -e

echo "=========================================="
echo "AI Orchestrator Setup"
echo "=========================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo -e "\n${YELLOW}Checking Python version...${NC}"
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.11.0"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "Error: Python 3.11 or higher is required. Current version: $python_version"
    exit 1
fi
echo -e "${GREEN}✓ Python $python_version${NC}"

# Create virtual environment
echo -e "\n${YELLOW}Creating virtual environment...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Virtual environment already exists${NC}"
fi

# Activate virtual environment
echo -e "\n${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate

# Upgrade pip
echo -e "\n${YELLOW}Upgrading pip...${NC}"
pip install --upgrade pip

# Install dependencies
echo -e "\n${YELLOW}Installing dependencies...${NC}"
pip install -r requirements.txt
echo -e "${GREEN}✓ Dependencies installed${NC}"

# Create necessary directories
echo -e "\n${YELLOW}Creating directories...${NC}"
mkdir -p models logs cache config

# Copy example config if not exists
if [ ! -f ".env" ]; then
    echo -e "\n${YELLOW}Creating .env file from example...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✓ .env file created${NC}"
    echo -e "${YELLOW}Please edit .env file with your configuration${NC}"
fi

# Check for GPU
echo -e "\n${YELLOW}Checking for GPU...${NC}"
if command -v nvidia-smi &> /dev/null; then
    gpu_count=$(nvidia-smi --list-gpus | wc -l)
    echo -e "${GREEN}✓ Found $gpu_count NVIDIA GPU(s)${NC}"
    nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
else
    echo -e "${YELLOW}⚠ No NVIDIA GPU detected. Running on CPU.${NC}"
fi

# Initialize config files if they don't exist
echo -e "\n${YELLOW}Checking configuration files...${NC}"

config_files=("models.yaml" "runtimes.yaml" "policies.yaml" "hardware.yaml")
for config_file in "${config_files[@]}"; do
    if [ -f "config/$config_file" ]; then
        echo -e "${GREEN}✓ config/$config_file exists${NC}"
    else
        echo -e "${YELLOW}⚠ config/$config_file not found${NC}"
        echo "Please ensure all configuration files are in the config/ directory"
    fi
done

# Check for Ollama
echo -e "\n${YELLOW}Checking for Ollama...${NC}"
if command -v ollama &> /dev/null; then
    echo -e "${GREEN}✓ Ollama is installed${NC}"
    
    # Check if Ollama is running
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Ollama is running${NC}"
    else
        echo -e "${YELLOW}⚠ Ollama is not running. Start it with: ollama serve${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Ollama not found. Install from: https://ollama.ai${NC}"
fi

# Run tests
echo -e "\n${YELLOW}Would you like to run tests? (y/n)${NC}"
read -r run_tests
if [ "$run_tests" = "y" ]; then
    echo -e "\n${YELLOW}Running tests...${NC}"
    pytest tests/ -v
fi

echo -e "\n=========================================="
echo -e "${GREEN}Setup Complete!${NC}"
echo -e "=========================================="
echo ""
echo "To start the orchestrator:"
echo "  1. Activate virtual environment: source venv/bin/activate"
echo "  2. Run the server: python main.py"
echo ""
echo "Or use Docker:"
echo "  docker-compose up -d"
echo ""
echo "API will be available at: http://localhost:8080"
echo "Documentation: http://localhost:8080/docs"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "  1. Edit .env file with your configuration"
echo "  2. Ensure Ollama is running (ollama serve)"
echo "  3. Pull models with Ollama (ollama pull mistral)"
echo "  4. Start the orchestrator"
echo ""