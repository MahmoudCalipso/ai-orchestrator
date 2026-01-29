#!/usr/bin/env python3
"""
Ollama Model Downloader
Downloads open-source AI models based on hardware tier.
"""
import subprocess
import sys
import argparse
import logging
from typing import List, Dict

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Tiered Model Configuration
TIERS: Dict[str, List[str]] = {
    "minimal": [
        "qwen2.5-coder:7b",
        "glm4:9b",
        "phi3:3.8b",
    ],
    "balanced": [
        "qwen2.5-coder:14b",
        "qwen2.5-coder:7b",
        "glm4:9b",
        "codellama:13b",
        "mistral:7b",
        "phi3:14b",
    ],
    "full": [
        "qwen2.5-coder:32b",
        "deepseek-r1:32b-q4",
        "qwen2.5-coder:14b",
        "glm4:9b",
        "codellama:34b",
        "mixtral:8x7b",
        "starcoder2:15b",
    ],
    "ultra": [
        "qwen3:235b-q4",
        "deepseek-r1:70b-q4",
        "qwen2.5-coder:32b",
        "glm4:9b",
        "llama3.1:70b",
        "mixtral:8x22b",
        "deepseek-coder:33b",
    ]
}

def check_ollama_installed() -> bool:
    """Check if Ollama is installed."""
    try:
        result = subprocess.run(
            ["ollama", "--version"],
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode == 0:
            logger.info(f"Ollama is installed: {result.stdout.strip()}")
            return True
        return False
    except FileNotFoundError:
        return False

def install_ollama():
    """Provide instructions to install Ollama."""
    logger.error("Ollama is not installed!")
    logger.info("Please install Ollama:")
    logger.info("  Windows: https://ollama.ai/download/windows")
    logger.info("  macOS: brew install ollama")
    logger.info("  Linux: curl -fsSL https://ollama.ai/install.sh | sh")
    sys.exit(1)

def pull_model(model: str) -> bool:
    """Pull a single model using Ollama."""
    try:
        logger.info(f"Pulling model: {model}")
        result = subprocess.run(
            ["ollama", "pull", model],
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            logger.info(f"✓ Successfully pulled: {model}")
            return True
        else:
            logger.error(f"✗ Failed to pull {model}: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"✗ Error pulling {model}: {e}")
        return False

def list_installed_models() -> List[str]:
    """List currently installed Ollama models."""
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Parse output (skip header)
        lines = result.stdout.strip().split('\n')[1:]
        models = [line.split()[0] for line in lines if line.strip()]
        return models
        
    except Exception as e:
        logger.error(f"Failed to list models: {e}")
        return []

def download_tier(tier: str, skip_existing: bool = True):
    """Download all models for a specific tier."""
    if tier not in TIERS:
        logger.error(f"Invalid tier: {tier}. Choose from: {list(TIERS.keys())}")
        sys.exit(1)
    
    models = TIERS[tier]
    logger.info(f"Downloading {tier} tier ({len(models)} models)")
    logger.info(f"Models: {', '.join(models)}")
    
    # Get installed models if skipping
    installed = []
    if skip_existing:
        installed = list_installed_models()
        logger.info(f"Already installed: {len(installed)} models")
    
    # Download each model
    success_count = 0
    for i, model in enumerate(models, 1):
        logger.info(f"\n[{i}/{len(models)}] Processing: {model}")
        
        if skip_existing and model in installed:
            logger.info(f"⊙ Skipping {model} (already installed)")
            success_count += 1
            continue
        
        if pull_model(model):
            success_count += 1
    
    # Summary
    logger.info(f"\n{'='*60}")
    logger.info(f"Download Summary for '{tier}' tier:")
    logger.info(f"  Total models: {len(models)}")
    logger.info(f"  Successfully downloaded: {success_count}")
    logger.info(f"  Failed: {len(models) - success_count}")
    logger.info(f"{'='*60}")

def main():
    parser = argparse.ArgumentParser(
        description="Download Ollama models by hardware tier"
    )
    parser.add_argument(
        "tier",
        choices=list(TIERS.keys()),
        help="Hardware tier (minimal=16GB, balanced=32GB, full=64GB+, ultra=128GB+)"
    )
    parser.add_argument(
        "--no-skip",
        action="store_true",
        help="Re-download models even if already installed"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List currently installed models and exit"
    )
    
    args = parser.parse_args()
    
    # Check Ollama installation
    if not check_ollama_installed():
        install_ollama()
    
    # List models if requested
    if args.list:
        installed = list_installed_models()
        logger.info(f"Installed models ({len(installed)}):")
        for model in installed:
            logger.info(f"  - {model}")
        sys.exit(0)
    
    # Download tier
    download_tier(args.tier, skip_existing=not args.no_skip)

if __name__ == "__main__":
    main()
