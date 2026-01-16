"""
File System Service - Complete implementation for browser IDE
Provides comprehensive file and directory operations with quota enforcement
"""

import os
import shutil
import mimetypes
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import aiofiles
import asyncio
from fastapi import HTTPException


class FileSystemService:
    """Complete file system service for browser IDE"""
    
    def __init__(self, base_path: str = "storage/workspaces"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        # File size limits
        self.max_file_size_mb = 100
        
        # Excluded patterns (don't show in file tree)
        self.excluded_patterns = {
            '__pycache__',
            'node_modules',
            '.git',
            '.venv',
            'venv',
            '.idea',
            '.vscode',
            '*.pyc',
            '*.pyo',
            '.DS_Store'
        }
    
    def _get_workspace_path(self, workspace_id: str) -> Path:
        """Get workspace directory path"""
        workspace_path = self.base_path / workspace_id
        workspace_path.mkdir(parents=True, exist_ok=True)
        return workspace_path
    
    def _resolve_path(self, workspace_id: str, file_path: str) -> Path:
        """
        Resolve and validate file path
        Prevents directory traversal attacks
        """
        workspace_path = self._get_workspace_path(workspace_id)
        target_path = (workspace_path / file_path.lstrip("/")).resolve()
        
        # Security check: ensure path is within workspace
        if not str(target_path).startswith(str(workspace_path)):
            raise HTTPException(403, "Access denied: Path outside workspace")
        
        return target_path
    
    def _should_exclude(self, path: Path) -> bool:
        """Check if path should be excluded from listings"""
        for pattern in self.excluded_patterns:
            if pattern.startswith('*'):
                # Wildcard pattern
                if path.name.endswith(pattern[1:]):
                    return True
            else:
                # Exact match
                if path.name == pattern:
                    return True
        return False
    
    async def list_directory(
        self,
        workspace_id: str,
        path: str = "/"
    ) -> List[Dict[str, Any]]:
        """
        List directory contents with metadata
        
        Args:
            workspace_id: Workspace ID
            path: Directory path (relative to workspace root)
            
        Returns:
            List of file/directory entries with metadata
        """
        full_path = self._resolve_path(workspace_id, path)
        
        if not full_path.exists():
            raise HTTPException(404, f"Directory not found: {path}")
        
        if not full_path.is_dir():
            raise HTTPException(400, f"Not a directory: {path}")
        
        entries = []
        
        for item in sorted(full_path.iterdir()):
            # Skip excluded items
            if self._should_exclude(item):
                continue
            
            try:
                stat = item.stat()
                
                entry = {
                    "name": item.name,
                    "path": str(item.relative_to(self._get_workspace_path(workspace_id))),
                    "type": "directory" if item.is_dir() else "file",
                    "size": stat.st_size if item.is_file() else 0,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                }
                
                # Add file-specific metadata
                if item.is_file():
                    entry["extension"] = item.suffix
                    entry["mime_type"] = mimetypes.guess_type(item.name)[0]
                    entry["is_binary"] = self._is_binary_file(item)
                
                entries.append(entry)
                
            except Exception as e:
                # Skip files that can't be accessed
                continue
        
        # Sort: directories first, then files alphabetically
        entries.sort(key=lambda x: (x["type"] != "directory", x["name"].lower()))
        
        return entries
    
    async def read_file(self, workspace_id: str, file_path: str) -> Dict[str, Any]:
        """
        Read file content
        
        Args:
            workspace_id: Workspace ID
            file_path: File path
            
        Returns:
            File content and metadata
        """
        full_path = self._resolve_path(workspace_id, file_path)
        
        if not full_path.exists():
            raise HTTPException(404, f"File not found: {file_path}")
        
        if not full_path.is_file():
            raise HTTPException(400, f"Not a file: {file_path}")
        
        # Check if binary
        if self._is_binary_file(full_path):
            raise HTTPException(400, "Cannot read binary file as text")
        
        # Read file
        async with aiofiles.open(full_path, 'r', encoding='utf-8') as f:
            content = await f.read()
        
        stat = full_path.stat()
        
        return {
            "path": file_path,
            "content": content,
            "size": stat.st_size,
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "encoding": "utf-8",
            "line_count": content.count('\n') + 1,
            "language": self._detect_language(full_path)
        }
    
    async def write_file(
        self,
        workspace_id: str,
        file_path: str,
        content: str
    ) -> Dict[str, Any]:
        """
        Write file content
        
        Args:
            workspace_id: Workspace ID
            file_path: File path
            content: File content
            
        Returns:
            File metadata
        """
        full_path = self._resolve_path(workspace_id, file_path)
        
        # Check file size
        content_size_mb = len(content.encode('utf-8')) / (1024 * 1024)
        if content_size_mb > self.max_file_size_mb:
            raise HTTPException(413, f"File too large: {content_size_mb:.2f}MB (max {self.max_file_size_mb}MB)")
        
        # Create parent directories
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write file
        async with aiofiles.open(full_path, 'w', encoding='utf-8') as f:
            await f.write(content)
        
        stat = full_path.stat()
        
        return {
            "path": file_path,
            "size": stat.st_size,
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "message": "File saved successfully"
        }
    
    async def delete_file(self, workspace_id: str, file_path: str) -> Dict[str, str]:
        """
        Delete file or directory
        
        Args:
            workspace_id: Workspace ID
            file_path: File/directory path
            
        Returns:
            Success message
        """
        full_path = self._resolve_path(workspace_id, file_path)
        
        if not full_path.exists():
            raise HTTPException(404, f"Path not found: {file_path}")
        
        if full_path.is_dir():
            shutil.rmtree(full_path)
            message = "Directory deleted successfully"
        else:
            full_path.unlink()
            message = "File deleted successfully"
        
        return {"message": message, "path": file_path}
    
    async def create_directory(
        self,
        workspace_id: str,
        dir_path: str
    ) -> Dict[str, Any]:
        """
        Create directory
        
        Args:
            workspace_id: Workspace ID
            dir_path: Directory path
            
        Returns:
            Directory metadata
        """
        full_path = self._resolve_path(workspace_id, dir_path)
        
        if full_path.exists():
            raise HTTPException(400, f"Path already exists: {dir_path}")
        
        full_path.mkdir(parents=True, exist_ok=True)
        
        return {
            "path": dir_path,
            "type": "directory",
            "message": "Directory created successfully"
        }
    
    async def rename(
        self,
        workspace_id: str,
        old_path: str,
        new_path: str
    ) -> Dict[str, Any]:
        """
        Rename/move file or directory
        
        Args:
            workspace_id: Workspace ID
            old_path: Current path
            new_path: New path
            
        Returns:
            Success message
        """
        old_full_path = self._resolve_path(workspace_id, old_path)
        new_full_path = self._resolve_path(workspace_id, new_path)
        
        if not old_full_path.exists():
            raise HTTPException(404, f"Source not found: {old_path}")
        
        if new_full_path.exists():
            raise HTTPException(400, f"Destination already exists: {new_path}")
        
        # Create parent directory if needed
        new_full_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Rename/move
        old_full_path.rename(new_full_path)
        
        return {
            "old_path": old_path,
            "new_path": new_path,
            "message": "Renamed successfully"
        }
    
    async def copy(
        self,
        workspace_id: str,
        source_path: str,
        dest_path: str
    ) -> Dict[str, Any]:
        """
        Copy file or directory
        
        Args:
            workspace_id: Workspace ID
            source_path: Source path
            dest_path: Destination path
            
        Returns:
            Success message
        """
        source_full_path = self._resolve_path(workspace_id, source_path)
        dest_full_path = self._resolve_path(workspace_id, dest_path)
        
        if not source_full_path.exists():
            raise HTTPException(404, f"Source not found: {source_path}")
        
        if dest_full_path.exists():
            raise HTTPException(400, f"Destination already exists: {dest_path}")
        
        # Create parent directory
        dest_full_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Copy
        if source_full_path.is_dir():
            shutil.copytree(source_full_path, dest_full_path)
        else:
            shutil.copy2(source_full_path, dest_full_path)
        
        return {
            "source_path": source_path,
            "dest_path": dest_path,
            "message": "Copied successfully"
        }
    
    async def search_files(
        self,
        workspace_id: str,
        query: str,
        file_pattern: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for files by name or content
        
        Args:
            workspace_id: Workspace ID
            query: Search query
            file_pattern: Optional file pattern (e.g., "*.py")
            
        Returns:
            List of matching files
        """
        workspace_path = self._get_workspace_path(workspace_id)
        results = []
        
        # Search in file names and content
        for file_path in workspace_path.rglob("*"):
            if file_path.is_file() and not self._should_exclude(file_path):
                # Check file pattern
                if file_pattern and not file_path.match(file_pattern):
                    continue
                
                # Search in filename
                if query.lower() in file_path.name.lower():
                    results.append({
                        "path": str(file_path.relative_to(workspace_path)),
                        "name": file_path.name,
                        "match_type": "filename",
                        "size": file_path.stat().st_size
                    })
                    continue
                
                # Search in content (text files only)
                if not self._is_binary_file(file_path):
                    try:
                        async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                            content = await f.read()
                            if query.lower() in content.lower():
                                # Find line numbers
                                lines = content.split('\n')
                                matches = [
                                    i + 1 for i, line in enumerate(lines)
                                    if query.lower() in line.lower()
                                ]
                                
                                results.append({
                                    "path": str(file_path.relative_to(workspace_path)),
                                    "name": file_path.name,
                                    "match_type": "content",
                                    "line_numbers": matches[:10],  # Limit to first 10 matches
                                    "match_count": len(matches)
                                })
                    except:
                        # Skip files that can't be read
                        pass
        
        return results[:100]  # Limit results
    
    async def get_file_tree(
        self,
        workspace_id: str,
        max_depth: int = 5
    ) -> Dict[str, Any]:
        """
        Get complete file tree structure
        
        Args:
            workspace_id: Workspace ID
            max_depth: Maximum depth to traverse
            
        Returns:
            Nested file tree structure
        """
        workspace_path = self._get_workspace_path(workspace_id)
        
        def build_tree(path: Path, depth: int = 0) -> Dict[str, Any]:
            if depth > max_depth:
                return None
            
            if self._should_exclude(path):
                return None
            
            node = {
                "name": path.name if path != workspace_path else "/",
                "path": str(path.relative_to(workspace_path)) if path != workspace_path else "/",
                "type": "directory" if path.is_dir() else "file"
            }
            
            if path.is_dir():
                children = []
                for child in sorted(path.iterdir()):
                    child_node = build_tree(child, depth + 1)
                    if child_node:
                        children.append(child_node)
                node["children"] = children
            else:
                stat = path.stat()
                node["size"] = stat.st_size
                node["extension"] = path.suffix
            
            return node
        
        return build_tree(workspace_path)
    
    def _is_binary_file(self, file_path: Path) -> bool:
        """Check if file is binary"""
        text_extensions = {
            '.txt', '.py', '.js', '.ts', '.jsx', '.tsx', '.html', '.css', '.scss',
            '.json', '.xml', '.yaml', '.yml', '.md', '.rst', '.go', '.rs', '.java',
            '.c', '.cpp', '.h', '.hpp', '.cs', '.php', '.rb', '.sh', '.bash', '.sql',
            '.env', '.gitignore', '.dockerignore', '.conf', '.ini', '.toml'
        }
        
        if file_path.suffix.lower() in text_extensions:
            return False
        
        # Check by reading first bytes
        try:
            with open(file_path, 'rb') as f:
                chunk = f.read(1024)
                return b'\x00' in chunk
        except:
            return True
    
    def _detect_language(self, file_path: Path) -> str:
        """Detect programming language from file extension"""
        extension_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'javascriptreact',
            '.tsx': 'typescriptreact',
            '.java': 'java',
            '.go': 'go',
            '.rs': 'rust',
            '.c': 'c',
            '.cpp': 'cpp',
            '.cs': 'csharp',
            '.php': 'php',
            '.rb': 'ruby',
            '.html': 'html',
            '.css': 'css',
            '.scss': 'scss',
            '.json': 'json',
            '.xml': 'xml',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.md': 'markdown',
            '.sql': 'sql',
            '.sh': 'shellscript',
        }
        
        return extension_map.get(file_path.suffix.lower(), 'plaintext')
