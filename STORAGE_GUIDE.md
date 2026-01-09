# Storage Guide - AI Orchestrator

## Overview

The AI Orchestrator uses a local storage architecture designed to handle large-scale projects (>1GB) with unlimited capacity, version control, and automated backup capabilities.

## Storage Architecture

### Directory Structure

```
storage/
├── projects/           # Active generated and migrated projects
│   ├── {project-id}/
│   │   ├── metadata.json
│   │   ├── source/
│   │   └── artifacts/
├── archives/           # Archived projects (90+ days old)
│   ├── {year}/
│   │   └── {month}/
│   │       └── {project-id}.tar.gz
├── templates/          # Project templates
│   ├── backend/
│   ├── frontend/
│   └── fullstack/
└── cache/             # Temporary build cache
    └── {workbench-id}/
```

### Project Metadata

Each project includes a `metadata.json` file:

```json
{
  "project_id": "uuid-here",
  "name": "ecommerce-platform",
  "type": "generation|migration",
  "created_at": "2026-01-09T15:00:00Z",
  "size_bytes": 1073741824,
  "languages": ["python", "typescript"],
  "frameworks": ["fastapi", "react"],
  "status": "active|archived|deleted",
  "tags": ["ecommerce", "production"],
  "git_repository": "https://github.com/user/repo"
}
```

## Storage Configuration

### Configuration File: `config/storage.yaml`

```yaml
storage:
  # Base storage path (absolute or relative)
  base_path: "./storage"
  
  # Maximum size per project (in GB)
  max_project_size: 10
  
  # Total storage quota (in GB, 0 = unlimited)
  total_quota: 0
  
  # Archive projects older than X days
  archive_after_days: 90
  
  # Enable automatic cleanup
  cleanup_enabled: true
  
  # Cleanup schedule (cron format)
  cleanup_schedule: "0 2 * * 0"  # Weekly at 2 AM
  
  # Backup configuration
  backup:
    enabled: true
    frequency: "daily"  # daily, weekly, monthly
    retention_days: 30
    compression: true
    destination: "./backups"
```

### Environment Variables

```powershell
# Override storage base path
$env:STORAGE_BASE_PATH="D:\AI-Projects\storage"

# Override max project size (in GB)
$env:STORAGE_MAX_PROJECT_SIZE="20"

# Override total quota (in GB)
$env:STORAGE_TOTAL_QUOTA="500"

# Enable/disable backup
$env:STORAGE_BACKUP_ENABLED="true"
```

## Large Project Handling (>1GB)

### Optimization Strategies

1. **Incremental Storage**
   - Only store changed files
   - Use git-like diff storage
   - Compress artifacts

2. **Streaming Operations**
   - Stream large files instead of loading into memory
   - Use chunked uploads/downloads
   - Progress tracking for large operations

3. **Compression**
   - Automatic compression for archived projects
   - Configurable compression levels
   - Selective compression (code vs. binaries)

### Example: Storing a Large Project

```python
from core.storage import StorageManager

storage = StorageManager()

# Store large project with progress tracking
project_id = await storage.store_project(
    project_path="/path/to/large/project",
    metadata={
        "name": "enterprise-erp",
        "type": "generation",
        "size_bytes": 5368709120  # 5GB
    },
    compress=True,
    on_progress=lambda progress: print(f"Progress: {progress}%")
)

print(f"Project stored with ID: {project_id}")
```

## Storage Management

### List Projects

```python
# List all active projects
projects = await storage.list_projects(status="active")

# List by language
python_projects = await storage.list_projects(language="python")

# List by size
large_projects = await storage.list_projects(min_size_gb=1)
```

### Retrieve Project

```python
# Get project by ID
project = await storage.get_project(project_id)

# Extract to temporary directory
extracted_path = await storage.extract_project(
    project_id,
    destination="/tmp/workspace"
)
```

### Archive Project

```python
# Archive old project
await storage.archive_project(project_id)

# Archive all projects older than 90 days
archived_count = await storage.archive_old_projects(days=90)
```

### Delete Project

```python
# Soft delete (mark as deleted)
await storage.delete_project(project_id, soft=True)

# Hard delete (permanent removal)
await storage.delete_project(project_id, soft=False)
```

## Backup & Recovery

### Automated Backups

Backups run automatically based on `storage.yaml` configuration:

```yaml
backup:
  enabled: true
  frequency: "daily"
  retention_days: 30
  compression: true
  destination: "./backups"
```

### Manual Backup

```python
from core.storage import BackupManager

backup_mgr = BackupManager()

# Backup specific project
backup_id = await backup_mgr.backup_project(project_id)

# Backup all projects
backup_id = await backup_mgr.backup_all_projects()

# List backups
backups = await backup_mgr.list_backups()
```

