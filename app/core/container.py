"""Dependency injection container."""
import os
from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
import redis.asyncio as redis
from .database import db_manager, DatabaseManager
from .agent_manager import agent_manager, AgentManager

class Container(containers.DeclarativeContainer):
    """Service container for dependency injection."""
    
    config = providers.Configuration()
    
    # --- Infrastructure Layer ---
    db_manager = providers.Singleton(DatabaseManager)
    agent_manager = providers.Singleton(AgentManager)
    redis_client = providers.Singleton(
        redis.from_url,
        url=config.database.redis_url,
        decode_responses=True
    )
    
    # --- Core AI & Platforms ---
    from core.orchestrator import Orchestrator
    orchestrator = providers.Singleton(Orchestrator)
    
    # --- Integration Services ---
    from services.git import GitCredentialManager, RepositoryManager
    git_credentials = providers.Singleton(GitCredentialManager)
    repo_manager = providers.Singleton(RepositoryManager, credentials=git_credentials)
    
    from services.database import DatabaseConnectionManager, SchemaAnalyzer, EntityGenerator
    db_conn_manager = providers.Singleton(DatabaseConnectionManager)
    schema_analyzer = providers.Singleton(SchemaAnalyzer, db_manager=db_conn_manager)
    entity_generator = providers.Singleton(EntityGenerator, orchestrator=orchestrator)
    
    from services.registry import LanguageRegistry
    language_registry = providers.Singleton(LanguageRegistry)
    
    # --- IDE & Development Services ---
    from services.ide import EditorService, TerminalService, DebuggerService
    editor_service = providers.Singleton(EditorService)
    terminal_service = providers.Singleton(TerminalService)
    debugger_service = providers.Singleton(DebuggerService)
    
    # --- Project Management Services ---
    from services.project_manager import ProjectManager
    from services.git_sync import GitSyncService
    from services.ai_update_service import AIUpdateService
    from services.build_service import BuildService
    from services.runtime_service import RuntimeService
    from services.workflow_engine import WorkflowEngine
    from services.monitoring import RealtimeMonitoringService
    from core.storage import StorageManager, BackupManager
    from services.collaboration import CollaborationService
    
    project_manager = providers.Singleton(ProjectManager)
    git_sync_service = providers.Singleton(GitSyncService)
    ai_update_service = providers.Singleton(AIUpdateService, orchestrator=orchestrator)
    build_service = providers.Singleton(BuildService)
    runtime_service = providers.Singleton(RuntimeService)
    monitoring_service = providers.Singleton(RealtimeMonitoringService)
    storage_manager = providers.Singleton(lambda: orchestrator().storage)
    backup_manager = providers.Singleton(BackupManager)
    collaboration_service = providers.Singleton(CollaborationService)
    
    workflow_engine = providers.Singleton(
        WorkflowEngine,
        services=providers.Dict(
            project_manager=project_manager,
            git_sync=git_sync_service,
            ai_update=ai_update_service,
            build=build_service,
            runtime=runtime_service
        )
    )
    
    # --- Extreme Power 2026 Services ---
    from services.devops.iac_engine import AutonomousIaCEngine
    from services.monitoring.cost_pilot import AICostPilot
    from services.security.red_team_ai import RedTeamAI
    
    iac_engine = providers.Singleton(AutonomousIaCEngine, orchestrator=orchestrator)
    cost_pilot = providers.Singleton(AICostPilot, monitoring_service=monitoring_service)
    red_team_ai = providers.Singleton(RedTeamAI, orchestrator=orchestrator)
    
    # --- Next-Gen Core 2026+ Services ---
    from core.messaging.bus import MessageBus
    from services.monitoring.calt_service import CALTLogger
    
    message_bus = providers.Singleton(MessageBus)
    calt_logger = providers.Singleton(CALTLogger)
    
    # --- Hyper-Intelligence 2026 Final ---
    from core.memory.knowledge_graph import KnowledgeGraphService
    from services.security.quantum_vault import QuantumVaultService
    
    knowledge_graph = providers.Singleton(KnowledgeGraphService)
    quantum_vault = providers.Singleton(QuantumVaultService, orchestrator=orchestrator)
    
    # --- Strategic 20/20 Refinements ---
    from services.mcp.bridge import MCPBridge
    mcp_bridge = providers.Singleton(MCPBridge, orchestrator=orchestrator)

# Global container instance
container = Container()

def setup_container():
    """Configure the container with environment variables."""
    container.config.database.redis_url.from_env("REDIS_URL", "redis://localhost:6379")
    container.config.database.postgres_url.from_env("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost/ai_orchestrator")
    
    # Initialize the actual db_manager (singleton)
    # This might be redundant if we use the one from container, 
    # but the spec uses a global db_manager.
    db_manager.initialize(container.config.database.postgres_url())
    
    return container
