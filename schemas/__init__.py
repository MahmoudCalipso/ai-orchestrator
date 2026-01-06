"""
Schemas Module
==============

This module defines all data models and schemas used throughout the AI Orchestrator.
All schemas are built using Pydantic for validation and serialization.

Available Schemas:
-----------------

Enums:
------
- TaskType: Available task types for inference
- RuntimeType: Available runtime types
- ModelStatus: Model status enumeration

Request Models:
--------------
- InferenceParameters: Parameters for inference requests
- InferenceRequest: Complete inference request
- MigrationRequest: Task migration request

Response Models:
---------------
- InferenceResponse: Inference result
- HealthResponse: Health check response
- SystemStatus: Detailed system status
- ModelInfo: Model information

Data Models:
-----------
- AuditLog: Audit log entry

Usage:
------
    from schemas import (
        TaskType,
        InferenceRequest,
        InferenceResponse,
        InferenceParameters
    )

    # Create inference request
    request = InferenceRequest(
        prompt="What is AI?",
        task_type=TaskType.CHAT,
        parameters=InferenceParameters(
            temperature=0.7,
            max_tokens=2048
        )
    )

    # Validate data
    print(request.model_dump())

    # Create response
    response = InferenceResponse(
        request_id="req-123",
        model="mistral",
        runtime="ollama",
        output="AI is...",
        tokens_used=150,
        processing_time=2.5
    )

Schema Validation:
-----------------
All schemas include automatic validation:
- Type checking
- Range validation
- Required fields
- Default values
- Custom validators

Example with validation:
    >>> params = InferenceParameters(temperature=2.5)
    ValidationError: temperature must be <= 2.0

    >>> params = InferenceParameters(temperature=0.7)  # Valid
    >>> print(params.temperature)
    0.7
"""

from .spec import (
    # Enums
    TaskType,
    RuntimeType,
    ModelStatus,

    # Request models
    InferenceParameters,
    InferenceRequest,
    MigrationRequest,

    # Response models
    InferenceResponse,
    ModelInfo,
    HealthResponse,
    SystemStatus,

    # Data models
    AuditLog,
)

# Version
__version__ = "1.0.0"

# Public API
__all__ = [
    # Enums
    'TaskType',
    'RuntimeType',
    'ModelStatus',

    # Request models
    'InferenceParameters',
    'InferenceRequest',
    'MigrationRequest',

    # Response models
    'InferenceResponse',
    'ModelInfo',
    'HealthResponse',
    'SystemStatus',

    # Data models
    'AuditLog',
]


# Schema groups for convenience
REQUEST_SCHEMAS = [
    InferenceRequest,
    MigrationRequest,
]

RESPONSE_SCHEMAS = [
    InferenceResponse,
    ModelInfo,
    HealthResponse,
    SystemStatus,
]

ENUM_SCHEMAS = [
    TaskType,
    RuntimeType,
    ModelStatus,
]


# Utility functions for schema operations

def get_task_types() -> list:
    """
    Get all available task types.

    Returns:
        List of task type values

    Example:
        >>> task_types = get_task_types()
        >>> print(task_types)
        ['code_generation', 'code_review', 'reasoning', ...]
    """
    return [task_type.value for task_type in TaskType]


def get_runtime_types() -> list:
    """
    Get all available runtime types.

    Returns:
        List of runtime type values

    Example:
        >>> runtimes = get_runtime_types()
        >>> print(runtimes)
        ['ollama', 'vllm', 'transformers', 'llamacpp']
    """
    return [runtime.value for runtime in RuntimeType]


def get_model_statuses() -> list:
    """
    Get all available model status values.

    Returns:
        List of model status values

    Example:
        >>> statuses = get_model_statuses()
        >>> print(statuses)
        ['available', 'loading', 'loaded', ...]
    """
    return [status.value for status in ModelStatus]


def validate_task_type(task_type: str) -> bool:
    """
    Validate if a task type is valid.

    Args:
        task_type: Task type string to validate

    Returns:
        True if valid, False otherwise

    Example:
        >>> validate_task_type('chat')
        True
        >>> validate_task_type('invalid')
        False
    """
    try:
        TaskType(task_type)
        return True
    except ValueError:
        return False


def validate_runtime_type(runtime_type: str) -> bool:
    """
    Validate if a runtime type is valid.

    Args:
        runtime_type: Runtime type string to validate

    Returns:
        True if valid, False otherwise

    Example:
        >>> validate_runtime_type('ollama')
        True
        >>> validate_runtime_type('invalid')
        False
    """
    try:
        RuntimeType(runtime_type)
        return True
    except ValueError:
        return False