### Recovery

```python
# Restore from backup
await backup_mgr.restore_project(
    backup_id=backup_id,
    project_id=project_id,
    destination="/path/to/restore"
)

# Restore all projects from backup
await backup_mgr.restore_all_projects(backup_id)
```

## Storage Cleanup

### Automatic Cleanup

Cleanup runs on schedule (configured in `storage.yaml`):

- Archives projects older than `archive_after_days`
- Removes old backups beyond `retention_days`
- Cleans temporary cache files
- Optimizes storage usage

### Manual Cleanup

```python
from core.storage import StorageManager

storage = StorageManager()

# Clean cache
await storage.clean_cache()

# Archive old projects
archived = await storage.archive_old_projects(days=90)

# Remove old backups
removed = await storage.cleanup_old_backups(days=30)

# Full cleanup
report = await storage.full_cleanup()
print(f"Freed: {report['freed_bytes']} bytes")
```

## Storage Monitoring

### Check Storage Usage

```python
# Get storage statistics
stats = await storage.get_storage_stats()

print(f"Total projects: {stats['total_projects']}")
print(f"Total size: {stats['total_size_gb']} GB")
print(f"Active projects: {stats['active_projects']}")
print(f"Archived projects: {stats['archived_projects']}")
print(f"Available space: {stats['available_space_gb']} GB")
```

### Storage API Endpoints

```bash
# Get storage statistics
GET /api/storage/stats

# List projects
GET /api/storage/projects?status=active&language=python

# Get project details
GET /api/storage/projects/{project_id}

# Archive project
POST /api/storage/archive/{project_id}

# Delete project
DELETE /api/storage/projects/{project_id}

# Trigger cleanup
POST /api/storage/cleanup
```

## Best Practices

### 1. Regular Archiving
- Archive projects after completion
- Keep only active projects in main storage
- Use tags for easy filtering

### 2. Backup Strategy
- Enable daily backups
- Keep 30-day retention minimum
- Store backups on separate drive/location

### 3. Storage Optimization
- Enable compression for archives
- Clean cache regularly
- Monitor storage usage

### 4. Large Project Handling
- Use streaming for >1GB projects
- Enable compression
- Monitor progress during operations

### 5. Disaster Recovery
- Test backup restoration regularly
- Keep multiple backup copies
- Document recovery procedures

## Troubleshooting

### Issue: Storage Full

```powershell
# Check storage usage
curl http://localhost:8080/api/storage/stats

# Archive old projects
curl -X POST http://localhost:8080/api/storage/cleanup

# Increase quota in config/storage.yaml
```

### Issue: Slow Project Retrieval

```powershell
# Check if project is archived
curl http://localhost:8080/api/storage/projects/{id}

# Extract to cache for faster access
curl -X POST http://localhost:8080/api/storage/extract/{id}
```

### Issue: Backup Failed

```powershell
# Check backup logs
cat logs/backup.log

# Verify backup destination exists
ls ./backups

# Manually trigger backup
curl -X POST http://localhost:8080/api/storage/backup
```

## Migration from Other Storage

### From Cloud Storage (S3, Azure Blob)

```python
# Import from S3
from core.storage import StorageManager, CloudImporter

storage = StorageManager()
importer = CloudImporter(provider="s3")

# Import project from S3
project_id = await importer.import_from_cloud(
    bucket="my-bucket",
    key="projects/my-project.tar.gz",
    storage_manager=storage
)
```

### From Local Directory

```python
# Import existing project
project_id = await storage.import_project(
    source_path="/path/to/existing/project",
    metadata={
        "name": "legacy-project",
        "type": "migration"
    }
)
```

## Advanced Configuration

### Custom Storage Backend

```python
# Implement custom storage backend
from core.storage import StorageBackend

class S3StorageBackend(StorageBackend):
    async def store(self, data, path):
        # Custom S3 implementation
        pass
    
    async def retrieve(self, path):
        # Custom S3 implementation
        pass

# Use custom backend
storage = StorageManager(backend=S3StorageBackend())
```

### Storage Plugins

```python
# Register storage plugin
from core.storage import StoragePlugin

class CompressionPlugin(StoragePlugin):
    async def on_store(self, project_data):
        # Compress before storing
        return compressed_data
    
    async def on_retrieve(self, project_data):
        # Decompress after retrieving
        return decompressed_data

storage.register_plugin(CompressionPlugin())
```

---

**For more information, see:**
- [CONFIGURATION_GUIDE.md](CONFIGURATION_GUIDE.md) - Configuration reference
- [API_DOCUMENTATION.md](API_DOCUMENTATION.md) - API endpoints
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues
