"""
Browser-Based IDE - Editor Service
Provides file operations, LSP integration, and code intelligence
"""
from pathlib import Path
from typing import Dict, Any, List, Optional
import aiofiles


class EditorService:
    """Browser-based code editor service"""
    
    def __init__(self, workspace_root: str = "./workspaces"):
        self.workspace_root = Path(workspace_root)
        self.workspace_root.mkdir(parents=True, exist_ok=True)
        self.lsp_servers: Dict[str, Any] = {}
    
    async def read_file(self, workspace_id: str, file_path: str) -> Dict[str, Any]:
        """Read file contents"""
        full_path = self.workspace_root / workspace_id / file_path
        
        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Security check: ensure path is within workspace
        if not str(full_path.resolve()).startswith(str((self.workspace_root / workspace_id).resolve())):
            raise PermissionError("Access denied: path outside workspace")
        
        async with aiofiles.open(full_path, 'r', encoding='utf-8') as f:
            content = await f.read()
        
        return {
            "path": file_path,
            "content": content,
            "size": full_path.stat().st_size,
            "modified": full_path.stat().st_mtime
        }
    
    async def write_file(self, workspace_id: str, file_path: str, content: str) -> Dict[str, Any]:
        """Write file contents"""
        full_path = self.workspace_root / workspace_id / file_path
        
        # Security check
        if not str(full_path.resolve()).startswith(str((self.workspace_root / workspace_id).resolve())):
            raise PermissionError("Access denied: path outside workspace")
        
        # Create parent directories
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        async with aiofiles.open(full_path, 'w', encoding='utf-8') as f:
            await f.write(content)
        
        return {
            "path": file_path,
            "size": full_path.stat().st_size,
            "modified": full_path.stat().st_mtime,
            "status": "saved"
        }
    
    async def delete_file(self, workspace_id: str, file_path: str) -> Dict[str, Any]:
        """Delete file"""
        full_path = self.workspace_root / workspace_id / file_path
        
        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Security check
        if not str(full_path.resolve()).startswith(str((self.workspace_root / workspace_id).resolve())):
            raise PermissionError("Access denied: path outside workspace")
        
        if full_path.is_dir():
            import shutil
            shutil.rmtree(full_path)
        else:
            full_path.unlink()
        
        return {
            "path": file_path,
            "status": "deleted"
        }
    
    async def list_files(self, workspace_id: str, directory: str = ".") -> List[Dict[str, Any]]:
        """List files in directory"""
        full_path = self.workspace_root / workspace_id / directory
        
        if not full_path.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")
        
        # Security check
        if not str(full_path.resolve()).startswith(str((self.workspace_root / workspace_id).resolve())):
            raise PermissionError("Access denied: path outside workspace")
        
        files = []
        for item in full_path.iterdir():
            files.append({
                "name": item.name,
                "path": str(item.relative_to(self.workspace_root / workspace_id)),
                "type": "directory" if item.is_dir() else "file",
                "size": item.stat().st_size if item.is_file() else 0,
                "modified": item.stat().st_mtime
            })
        
        return sorted(files, key=lambda x: (x["type"] != "directory", x["name"]))
    
    async def create_workspace(self, workspace_id: str) -> Dict[str, Any]:
        """Create a new workspace"""
        workspace_path = self.workspace_root / workspace_id
        workspace_path.mkdir(parents=True, exist_ok=True)
        
        # Create default structure
        (workspace_path / "src").mkdir(exist_ok=True)
        (workspace_path / "tests").mkdir(exist_ok=True)
        
        # Create README
        readme_path = workspace_path / "README.md"
        async with aiofiles.open(readme_path, 'w') as f:
            await f.write(f"# Workspace: {workspace_id}\n\nCreated by AI Orchestrator IDE\n")
        
        return {
            "workspace_id": workspace_id,
            "path": str(workspace_path),
            "status": "created"
        }
    
    async def get_completions(
        self,
        workspace_id: str,
        file_path: str,
        line: int,
        column: int,
        language: str
    ) -> List[Dict[str, Any]]:
        """Get code completions (LSP integration)"""
        # This would integrate with Language Server Protocol
        # For now, return basic completions
        
        # TODO: Implement LSP client integration
        # - Start LSP server for language
        # - Send textDocument/completion request
        # - Parse and return completions
        
        return [
            {
                "label": "example_function",
                "kind": "function",
                "detail": "Example function",
                "documentation": "This is an example completion"
            }
        ]
    
    async def format_code(
        self,
        workspace_id: str,
        file_path: str,
        language: str
    ) -> Dict[str, Any]:
        """Format code using language-specific formatter"""
        content = await self.read_file(workspace_id, file_path)
        
        # Format based on language
        formatters = {
            "python": self._format_python,
            "javascript": self._format_javascript,
            "typescript": self._format_typescript,
            "go": self._format_go,
            "rust": self._format_rust
        }
        
        formatter = formatters.get(language)
        if formatter:
            formatted_content = await formatter(content["content"])
            await self.write_file(workspace_id, file_path, formatted_content)
            return {"status": "formatted", "path": file_path}
        
        return {"status": "no_formatter", "path": file_path}
    
    async def _format_python(self, code: str) -> str:
        """Format Python code using black"""
        try:
            import black
            return black.format_str(code, mode=black.Mode())
        except Exception:
            return code
    
    async def _format_javascript(self, code: str) -> str:
        """Format JavaScript code"""
        # Would use prettier or similar
        return code
    
    async def _format_typescript(self, code: str) -> str:
        """Format TypeScript code"""
        # Would use prettier or similar
        return code
    
    async def _format_go(self, code: str) -> str:
        """Format Go code"""
        # Would use gofmt
        return code
    
    async def _format_rust(self, code: str) -> str:
        """Format Rust code"""
        # Would use rustfmt
        return code
    
    async def search_in_files(
        self,
        workspace_id: str,
        query: str,
        file_pattern: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Search for text in workspace files"""
        workspace_path = self.workspace_root / workspace_id
        results = []
        
        for file_path in workspace_path.rglob(file_pattern or "*"):
            if file_path.is_file():
                try:
                    async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                        content = await f.read()
                    
                    lines = content.split('\n')
                    for line_num, line in enumerate(lines, 1):
                        if query.lower() in line.lower():
                            results.append({
                                "file": str(file_path.relative_to(workspace_path)),
                                "line": line_num,
                                "content": line.strip(),
                                "column": line.lower().index(query.lower())
                            })
                except Exception:
                    continue
        
        return results


class LSPManager:
    """Language Server Protocol Manager"""
    
    def __init__(self):
        self.servers: Dict[str, Any] = {}
    
    async def start_server(self, language: str, workspace_path: str) -> bool:
        """Start LSP server for language"""
        # Map language to LSP server command
        server_commands = {
            "python": ["pylsp"],
            "javascript": ["typescript-language-server", "--stdio"],
            "typescript": ["typescript-language-server", "--stdio"],
            "go": ["gopls"],
            "rust": ["rust-analyzer"],
            "java": ["jdtls"],
            "csharp": ["omnisharp"]
        }
        
        command = server_commands.get(language)
        if not command:
            return False
        
        # TODO: Start LSP server process
        # - Use asyncio.create_subprocess_exec
        # - Handle stdin/stdout communication
        # - Implement LSP protocol
        
        return True
    
    async def stop_server(self, language: str) -> bool:
        """Stop LSP server"""
        if language in self.servers:
            # TODO: Send shutdown request to LSP server
            # - Send shutdown request
            # - Wait for response
            # - Terminate process
            del self.servers[language]
            return True
        return False
