#!/bin/bash
# =============================================================================
# IA-ORCHESTRATOR 2026 - AUTOMATIC MODEL DOWNLOADER
# Downloads AI models based on tier selection
# =============================================================================

set -e

echo "🤖 IA-Orchestrator 2026 - Model Downloader"
echo "=========================================="
echo ""

# Configuration
OLLAMA_HOST="${OLLAMA_HOST:-http://ollama:11434}"
MODEL_TIER="${MODEL_TIER:-balanced}"

# Wait for Ollama to be ready
echo "⏳ Waiting for Ollama service..."
max_attempts=30
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if ollama list > /dev/null 2>&1; then
        echo "✓ Ollama is ready!"
        break
    fi
    attempt=$((attempt + 1))
    echo "  Attempt $attempt/$max_attempts..."
    sleep 2
done

if [ $attempt -eq $max_attempts ]; then
    echo "✗ Ollama service not available after $max_attempts attempts"
    exit 1
fi

echo ""

# Define model tiers
declare -A MODELS

# Minimal tier (16GB RAM) - Fast, efficient
MODELS[minimal]="qwen2.5-coder:7b glm4:9b"

# Balanced tier (32GB RAM) - Recommended
MODELS[balanced]="qwen2.5-coder:14b qwen2.5-coder:7b glm4:9b codellama:13b"

# Full Power tier (64GB+ RAM) - Best quality
MODELS[full]="qwen2.5-coder:32b deepseek-r1:32b-q4 qwen2.5-coder:14b glm4:9b"

# Ultra tier (128GB+ RAM) - Maximum performance
MODELS[ultra]="qwen3:235b-q4 deepseek-r1:70b-q4 qwen2.5-coder:32b glm4:9b"

# Select models based on tier
if [ -n "${MODELS[$MODEL_TIER]}" ]; then
    SELECTED_MODELS="${MODELS[$MODEL_TIER]}"
else
    echo "⚠️  Unknown tier '$MODEL_TIER', using 'balanced'"
    SELECTED_MODELS="${MODELS[balanced]}"
fi

echo "📦 Downloading models for tier: $MODEL_TIER"
echo "Models: $SELECTED_MODELS"
echo ""

# Download models
downloaded=0
failed=0
total=$(echo $SELECTED_MODELS | wc -w)
current=0

for model in $SELECTED_MODELS; do
    current=$((current + 1))
    echo "------------------------------------------"
    echo "[$current/$total] 📥 STARTING: $model"
    echo "------------------------------------------"
    
    # Use ollama pull. The TTY=true in compose should help with the progress bar.
    if ollama pull "$model"; then
        echo ""
        echo "✅ SUCCESS: $model downloaded and verified"
        downloaded=$((downloaded + 1))
    else
        echo ""
        echo "❌ FAILURE: Failed to download $model"
        failed=$((failed + 1))
    fi
    echo ""
done

# Summary
echo "=========================================="
echo "Download Summary:"
echo "  ✓ Downloaded: $downloaded"
echo "  ✗ Failed: $failed"
echo "=========================================="
echo ""

if [ $downloaded -gt 0 ]; then
    echo "✅ Models ready to use!"
    echo ""
    echo "Available models:"
    ollama list
else
    echo "⚠️  No models were downloaded successfully"
    exit 1
fi

echo ""
echo "🚀 IA-Orchestrator is ready!"
