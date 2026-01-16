"""
Code Intelligence Service - AI-powered features for browser IDE
Provides completions, hover information, diagnostics, and AI refactoring
"""

import json
import logging
import re
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class IntelligenceService:
    """AI-powered code intelligence service for browser IDE"""
    
    def __init__(self, orchestrator):
        """
        Initialize with orchestrator instance
        
        Args:
            orchestrator: The main AI orchestrator instance
        """
        self.orchestrator = orchestrator
        self.default_model = "qwen2.5-coder:7b"
    
    async def get_completions(
        self,
        code: str,
        language: str,
        cursor_offset: int,
        file_path: str = "main.py"
    ) -> List[Dict[str, Any]]:
        """
        Get AI-powered code completions
        
        Args:
            code: Full file content
            language: Programming language
            cursor_offset: Cursor position in characters
            file_path: Relative path to the file
            
        Returns:
            List of completion items
        """
        # Prepare context by splitting code at cursor
        prefix = code[:cursor_offset]
        suffix = code[cursor_offset:]
        
        prompt = f"""
Provide intelligent code completions for this {language} file: {file_path}

CODE BEFORE CURSOR:
{prefix}

CODE AFTER CURSOR:
{suffix}

As an expert {language} developer, provide 3-5 relevant and high-quality completions that would fit at the cursor position.
For each completion, provide:
1. The exact text to insert
2. A label for the completion (e.g., function name, variable)
3. The type (Method, Property, Variable, Class, Keyword, Snippet)
4. A brief description

Respond ONLY with a JSON array of completion items.
Format: {{"completions": [{{"insertText": "text", "label": "label", "kind": "kind", "detail": "detail"}}]}}
"""
        try:
            result = await self.orchestrator.run_inference(
                prompt=prompt,
                task_type="code_completion",
                model=self.default_model,
                parameters={"temperature": 0.2, "max_tokens": 512}
            )
            
            content = result.get("output", "{}")
            data = self._parse_json_result(content)
            return data.get("completions", [])
            
        except Exception as e:
            logger.error(f"Intelligence completion failed: {e}")
            return []

    async def get_hover_info(
        self,
        code: str,
        language: str,
        symbol: str,
        file_path: str = "main.py"
    ) -> Dict[str, Any]:
        """
        Get information about a symbol on hover
        
        Args:
            code: Full file content
            language: Programming language
            symbol: The symbol being hovered
            file_path: File path
            
        Returns:
            Symbol documentation and details
        """
        prompt = f"""
Explain this symbol in the context of this {language} file: {file_path}

SYMBOL: {symbol}

CODE CONTEXT:
{code}

Provide:
1. Full signature or type definition
2. Descriptive explanation of what it is/does
3. Usage example if applicable

Respond ONLY with a JSON object.
Format: {{"signature": "...", "description": "...", "usage": "..."}}
"""
        try:
            result = await self.orchestrator.run_inference(
                prompt=prompt,
                task_type="code_analysis",
                model=self.default_model
            )
            
            content = result.get("output", "{}")
            return self._parse_json_result(content)
            
        except Exception as e:
            logger.error(f"Intelligence hover failed: {e}")
            return {"error": str(e)}

    async def get_diagnostics(
        self,
        code: str,
        language: str,
        file_path: str = "main.py"
    ) -> List[Dict[str, Any]]:
        """
        Get code diagnostics (errors, warnings, hints)
        
        Args:
            code: Full file content
            language: Programming language
            file_path: File path
            
        Returns:
            List of diagnostic items
        """
        prompt = f"""
Analyze this {language} code for potential errors, warnings, and improvements:

FILE: {file_path}

CODE:
{code}

Find at least 3-5 issues or improvement opportunities.
For each issue, specify:
1. Message describing the issue
2. Severity (Error, Warning, Information, Hint)
3. Line number (1-indexed)
4. Character range (start and end)

Respond ONLY with a JSON array of diagnostics.
Format: {{"diagnostics": [{{"message": "...", "severity": "...", "line": 1, "start": 0, "end": 10}}]}}
"""
        try:
            result = await self.orchestrator.run_inference(
                prompt=prompt,
                task_type="code_review",
                model=self.default_model
            )
            
            content = result.get("output", "{}")
            data = self._parse_json_result(content)
            return data.get("diagnostics", [])
            
        except Exception as e:
            logger.error(f"Intelligence diagnostics failed: {e}")
            return []

    async def ai_refactor(
        self,
        code: str,
        instruction: str,
        language: str,
        range: Optional[Dict[str, int]] = None
    ) -> Dict[str, Any]:
        """
        Perform an AI-powered refactoring on a specific code block
        
        Args:
            code: Original code
            instruction: What to do (e.g., "Extract this logic into a separate function")
            language: Programming language
            range: Optional start and end line/char
            
        Returns:
            Refactored code and summary
        """
        prompt = f"""
As an AI coding assistant, refactor the following {language} code.

USER INSTRUCTION: {instruction}

ORIGINAL CODE:
{code}

{'The refactor should focus on this range: ' + str(range) if range else ''}

Apply the requested changes while maintaining the original functionality where appropriate.
Ensure high code quality, proper naming, and adherence to best practices for {language}.

Respond ONLY with a JSON object.
Format: {{"refactored_code": "...", "changes_summary": "..."}}
"""
        try:
            result = await self.orchestrator.run_inference(
                prompt=prompt,
                task_type="refactor",
                model=self.default_model
            )
            
            content = result.get("output", "{}")
            return self._parse_json_result(content)
            
        except Exception as e:
            logger.error(f"Intelligence refactor failed: {e}")
            return {"error": str(e)}

    def _parse_json_result(self, content: str) -> Dict[str, Any]:
        """Helper to extract and parse JSON from LLM output"""
        try:
            # Try direct parse
            return json.loads(content)
        except json.JSONDecodeError:
            # Try searching for JSON block
            match = re.search(r'```json\n(.*?)\n```', content, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(1))
                except:
                    pass
            
            # Try searching for anything between braces
            match = re.search(r'({.*})', content, re.DOTALL | re.MULTILINE)
            if match:
                try:
                    return json.loads(match.group(0))
                except:
                    pass
            
            return {"error": "Failed to parse JSON result", "raw": content}
