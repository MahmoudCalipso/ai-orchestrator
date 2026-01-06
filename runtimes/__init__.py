"""
Runtimes Module
===============

This module provides runtime implementations for different AI inference engines.

Available Runtimes:
------------------
- OllamaRuntime: Integration with Ollama for local model inference
- VLLMRuntime: High-performance inference with vLLM
- TransformersRuntime: Direct HuggingFace Transformers integration
- LlamaCppRuntime: llama.cpp for GGUF quantized models

Usage:
------
    from runtimes import OllamaRuntime, VLLMRuntime

    # Initialize a runtime
    runtime = OllamaRuntime(config_path="config")
    await runtime.initialize()

    # Load a model
    await runtime.load_model("mistral")

    # Generate text
    result = await runtime.generate(
        model="mistral",
        prompt="Hello, world!",
        temperature=0.7
    )

    # Cleanup
    await runtime.shutdown()

Runtime Selection:
-----------------
Choose runtime based on your needs:
- Ollama: Easy setup, good for development, supports many models
- vLLM: Best for production, high throughput, continuous batching
- Transformers: Most flexible, supports fine-tuning and adapters
- LlamaCpp: Best for CPU inference, efficient with quantized models
"""

from .base import BaseRuntime
from .ollama import OllamaRuntime
from .vllm import VLLMRuntime
from .transformers import TransformersRuntime
from .llamacpp import LlamaCppRuntime

# Version
__version__ = "1.0.0"

# Public API
__all__ = [
    'BaseRuntime',
    'OllamaRuntime',
    'VLLMRuntime',
    'TransformersRuntime',
    'LlamaCppRuntime',
]

# Runtime registry for dynamic loading
RUNTIME_REGISTRY = {
    'ollama': OllamaRuntime,
    'vllm': VLLMRuntime,
    'transformers': TransformersRuntime,
    'llamacpp': LlamaCppRuntime,
}


def get_runtime(runtime_name: str, config_path: str = "config") -> BaseRuntime:
    """
    Factory function to get a runtime instance by name.

    Args:
        runtime_name: Name of the runtime ('ollama', 'vllm', 'transformers', 'llamacpp')
        config_path: Path to configuration directory

    Returns:
        Runtime instance

    Raises:
        ValueError: If runtime name is not recognized

    Example:
        >>> runtime = get_runtime('ollama', 'config')
        >>> await runtime.initialize()
    """
    if runtime_name not in RUNTIME_REGISTRY:
        available = ', '.join(RUNTIME_REGISTRY.keys())
        raise ValueError(
            f"Unknown runtime '{runtime_name}'. "
            f"Available runtimes: {available}"
        )

    runtime_class = RUNTIME_REGISTRY[runtime_name]
    return runtime_class(config_path)


def list_available_runtimes() -> list:
    """
    List all available runtime names.

    Returns:
        List of runtime names

    Example:
        >>> runtimes = list_available_runtimes()
        >>> print(runtimes)
        ['ollama', 'vllm', 'transformers', 'llamacpp']
    """
    return list(RUNTIME_REGISTRY.keys())


# Convenience imports for common operations
from typing import Dict, Any, Optional


async def quick_generate(
    runtime_name: str,
    model: str,
    prompt: str,
    config_path: str = "config",
    **kwargs
) -> Dict[str, Any]:
    """
    Quick generation without managing runtime lifecycle.

    Args:
        runtime_name: Runtime to use
        model: Model name
        prompt: Input prompt
        config_path: Configuration path
        **kwargs: Additional generation parameters

    Returns:
        Generation result dictionary

    Example:
        >>> result = await quick_generate(
        ...     'ollama',
        ...     'mistral',
        ...     'Hello, world!'
        ... )
        >>> print(result['output'])
    """
    runtime = get_runtime(runtime_name, config_path)

    try:
        await runtime.initialize()

        if not await runtime.is_model_loaded(model):
            await runtime.load_model(model)

        result = await runtime.generate(model=model, prompt=prompt, **kwargs)
        return result

    finally:
        await runtime.shutdown()


# Runtime metadata
RUNTIME_METADATA = {
    'ollama': {
        'name': 'Ollama',
        'description': 'Local model inference with Ollama',
        'features': ['streaming', 'batching', 'quantization'],
        'best_for': ['development', 'local_inference', 'quick_setup'],
        'requires': ['ollama_server'],
    },
    'vllm': {
        'name': 'vLLM',
        'description': 'High-performance inference server',
        'features': ['streaming', 'continuous_batching', 'paged_attention'],
        'best_for': ['production', 'high_throughput', 'multi_gpu'],
        'requires': ['vllm_server', 'gpu'],
    },
    'transformers': {
        'name': 'HuggingFace Transformers',
        'description': 'Direct transformers library integration',
        'features': ['streaming', 'fine_tuning', 'adapters'],
        'best_for': ['flexibility', 'research', 'custom_models'],
        'requires': ['transformers', 'torch'],
    },
    'llamacpp': {
        'name': 'llama.cpp',
        'description': 'Efficient CPU/GPU inference',
        'features': ['streaming', 'quantization', 'mmap'],
        'best_for': ['cpu_inference', 'edge_devices', 'gguf_models'],
        'requires': ['llama_cpp_python'],
    },
}


def get_runtime_info(runtime_name: str) -> Optional[Dict[str, Any]]:
    """
    Get metadata about a runtime.

    Args:
        runtime_name: Name of the runtime

    Returns:
        Runtime metadata dictionary or None if not found

    Example:
        >>> info = get_runtime_info('ollama')
        >>> print(info['description'])
        'Local model inference with Ollama'
    """
    return RUNTIME_METADATA.get(runtime_name)