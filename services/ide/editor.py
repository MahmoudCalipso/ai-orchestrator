"""
Browser-Based IDE - Editor Service
Provides file operations, LSP integration, and code intelligence
Unified interface for the browser IDE
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

from services.ide.filesystem_service import FileSystemService
from services.ide.intelligence_service import IntelligenceService

logger = logging.getLogger(__name__)


class EditorService:
    """
    Browser-based code editor service
    Coordinates file system and AI intelligence operations
    """
    
    def __init__(self, orchestrator=None, workspace_root: str = "storage/workspaces"):
        self.fs = FileSystemService(base_path=workspace_root)
        self.intelligence = IntelligenceService(orchestrator) if orchestrator else None
        self.workspace_root = Path(workspace_root)
    
    # --- File Operations (Delegated to FileSystemService) ---
    
    async def read_file(self, workspace_id: str, file_path: str) -> Dict[str, Any]:
        """Read file contents"""
        return await self.fs.read_file(workspace_id, file_path)
    
    async def write_file(self, workspace_id: str, file_path: str, content: str) -> Dict[str, Any]:
        """Write file contents"""
        return await self.fs.write_file(workspace_id, file_path, content)
    
    async def delete_file(self, workspace_id: str, file_path: str) -> Dict[str, Any]:
        """Delete file or directory"""
        return await self.fs.delete_file(workspace_id, file_path)
    
    async def list_files(self, workspace_id: str, directory: str = ".") -> List[Dict[str, Any]]:
        """List files in directory"""
        return await self.fs.list_directory(workspace_id, directory)
    
    async def get_file_tree(self, workspace_id: str) -> Dict[str, Any]:
        """Get complete file tree"""
        return await self.fs.get_file_tree(workspace_id)
    
    async def create_workspace(self, workspace_id: str) -> Dict[str, Any]:
        """Create a new workspace with default structure"""
        workspace_path = self.workspace_root / workspace_id
        workspace_path.mkdir(parents=True, exist_ok=True)
        
        # Create default structure
        (workspace_path / "src").mkdir(exist_ok=True)
        (workspace_path / "tests").mkdir(exist_ok=True)
        
        # Create README
        readme_path = "README.md"
        content = f"# Workspace: {workspace_id}\n\nCreated by AI Orchestrator IDE\n"
        await self.fs.write_file(workspace_id, readme_path, content)
        
        return {
            "workspace_id": workspace_id,
            "status": "created"
        }
    
    # --- Intelligence Operations (Delegated to IntelligenceService) ---
    
    async def get_completions(
        self,
        workspace_id: str,
        file_path: str,
        cursor_offset: int,
        language: str
    ) -> List[Dict[str, Any]]:
        """Get AI-powered code completions"""
        if not self.intelligence:
            return []
            
        file_data = await self.fs.read_file(workspace_id, file_path)
        return await self.intelligence.get_completions(
            code=file_data["content"],
            language=language or file_data["language"],
            cursor_offset=cursor_offset,
            file_path=file_path
        )
    
    async def get_hover_info(
        self,
        workspace_id: str,
        file_path: str,
        symbol: str,
        language: str = None
    ) -> Dict[str, Any]:
        """Get information about a symbol on hover"""
        if not self.intelligence:
            return {"error": "Intelligence service not available"}
            
        file_data = await self.fs.read_file(workspace_id, file_path)
        return await self.intelligence.get_hover_info(
            code=file_data["content"],
            language=language or file_data["language"],
            symbol=symbol,
            file_path=file_path
        )
    
    async def get_diagnostics(
        self,
        workspace_id: str,
        file_path: str,
        language: str = None
    ) -> List[Dict[str, Any]]:
        """Get code diagnostics"""
        if not self.intelligence:
            return []
            
        file_data = await self.fs.read_file(workspace_id, file_path)
        return await self.intelligence.get_diagnostics(
            code=file_data["content"],
            language=language or file_data["language"],
            file_path=file_path
        )
    
    async def ai_refactor(
        self,
        workspace_id: str,
        file_path: str,
        instruction: str,
        language: str = None
    ) -> Dict[str, Any]:
        """Perform AI-powered refactoring"""
        if not self.intelligence:
            return {"error": "Intelligence service not available"}
            
        file_data = await self.fs.read_file(workspace_id, file_path)
        return await self.intelligence.ai_refactor(
            code=file_data["content"],
            instruction=instruction,
            language=language or file_data["language"]
        )
    
    # --- Code Formatting ---
    
    async def format_code(
        self,
        workspace_id: str,
        file_path: str,
        language: str = None
    ) -> Dict[str, Any]:
        """Format code using language-specific formatter"""
        file_data = await self.fs.read_file(workspace_id, file_path)
        code = file_data["content"]
        lang = language or file_data["language"]
        
        # Format based on language
        formatted_code = code
        try:
            if lang == "python":
                import black
                formatted_code = black.format_str(code, mode=black.Mode())
            # Add other formatters here as needed
        except Exception as e:
            logger.warning(f"Formatting failed for {lang}: {e}")
            return {"status": "formatting_failed", "error": str(e)}
            
        if formatted_code != code:
            await self.fs.write_file(workspace_id, file_path, formatted_code)
            return {"status": "formatted", "path": file_path}
            
        return {"status": "unchanged", "path": file_path}
    
    async def search_in_files(
        self,
        workspace_id: str,
        query: str,
        file_pattern: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Search for text in workspace files"""
        return await self.fs.search_files(workspace_id, query, file_pattern)
