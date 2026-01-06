#!/bin/bash

# Script to install recommended Ollama models for AI Orchestrator

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "========================================"
echo "AI Orchestrator - Model Installation"
echo "========================================"

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo -e "${RED}Error: Ollama is not installed${NC}"
    echo "Please install Ollama from: https://ollama.ai"
    exit 1
fi

echo -e "${GREEN}✓ Ollama is installed${NC}"

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠ Ollama is not running${NC}"
    echo "Starting Ollama..."
    ollama serve &
    OLLAMA_PID=$!
    sleep 3
fi

echo -e "${GREEN}✓ Ollama is running${NC}"

# Define models to install
declare -A MODELS=(
    ["mistral"]="Fast, lightweight model for general tasks"
    ["phi3"]="Efficient model for resource-constrained environments"
    ["deepseek-coder"]="Specialized for code generation and review"
    ["llama3.1"]="General purpose, strong reasoning"
    ["qwen2.5"]="Excellent for complex reasoning and math"
)

echo ""
echo "Available models to install:"
echo ""
for model in "${!MODELS[@]}"; do
    echo "  - $model: ${MODELS[$model]}"
done
echo ""

# Ask user which models to install
echo "Which models would you like to install?"
echo "1) Essential only (mistral, phi3)"
echo "2) Essential + Code (mistral, phi3, deepseek-coder)"
echo "3) All models"
echo "4) Custom selection"
echo "5) Skip installation"
echo ""
read -p "Enter your choice (1-5): " choice

MODELS_TO_INSTALL=()

case $choice in
    1)
        MODELS_TO_INSTALL=("mistral" "phi3")
        ;;
    2)
        MODELS_TO_INSTALL=("mistral" "phi3" "deepseek-coder")
        ;;
    3)
        MODELS_TO_INSTALL=("${!MODELS[@]}")
        ;;
    4)
        echo ""
        for model in "${!MODELS[@]}"; do
            read -p "Install $model? (y/n): " install
            if [[ $install == "y" || $install == "Y" ]]; then
                MODELS_TO_INSTALL+=("$model")
            fi
        done
        ;;
    5)
        echo "Skipping model installation"
        exit 0
        ;;
    *)
        echo "Invalid choice, installing essential models only"
        MODELS_TO_INSTALL=("mistral" "phi3")
        ;;
esac

# Install selected models
echo ""
echo "Installing ${#MODELS_TO_INSTALL[@]} model(s)..."
echo ""

for model in "${MODELS_TO_INSTALL[@]}"; do
    echo -e "${YELLOW}Installing $model...${NC}"
    echo "Description: ${MODELS[$model]}"
    
    if ollama pull "$model"; then
        echo -e "${GREEN}✓ $model installed successfully${NC}"
    else
        echo -e "${RED}✗ Failed to install $model${NC}"
    fi
    echo ""
done

# List installed models
echo ""
echo "Installed models:"
ollama list

echo ""
echo -e "${GREEN}Model installation complete!${NC}"
echo ""
echo "You can now start the orchestrator with:"
echo "  ./run.sh"
echo ""
echo "Or test a model directly with:"
echo "  ollama run mistral"
echo ""