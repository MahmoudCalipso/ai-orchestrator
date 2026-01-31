from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from dto.v1.schemas.enums import TaskType

class CodeTaskRequest(BaseModel):
    """Refined base schema for code-centric AI operations"""
    code: str = Field(..., min_length=1, description="Source code snippet or file content to process", example="def hello():\n    print('world')")
    language: Optional[str] = Field(None, description="Programming language for context-aware processing", example="python")

class FixCodeRequest(CodeTaskRequest):
    """Request to automatically identify and resolve code issues"""
    issue: str = Field(..., description="Description of the bug, error, or logic flaw to fix", example="The function return type is incorrect")

class AnalyzeCodeRequest(CodeTaskRequest):
    """Request for deep structural or security analysis of code"""
    analysis_type: str = Field("comprehensive", description="Level of analysis depth", example="security")

class TestCodeRequest(CodeTaskRequest):
    """Request to generate automated test suites for provided code"""
    test_framework: Optional[str] = Field(None, description="Preferred unit test framework", example="pytest")

class OptimizeCodeRequest(CodeTaskRequest):
    """Request to enhance code performance or readability"""
    optimization_goal: str = Field("performance", description="Primary goal of the optimization", example="memory_usage")

class DocumentCodeRequest(CodeTaskRequest):
    """Request to generate high-quality code documentation"""
    doc_style: str = Field("comprehensive", description="Target documentation format", example="numpy")

class ReviewCodeRequest(CodeTaskRequest):
    """Request for code review"""
    pass

class ExplainCodeRequest(CodeTaskRequest):
    """Request to explain code"""
    pass

class RefactorCodeRequest(CodeTaskRequest):
    """Request for architectural or logic improvements"""
    refactoring_goal: str = Field(..., description="Strategic objective of the refactoring", example="Convert to asynchronous implementation")

class InferenceParametersDTO(BaseModel):
    """Advanced generation parameters for fine-tuning AI output"""
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Sampling temperature")
    top_p: float = Field(default=0.9, ge=0.0, le=1.0, description="Nucleus sampling probability")
    top_k: int = Field(default=40, ge=0, description="Top-K sampling constraint")
    max_tokens: int = Field(default=2048, ge=1, description="Maximum output token count")
    stop_sequences: Optional[List[str]] = Field(None, description="Sequences to cease generation")
    stream: bool = Field(False, description="Enable server-sent events for streaming output")

class InferenceRequest(BaseModel):
    """High-level request for AI model inference"""
    prompt: str = Field(..., min_length=1, description="Target input prompt for the model", example="Explain the concept of monads in functional programming")
    task_type: TaskType = Field(TaskType.CHAT, description="Specific category of AI task")
    model: Optional[str] = Field(None, description="Explicit model name to override defaults", example="mistral-7b")
    parameters: InferenceParametersDTO = Field(default_factory=InferenceParametersDTO, description="Generation overrides")
    context: Optional[Dict[str, Any]] = Field(None, description="Optional conversational or system context")
    system_prompt: Optional[str] = Field(None, description="Override default system instructions")
