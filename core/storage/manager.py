"""
Storage Manager - Handle large project storage (>1GB)
"""
import os
import json
import shutil
import tarfile
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import asyncio


class StorageManager:
    """Manage local storage for generated and migrated projects"""
    
    def __init__(self, config_path: str = "config/storage.yaml"):
        self.config = self._load_config(config_path)
        self.base_path = Path(self.config.get("storage", {}).get("base_path", "./storage"))
        self.projects_path = self.base_path / "projects"
        self.archives_path = self.base_path / "archives"
        self.templates_path = self.base_path / "templates"
        self.cache_path = self.base_path / "cache"
        
        # Ensure directories exist
        self._ensure_directories()
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            import yaml
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Warning: Could not load config from {config_path}: {e}")
            return {}
    
    def _ensure_directories(self):
        """Ensure all storage directories exist"""
        for path in [self.projects_path, self.archives_path, self.templates_path, self.cache_path]:
            path.mkdir(parents=True, exist_ok=True)
    
    async def store_project(
        self,
        project_path: str,
        metadata: Dict[str, Any],
        compress: bool = False
    ) -> str:
        """
        Store a project in local storage
        
        Args:
            project_path: Path to the project to store
            metadata: Project metadata (name, type, etc.)
            compress: Whether to compress the project
            
        Returns:
            Project ID
        """
        import uuid
        
        project_id = str(uuid.uuid4())
        project_dir = self.projects_path / project_id
        project_dir.mkdir(parents=True, exist_ok=True)
        
        # Add metadata
        metadata["project_id"] = project_id
        metadata["created_at"] = datetime.utcnow().isoformat()
        metadata["status"] = "active"
        
        # Calculate size
        total_size = sum(
            f.stat().st_size for f in Path(project_path).rglob('*') if f.is_file()
        )
        metadata["size_bytes"] = total_size
        
        # Save metadata
        with open(project_dir / "metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # Copy or compress project
        source_dir = project_dir / "source"
        
        if compress:
            # Compress project
            archive_path = project_dir / "source.tar.gz"
            await self._compress_directory(project_path, archive_path)
        else:
            # Copy project
            shutil.copytree(project_path, source_dir, dirs_exist_ok=True)
        
        return project_id
    
    async def _compress_directory(self, source_path: str, archive_path: Path):
        """Compress a directory to tar.gz"""
        def _compress():
            with tarfile.open(archive_path, "w:gz") as tar:
                tar.add(source_path, arcname=os.path.basename(source_path))
        
        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _compress)
    
    async def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get project metadata"""
        project_dir = self.projects_path / project_id
        metadata_file = project_dir / "metadata.json"
        
        if not metadata_file.exists():
            return None
        
        with open(metadata_file, 'r') as f:
            return json.load(f)
    
    async def list_projects(
        self,
        status: Optional[str] = None,
        language: Optional[str] = None,
        min_size_gb: Optional[float] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """List projects with optional filters and pagination"""
        projects = []
        
        for project_dir in self.projects_path.iterdir():
            if not project_dir.is_dir():
                continue
            
            metadata_file = project_dir / "metadata.json"
            if not metadata_file.exists():
                continue
            
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            
            # Apply filters
            if status and metadata.get("status") != status:
                continue
            
            if language and language not in metadata.get("languages", []):
                continue
            
            if min_size_gb:
                size_gb = metadata.get("size_bytes", 0) / (1024**3)
                if size_gb < min_size_gb:
                    continue
            
            projects.append(metadata)
        
        # Sort by creation date (newest first)
        projects.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        total = len(projects)
        start = (page - 1) * page_size
        end = start + page_size
        paginated_projects = projects[start:end]
        
        return {
            "projects": paginated_projects,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }
    
    async def archive_project(self, project_id: str) -> bool:
        """Archive a project"""
        project_dir = self.projects_path / project_id
        metadata_file = project_dir / "metadata.json"
        
        if not metadata_file.exists():
            return False
        
        # Update metadata
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        
        metadata["status"] = "archived"
        metadata["archived_at"] = datetime.utcnow().isoformat()
        
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # Move to archives
        year = datetime.utcnow().year
        month = datetime.utcnow().month
        archive_dir = self.archives_path / str(year) / f"{month:02d}"
        archive_dir.mkdir(parents=True, exist_ok=True)
        
        # Compress and move
        archive_path = archive_dir / f"{project_id}.tar.gz"
        await self._compress_directory(str(project_dir), archive_path)
        
        # Remove from projects
        shutil.rmtree(project_dir)
        
        return True
    
    async def archive_old_projects(self, days: int = 90) -> int:
        """Archive projects older than specified days"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        archived_count = 0
        
        projects = await self.list_projects(status="active")
        
        for project in projects:
            created_at = datetime.fromisoformat(project["created_at"])
            if created_at < cutoff_date:
                await self.archive_project(project["project_id"])
                archived_count += 1
        
        return archived_count
    
    async def delete_project(self, project_id: str, soft: bool = True) -> bool:
        """Delete a project (soft or hard delete)"""
        project_dir = self.projects_path / project_id
        
        if not project_dir.exists():
            return False
        
        if soft:
            # Soft delete - mark as deleted
            metadata_file = project_dir / "metadata.json"
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            
            metadata["status"] = "deleted"
            metadata["deleted_at"] = datetime.utcnow().isoformat()
            
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
        else:
            # Hard delete - remove completely
            shutil.rmtree(project_dir)
        
        return True
    
    async def clean_cache(self) -> int:
        """Clean temporary cache and return freed bytes"""
        freed_bytes = 0
        
        for cache_dir in self.cache_path.iterdir():
            if cache_dir.is_dir():
                size = sum(f.stat().st_size for f in cache_dir.rglob('*') if f.is_file())
                freed_bytes += size
                shutil.rmtree(cache_dir)
        
        return freed_bytes
    
    async def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics"""
        projects = await self.list_projects()
        active_projects = [p for p in projects if p.get("status") == "active"]
        archived_projects = [p for p in projects if p.get("status") == "archived"]
        
        total_size = sum(p.get("size_bytes", 0) for p in projects)
        
        # Get available space
        stat = shutil.disk_usage(self.base_path)
        
        return {
            "total_projects": len(projects),
            "active_projects": len(active_projects),
            "archived_projects": len(archived_projects),
            "total_size_bytes": total_size,
            "total_size_gb": total_size / (1024**3),
            "available_space_bytes": stat.free,
            "available_space_gb": stat.free / (1024**3)
        }
    
    async def extract_project(self, project_id: str, destination: str) -> str:
        """Extract a project to a destination directory"""
        project_dir = self.projects_path / project_id
        source_dir = project_dir / "source"
        
        if source_dir.exists():
            # Project is not compressed
            shutil.copytree(source_dir, destination, dirs_exist_ok=True)
        else:
            # Project is compressed
            archive_path = project_dir / "source.tar.gz"
            if archive_path.exists():
                with tarfile.open(archive_path, "r:gz") as tar:
                    tar.extractall(destination)
        
        return destination


class BackupManager:
    """Manage backups for projects"""
    
    def __init__(self, config_path: str = "config/storage.yaml"):
        self.config = self._load_config(config_path)
        backup_config = self.config.get("storage", {}).get("backup", {})
        self.destination = Path(backup_config.get("destination", "./backups"))
        self.retention_days = backup_config.get("retention_days", 30)
        self.destination.mkdir(parents=True, exist_ok=True)
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            import yaml
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception:
            return {}
    
    async def backup_project(self, project_id: str) -> str:
        """Backup a specific project"""
        import uuid
        
        backup_id = str(uuid.uuid4())
        backup_path = self.destination / f"{backup_id}.tar.gz"
        
        # Compress project
        storage = StorageManager()
        project_dir = storage.projects_path / project_id
        
        await storage._compress_directory(str(project_dir), backup_path)
        
        # Save backup metadata
        metadata = {
            "backup_id": backup_id,
            "project_id": project_id,
            "created_at": datetime.utcnow().isoformat()
        }
        
        with open(self.destination / f"{backup_id}.json", 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return backup_id
    
    async def cleanup_old_backups(self, days: Optional[int] = None) -> int:
        """Remove backups older than retention period"""
        if days is None:
            days = self.retention_days
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        removed_count = 0
        
        for backup_file in self.destination.glob("*.json"):
            with open(backup_file, 'r') as f:
                metadata = json.load(f)
            
            created_at = datetime.fromisoformat(metadata["created_at"])
            if created_at < cutoff_date:
                # Remove backup and metadata
                backup_id = metadata["backup_id"]
                os.remove(self.destination / f"{backup_id}.tar.gz")
                os.remove(backup_file)
                removed_count += 1
        
        return removed_count
