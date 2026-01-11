"""
UNIVERSAL AI CODING AGENT
Language-agnostic AI agent powered by LLM intelligence
Works with ANY programming language, framework, or technology
"""
import logging
from typing import Dict, Any
from agents.base import BaseAgent

logger = logging.getLogger(__name__)

class UniversalAIAgent(BaseAgent):
    """
    Universal AI Coding Agent - Works with ANY language
    
    Capabilities:
    - Code Generation (any language)
    - Code Migration (any stack to any stack)
    - Code Fixing (any issue in any language)
    - Code Analysis (any codebase)
    - Code Testing (any framework)
    - Code Optimization (any language)
    - Code Documentation (any project)
    - Code Review (any codebase)
    
    Uses LLM intelligence - NO hardcoded patterns
    """
    
    def __init__(self, orchestrator=None):
        super().__init__(
            name="UniversalAIAgent",
            role="Universal AI Coding Specialist",
            system_prompt=self._get_universal_system_prompt()
        )
        self.orchestrator = orchestrator
        self.llm = orchestrator.llm if orchestrator else None
    
    def _get_universal_system_prompt(self) -> str:
        return """You are a UNIVERSAL AI CODING AGENT with expert-level knowledge in ALL programming languages, frameworks, and technologies.

Your capabilities are UNLIMITED and LANGUAGE-AGNOSTIC:

1. CODE GENERATION
   - Generate production-ready code in ANY language
   - Use appropriate frameworks and libraries
   - Follow language-specific best practices
   - Include error handling, logging, and tests

2. CODE MIGRATION
   - Migrate code between ANY tech stacks
   - Preserve business logic and functionality
   - Adapt to target language idioms
   - Handle breaking changes gracefully
   - Generate compatibility layers if needed

3. CODE FIXING
   - Fix bugs in ANY language
   - Resolve security vulnerabilities
   - Fix performance issues
   - Correct syntax and logic errors
   - Explain root cause and solution

4. CODE ANALYSIS
   - Analyze code in ANY language
   - Detect security vulnerabilities
   - Identify performance bottlenecks
   - Find code smells and anti-patterns
   - Suggest improvements

5. CODE TESTING
   - Generate tests for ANY language
   - Use appropriate testing frameworks
   - Cover edge cases and error scenarios
   - Aim for high code coverage

6. CODE OPTIMIZATION
   - Optimize code in ANY language
   - Improve time and space complexity
   - Reduce resource usage
   - Maintain readability

7. CODE DOCUMENTATION
   - Generate documentation for ANY project
   - Use appropriate doc formats
   - Include examples and usage
   - Explain complex logic

8. CODE REVIEW
   - Review code in ANY language
   - Provide constructive feedback
   - Suggest best practices
   - Identify potential issues

IMPORTANT PRINCIPLES:
- You are NOT limited to specific languages or frameworks
- You use your LLM intelligence to understand ANY code
- You adapt to the language and context provided
- You always produce high-quality, production-ready output
- You explain your reasoning and decisions
- You are creative and intelligent in solving problems

You have deep knowledge of:
- ALL programming languages (Java, Python, Go, JavaScript, TypeScript, C#, C++, Rust, Kotlin, Swift, Dart, PHP, Ruby, etc.)
- ALL frameworks (Spring, Django, FastAPI, React, Angular, Vue, Flutter, .NET, Rails, Laravel, etc.)
- ALL databases (PostgreSQL, MySQL, MongoDB, Redis, Cassandra, etc.)
- ALL cloud platforms (AWS, Azure, GCP, etc.)
- ALL design patterns and architectures
- ALL best practices and standards
"""
    
    async def act(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Universal entry point for ANY coding task
        Uses LLM intelligence to understand and execute
        """
        context = context or {}
        
        # Build comprehensive prompt
        prompt = self._build_universal_prompt(task, context)
        
        # Use LLM to solve the task
        response = await self.llm.generate(
            prompt=prompt,
            max_tokens=8000,
            temperature=0.3  # Lower temperature for code generation
        )
        
        return {
            "status": "success",
            "task": task,
            "context": context,
            "solution": response,
            "agent": self.name
        }
    
    def _build_universal_prompt(self, task: str, context: Dict[str, Any]) -> str:
        """Build intelligent prompt based on task and context"""
        
        # Extract context information
        code = context.get("code", "")
        language = context.get("language", "auto-detect")
        source_stack = context.get("source_stack", "")
        target_stack = context.get("target_stack", "")
        project_path = context.get("project_path", "")
        requirements = context.get("requirements", "")
        error_message = context.get("error", "")
        
        # Build dynamic prompt
        prompt_parts = [f"Task: {task}\n"]
        
        if code:
            prompt_parts.append(f"\nCode to work with:\n```\n{code}\n```\n")
        
        if language and language != "auto-detect":
            prompt_parts.append(f"\nProgramming Language: {language}\n")
        
        if source_stack and target_stack:
            prompt_parts.append(f"\nMigration: {source_stack} → {target_stack}\n")
        
        if requirements:
            prompt_parts.append(f"\nRequirements:\n{requirements}\n")
        
        if error_message:
            prompt_parts.append(f"\nError Message:\n{error_message}\n")
        
        if project_path:
            prompt_parts.append(f"\nProject Path: {project_path}\n")
        
        # Add instructions
        prompt_parts.append("""
Instructions:
1. Analyze the task and context carefully
2. Use your expert knowledge of the relevant languages/frameworks
3. Provide a complete, production-ready solution
4. Include explanations for your approach
5. Follow best practices for the specific language/framework
6. Consider edge cases and error handling
7. Make the code maintainable and well-documented

Provide your response in this format:

## Analysis
[Your analysis of the task and approach]

## Solution
```[language]
[Your code solution]
```

## Explanation
[Detailed explanation of your solution]

## Best Practices Applied
[List of best practices you followed]

## Additional Recommendations
[Any suggestions for improvement or related considerations]
""")
        
        return "".join(prompt_parts)
    
    async def generate_code(self, requirements: str, language: str = None, framework: str = None) -> Dict[str, Any]:
        """Generate code in ANY language"""
        context = {
            "language": language or "auto-detect",
            "framework": framework or "",
            "requirements": requirements
        }
        
        task = "Generate production-ready code based on the requirements"
        return await self.act(task, context)
    
    async def migrate_code(self, code: str, source_stack: str, target_stack: str) -> Dict[str, Any]:
        """Migrate code from ANY stack to ANY stack"""
        context = {
            "code": code,
            "source_stack": source_stack,
            "target_stack": target_stack
        }
        
        task = f"Migrate this code from {source_stack} to {target_stack}, preserving all functionality"
        return await self.act(task, context)
    
    async def fix_code(self, code: str, issue: str, language: str = None) -> Dict[str, Any]:
        """Fix code issues in ANY language"""
        context = {
            "code": code,
            "language": language or "auto-detect",
            "error": issue
        }
        
        task = f"Fix the following issue in the code: {issue}"
        return await self.act(task, context)
    
    async def analyze_code(self, code: str, language: str = None, analysis_type: str = "comprehensive") -> Dict[str, Any]:
        """Analyze code in ANY language"""
        context = {
            "code": code,
            "language": language or "auto-detect"
        }
        
        task = f"Perform a {analysis_type} analysis of this code, including security, performance, and quality"
        return await self.act(task, context)
    
    async def generate_tests(self, code: str, language: str = None, test_framework: str = None) -> Dict[str, Any]:
        """Generate tests for ANY language"""
        context = {
            "code": code,
            "language": language or "auto-detect",
            "framework": test_framework or "auto-select"
        }
        
        task = "Generate comprehensive unit tests for this code"
        return await self.act(task, context)
    
    async def optimize_code(self, code: str, language: str = None, optimization_goal: str = "performance") -> Dict[str, Any]:
        """Optimize code in ANY language"""
        context = {
            "code": code,
            "language": language or "auto-detect"
        }
        
        task = f"Optimize this code for {optimization_goal}"
        return await self.act(task, context)
    
    async def document_code(self, code: str, language: str = None, doc_style: str = "comprehensive") -> Dict[str, Any]:
        """Generate documentation for ANY language"""
        context = {
            "code": code,
            "language": language or "auto-detect"
        }
        
        task = f"Generate {doc_style} documentation for this code"
        return await self.act(task, context)
    
    async def review_code(self, code: str, language: str = None) -> Dict[str, Any]:
        """Review code in ANY language"""
        context = {
            "code": code,
            "language": language or "auto-detect"
        }
        
        task = "Perform a thorough code review and provide constructive feedback"
        return await self.act(task, context)
    
    async def analyze_project(self, project_path: str) -> Dict[str, Any]:
        """Analyze entire project in ANY language/framework"""
        context = {
            "project_path": project_path
        }
        
        task = "Analyze this entire project, detect tech stack, identify issues, and provide recommendations"
        return await self.act(task, context)
    
    async def migrate_project(self, project_path: str, source_stack: str, target_stack: str) -> Dict[str, Any]:
        """Migrate entire project from ANY stack to ANY stack"""
        context = {
            "project_path": project_path,
            "source_stack": source_stack,
            "target_stack": target_stack
        }
        
        task = f"Migrate this entire project from {source_stack} to {target_stack}"
        return await self.act(task, context)
    
    async def add_feature(self, project_path: str, feature_description: str) -> Dict[str, Any]:
        """Add feature to ANY project"""
        context = {
            "project_path": project_path,
            "requirements": feature_description
        }
        
        task = f"Add the following feature to this project: {feature_description}"
        return await self.act(task, context)
    
    async def refactor_code(self, code: str, refactoring_goal: str, language: str = None) -> Dict[str, Any]:
        """Refactor code in ANY language"""
        context = {
            "code": code,
            "language": language or "auto-detect",
            "requirements": refactoring_goal
        }
        
        task = f"Refactor this code to: {refactoring_goal}"
        return await self.act(task, context)
    
    async def explain_code(self, code: str, language: str = None) -> Dict[str, Any]:
        """Explain code in ANY language"""
        context = {
            "code": code,
            "language": language or "auto-detect"
        }
        
        task = "Explain this code in detail, including what it does and how it works"
        return await self.act(task, context)