# Schema documentation metadata
SCHEMA_METADATA = {
    'TaskType': {
        'description': 'Enumeration of available task types',
        'values': get_task_types(),
        'usage': 'Specify task type in inference requests'
    },
    'RuntimeType': {
        'description': 'Enumeration of available runtimes',
        'values': get_runtime_types(),
        'usage': 'Specify runtime for model execution'
    },
    'ModelStatus': {
        'description': 'Model availability status',
        'values': get_model_statuses(),
        'usage': 'Track model loading state'
    },
    'InferenceRequest': {
        'description': 'Request schema for inference',
        'required_fields': ['prompt'],
        'optional_fields': ['task_type', 'model', 'parameters', 'context', 'system_prompt']
    },
    'InferenceResponse': {
        'description': 'Response schema for inference',
        'fields': ['request_id', 'model', 'runtime', 'output', 'tokens_used', 'processing_time', 'metadata']
    },
    'InferenceParameters': {
        'description': 'Parameters for controlling inference',
        'fields': ['temperature', 'top_p', 'top_k', 'max_tokens', 'stop_sequences', etc.]
    },
}


def get_schema_info(schema_name: str) -> dict:
    """
    Get metadata about a schema.

    Args:
        schema_name: Name of the schema

    Returns:
        Schema metadata dictionary or None if not found

    Example:
        >>> info = get_schema_info('TaskType')
        >>> print(info['description'])
        'Enumeration of available task types'
        >>> print(info['values'])
        ['code_generation', 'code_review', ...]
    """
    return SCHEMA_METADATA.get(schema_name)


# Default parameter presets
DEFAULT_PARAMETERS = {
    'creative': InferenceParameters(
        temperature=0.8,
        top_p=0.95,
        max_tokens=2048
    ),
    'precise': InferenceParameters(
        temperature=0.2,
        top_p=0.9,
        max_tokens=2048
    ),
    'balanced': InferenceParameters(
        temperature=0.7,
        top_p=0.9,
        max_tokens=2048
    ),
}


def get_default_parameters(preset: str = 'balanced') -> InferenceParameters:
    """
    Get default inference parameters by preset.

    Args:
        preset: Parameter preset name ('creative', 'precise', 'balanced')

    Returns:
        InferenceParameters instance

    Raises:
        ValueError: If preset is not recognized

    Example:
        >>> params = get_default_parameters('creative')
        >>> print(params.temperature)
        0.8
    """
    if preset not in DEFAULT_PARAMETERS:
        available = ', '.join(DEFAULT_PARAMETERS.keys())
        raise ValueError(
            f"Unknown preset '{preset}'. "
            f"Available presets: {available}"
        )

    return DEFAULT_PARAMETERS[preset].model_copy()


# Schema examples for documentation
SCHEMA_EXAMPLES = {
    'InferenceRequest': {
        'simple': {
            'prompt': 'What is artificial intelligence?',
            'task_type': 'chat'
        },
        'detailed': {
            'prompt': 'Write a Python function to calculate fibonacci',
            'task_type': 'code_generation',
            'model': 'deepseek-coder',
            'parameters': {
                'temperature': 0.2,
                'max_tokens': 1024
            }
        },
        'with_context': {
            'prompt': 'Continue the story',
            'task_type': 'creative_writing',
            'context': {
                'conversation_history': [
                    'Once upon a time...',
                    'There was a brave knight.'
                ]
            },
            'parameters': {
                'temperature': 0.8,
                'max_tokens': 500
            }
        }
    },
    'MigrationRequest': {
        'simple': {
            'task_id': 'task-123',
            'target_model': 'qwen2.5'
        },
        'complete': {
            'task_id': 'task-123',
            'target_model': 'qwen2.5',
            'target_runtime': 'vllm',
            'preserve_state': True
        }
    }
}


def get_schema_example(schema_name: str, example_type: str = 'simple') -> dict:
    """
    Get example data for a schema.

    Args:
        schema_name: Name of the schema
        example_type: Type of example ('simple', 'detailed', 'complete')

    Returns:
        Example data dictionary

    Example:
        >>> example = get_schema_example('InferenceRequest', 'detailed')
        >>> request = InferenceRequest(**example)
    """
    if schema_name not in SCHEMA_EXAMPLES:
        return None

    examples = SCHEMA_EXAMPLES[schema_name]
    return examples.get(example_type, examples.get('simple'))


# Export utility functions
__all__.extend([
    'get_task_types',
    'get_runtime_types',
    'get_model_statuses',
    'validate_task_type',
    'validate_runtime_type',
    'get_schema_info',
    'get_default_parameters',
    'get_schema_example',
])