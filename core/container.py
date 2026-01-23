"""
Service Container
Dependency Injection container for global services to avoid circular imports
and allow controllers to access shared resources.
"""
from typing import Optional, Dict

class ServiceContainer:
    _instance = None
    
    def __init__(self):
        # Core Services
        self.orchestrator = None
        self.git_credentials = None
        self.repo_manager = None
        self.db_manager = None
        self.schema_analyzer = None
        self.entity_generator = None
        self.language_registry = None
        
        # IDE Services
        self.editor_service = None
        self.terminal_service = None
        self.debugger_service = None
        
        # Project Management Services
        self.project_manager = None
        self.git_sync_service = None
        self.ai_update_service = None
        self.build_service = None
        self.runtime_service = None
        self.workflow_engine = None
        self.monitoring_service = None
        self.storage_manager = None
        self.backup_manager = None
        self.collaboration_service = None
        
        # Security
        self.auth_router = None
        
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = ServiceContainer()
        return cls._instance

    def initialize_services(self, orchestrator, git_credentials, repo_manager, db_manager, 
                          schema_analyzer, entity_generator, language_registry):
        """Initialize core platform services"""
        self.orchestrator = orchestrator
        self.git_credentials = git_credentials
        self.repo_manager = repo_manager
        self.db_manager = db_manager
        self.schema_analyzer = schema_analyzer
        self.entity_generator = entity_generator
        self.language_registry = language_registry
        
    def initialize_ide_services(self, editor, terminal, debugger):
        """Initialize IDE services"""
        self.editor_service = editor
        self.terminal_service = terminal
        self.debugger_service = debugger
        
    def initialize_project_services(self, project_manager, git_sync, ai_update, build, runtime, workflow, monitoring, storage, backup, collaboration):
        """Initialize Project Management services"""
        self.project_manager = project_manager
        self.git_sync_service = git_sync
        self.ai_update_service = ai_update
        self.build_service = build
        self.runtime_service = runtime
        self.workflow_engine = workflow
        self.monitoring_service = monitoring
        self.storage_manager = storage
        self.backup_manager = backup
        self.collaboration_service = collaboration

# Global accessor
container = ServiceContainer.get_instance()
