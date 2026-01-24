from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from schemas.spec import TaskType

class CodeTaskRequest(BaseModel):
    """Base schema for simple code tasks"""
    code: str = Field(..., description="The source code to process")
    language: Optional[str] = Field(None, description="Programming language of the code")

class FixCodeRequest(CodeTaskRequest):
    """Request to fix code issues"""
    issue: str = Field(..., description="Description of the bug or issue to resolve")

class AnalyzeCodeRequest(CodeTaskRequest):
    """Request to analyze code"""
    analysis_type: str = Field("comprehensive", description="Type of analysis (security, performance, comprehensive)")

class TestCodeRequest(CodeTaskRequest):
    """Request to generate tests for code"""
    test_framework: Optional[str] = Field(None, description="Preferred test framework")

class OptimizeCodeRequest(CodeTaskRequest):
    """Request to optimize code"""
    optimization_goal: str = Field("performance", description="Goal of optimization (performance, memory, readability)")

class DocumentCodeRequest(CodeTaskRequest):
    """Request to generate documentation"""
    doc_style: str = Field("comprehensive", description="Style of documentation (comprehensive, api, user)")

class ReviewCodeRequest(CodeTaskRequest):
    """Request for code review"""
    pass

class ExplainCodeRequest(CodeTaskRequest):
    """Request to explain code"""
    pass

class RefactorCodeRequest(CodeTaskRequest):
    """Request to refactor code"""
    refactoring_goal: str = Field(..., description="Goal of the refactoring")

class InferenceParametersDTO(BaseModel):
    """Inference parameters DTO"""
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    top_p: float = Field(default=0.9, ge=0.0, le=1.0)
    top_k: int = Field(default=40, ge=0)
    max_tokens: int = Field(default=2048, ge=1)
    stop_sequences: Optional[List[str]] = None
    stream: bool = False

class InferenceRequest(BaseModel):
    """Inference request DTO"""
    prompt: str = Field(..., min_length=1)
    task_type: TaskType = TaskType.CHAT
    model: Optional[str] = None
    parameters: InferenceParametersDTO = Field(default_factory=InferenceParametersDTO)
    context: Optional[Dict[str, Any]] = None
    system_prompt: Optional[str] = None
