"""
Service Container
Dependency Injection container for global services to avoid circular imports
and allow controllers to access shared resources.
"""
from typing import Optional, Dict

from app.core.container import container as app_container

class ServiceContainer:
    """
    Unified Service Container Proxy.
    Maintains backward compatibility with legacy 'from core.container import container' 
    while delegating to the unified DeclarativeContainer in app.core.
    """
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = ServiceContainer()
        return cls._instance

    # Core Services
    @property
    def orchestrator(self): return app_container.orchestrator()
    @property
    def git_credentials(self): return app_container.git_credentials()
    @property
    def repo_manager(self): return app_container.repo_manager()
    @property
    def db_manager(self): return app_container.db_conn_manager()
    @property
    def schema_analyzer(self): return app_container.schema_analyzer()
    @property
    def entity_generator(self): return app_container.entity_generator()
    @property
    def language_registry(self): return app_container.language_registry()
    
    # IDE Services
    @property
    def editor_service(self): return app_container.editor_service()
    @property
    def terminal_service(self): return app_container.terminal_service()
    @property
    def debugger_service(self): return app_container.debugger_service()
    
    # Project Management Services
    @property
    def project_manager(self): return app_container.project_manager()
    @property
    def git_sync_service(self): return app_container.git_sync_service()
    @property
    def ai_update_service(self): return app_container.ai_update_service()
    @property
    def build_service(self): return app_container.build_service()
    @property
    def runtime_service(self): return app_container.runtime_service()
    @property
    def workflow_engine(self): return app_container.workflow_engine()
    @property
    def monitoring_service(self): return app_container.monitoring_service()
    @property
    def storage_manager(self): return app_container.storage_manager()
    @property
    def backup_manager(self): return app_container.backup_manager()
    @property
    def collaboration_service(self): return app_container.collaboration_service()
    
    # Extreme Power 2026 Services
    @property
    def iac_engine(self): return app_container.iac_engine()
    @property
    def cost_pilot(self): return app_container.cost_pilot()
    @property
    def red_team_ai(self): return app_container.red_team_ai()
    
    # Next-Gen Core 2026+
    @property
    def message_bus(self): return app_container.message_bus()
    @property
    def calt_logger(self): return app_container.calt_logger()
    
    # Hyper-Intelligence 2026 Final
    @property
    def knowledge_graph(self): return app_container.knowledge_graph()
    @property
    def quantum_vault(self): return app_container.quantum_vault()
    
    # Strategic 20/20 Refinements
    @property
    def mcp_bridge(self): return app_container.mcp_bridge()
    
    # Compatibility Methods (No-ops in unified mode)
    def initialize_services(self, *args, **kwargs): pass
    def initialize_ide_services(self, *args, **kwargs): pass
    def initialize_project_services(self, *args, **kwargs): pass
    def initialize_extreme_power_services(self, *args, **kwargs): pass
    def initialize_next_gen_services(self, *args, **kwargs): pass
    def initialize_hyper_intelligence_services(self, *args, **kwargs): pass
    def initialize_strategic_services(self, *args, **kwargs): pass

# Global accessor
container = ServiceContainer.get_instance()
