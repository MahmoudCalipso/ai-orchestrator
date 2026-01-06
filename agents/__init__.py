"""
Agents Module
=============

This module provides specialized agents for various orchestration tasks.

Available Agents:
----------------
- CreateAgent: Create and configure new AI agents
- MigrationAgent: Migrate tasks between models and runtimes
- AuditAgent: Comprehensive auditing and compliance monitoring
- TestAgent: Automated testing and validation

Usage:
------
    from agents import CreateAgent, MigrationAgent, AuditAgent, TestAgent
    from core.orchestrator import Orchestrator

    # Initialize orchestrator
    orchestrator = Orchestrator()
    await orchestrator.initialize()

    # Create Agent - Design new agents
    create_agent = CreateAgent(orchestrator)
    config = await create_agent.create_agent_config(
        name="code-assistant",
        purpose="Code generation and review",
        capabilities=["python", "javascript", "code_review"]
    )

    # Migration Agent - Move tasks between models
    migration_agent = MigrationAgent(orchestrator)
    result = await migration_agent.migrate_task(
        task_id="task-123",
        target_model="qwen2.5",
        target_runtime="vllm"
    )

    # Audit Agent - Track and audit system activity
    audit_agent = AuditAgent(orchestrator)
    await audit_agent.log_inference_request(
        user="john",
        request_id="req-456",
        model="mistral",
        task_type="chat",
        prompt_length=100,
        status="success"
    )
    report = await audit_agent.generate_audit_report()

    # Test Agent - Automated testing
    test_agent = TestAgent(orchestrator)
    health = await test_agent.run_health_check()
    integration = await test_agent.run_integration_tests()
    benchmark = await test_agent.benchmark_performance(num_requests=10)

Agent Lifecycle:
---------------
1. Initialize orchestrator
2. Create agent instance
3. Call agent methods
4. Process results
5. Cleanup (if needed)

Best Practices:
--------------
- Reuse agent instances when possible
- Handle exceptions from agent operations
- Review audit logs regularly
- Run tests before deployment
- Monitor migration patterns
"""

from .create_agent import CreateAgent
from .migrate_agent import MigrationAgent
from .audit_agent import AuditAgent
from .test_agent import TestAgent

# Version
__version__ = "1.0.0"

# Public API
__all__ = [
    'CreateAgent',
    'MigrationAgent',
    'AuditAgent',
    'TestAgent',
]

# Agent registry for dynamic loading
AGENT_REGISTRY = {
    'create': CreateAgent,
    'migrate': MigrationAgent,
    'audit': AuditAgent,
    'test': TestAgent,
}


def get_agent(agent_name: str, orchestrator):
    """
    Factory function to get an agent instance by name.

    Args:
        agent_name: Name of the agent ('create', 'migrate', 'audit', 'test')
        orchestrator: Orchestrator instance

    Returns:
        Agent instance

    Raises:
        ValueError: If agent name is not recognized

    Example:
        >>> from core.orchestrator import Orchestrator
        >>> orch = Orchestrator()
        >>> await orch.initialize()
        >>> agent = get_agent('test', orch)
        >>> results = await agent.run_health_check()
    """
    if agent_name not in AGENT_REGISTRY:
        available = ', '.join(AGENT_REGISTRY.keys())
        raise ValueError(
            f"Unknown agent '{agent_name}'. "
            f"Available agents: {available}"
        )

    agent_class = AGENT_REGISTRY[agent_name]
    return agent_class(orchestrator)


def list_available_agents() -> list:
    """
    List all available agent names.

    Returns:
        List of agent names

    Example:
        >>> agents = list_available_agents()
        >>> print(agents)
        ['create', 'migrate', 'audit', 'test']
    """
    return list(AGENT_REGISTRY.keys())


# Agent metadata
AGENT_METADATA = {
    'create': {
        'name': 'Create Agent',
        'description': 'Create and configure new AI agents',
        'capabilities': [
            'agent_design',
            'configuration_generation',
            'model_recommendation',
            'parameter_optimization'
        ],
        'use_cases': [
            'Designing specialized agents',
            'Configuring agent parameters',
            'Testing agent configurations'
        ],
    },
    'migrate': {
        'name': 'Migration Agent',
        'description': 'Migrate tasks between models and runtimes',
        'capabilities': [
            'task_migration',
            'state_preservation',
            'checkpoint_management',
            'pattern_analysis'
        ],
        'use_cases': [
            'Moving to faster models',
            'Switching runtimes for better performance',
            'Load balancing across resources',
            'Analyzing migration patterns'
        ],
    },
    'audit': {
        'name': 'Audit Agent',
        'description': 'Comprehensive auditing and compliance',
        'capabilities': [
            'event_logging',
            'compliance_checking',
            'report_generation',
            'anomaly_detection',
            'log_export'
        ],
        'use_cases': [
            'Security auditing',
            'Compliance monitoring',
            'Activity tracking',
            'Forensic analysis'
        ],
    },
    'test': {
        'name': 'Test Agent',
        'description': 'Automated testing and validation',
        'capabilities': [
            'health_checks',
            'integration_tests',
            'performance_benchmarks',
            'validation_tests'
        ],
        'use_cases': [
            'System health monitoring',
            'Pre-deployment testing',
            'Performance analysis',
            'Regression testing'
        ],
    },
}


def get_agent_info(agent_name: str) -> dict:
    """
    Get metadata about an agent.

    Args:
        agent_name: Name of the agent

    Returns:
        Agent metadata dictionary or None if not found

    Example:
        >>> info = get_agent_info('audit')
        >>> print(info['description'])
        'Comprehensive auditing and compliance'
        >>> print(info['capabilities'])
        ['event_logging', 'compliance_checking', ...]
    """
    return AGENT_METADATA.get(agent_name)


# Utility functions for common agent workflows

async def quick_audit_report(orchestrator, start_time=None, end_time=None):
    """
    Generate a quick audit report.

    Args:
        orchestrator: Orchestrator instance
        start_time: Start time for report (optional)
        end_time: End time for report (optional)

    Returns:
        Audit report dictionary

    Example:
        >>> report = await quick_audit_report(orchestrator)
        >>> print(report['summary']['total_events'])
    """
    audit_agent = AuditAgent(orchestrator)
    return await audit_agent.generate_audit_report(start_time, end_time)


async def quick_health_check(orchestrator):
    """
    Run a quick health check on the system.

    Args:
        orchestrator: Orchestrator instance

    Returns:
        Health check results

    Example:
        >>> health = await quick_health_check(orchestrator)
        >>> print(health['overall_status'])
        'healthy'
    """
    test_agent = TestAgent(orchestrator)
    return await test_agent.run_health_check()


async def quick_benchmark(orchestrator, num_requests: int = 5):
    """
    Run a quick performance benchmark.

    Args:
        orchestrator: Orchestrator instance
        num_requests: Number of test requests

    Returns:
        Benchmark results

    Example:
        >>> results = await quick_benchmark(orchestrator, 10)
        >>> print(results['statistics']['avg_processing_time'])
    """
    test_agent = TestAgent(orchestrator)
    return await test_agent.benchmark_performance(num_requests)


async def quick_migration(
    orchestrator,
    task_id: str,
    target_model: str = None,
    target_runtime: str = None
):
    """
    Quickly migrate a task.

    Args:
        orchestrator: Orchestrator instance
        task_id: Task ID to migrate
        target_model: Target model name (optional)
        target_runtime: Target runtime name (optional)

    Returns:
        Migration result

    Example:
        >>> result = await quick_migration(
        ...     orchestrator,
        ...     'task-123',
        ...     target_model='qwen2.5'
        ... )
        >>> print(result['status'])
    """
    migration_agent = MigrationAgent(orchestrator)
    return await migration_agent.migrate_task(
        task_id,
        target_model,
        target_runtime
    )


# Agent workflow helpers

class AgentWorkflow:
    """
    Helper class for orchestrating multiple agents.

    Example:
        >>> workflow = AgentWorkflow(orchestrator)
        >>>
        >>> # Run complete system check
        >>> results = await workflow.full_system_check()
        >>>
        >>> # Create and test new agent
        >>> config = await workflow.create_and_test_agent(
        ...     name="translator",
        ...     purpose="Language translation"
        ... )
    """

    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.create_agent = CreateAgent(orchestrator)
        self.migration_agent = MigrationAgent(orchestrator)
        self.audit_agent = AuditAgent(orchestrator)
        self.test_agent = TestAgent(orchestrator)

    async def full_system_check(self):
        """Run comprehensive system check"""
        return {
            'health': await self.test_agent.run_health_check(),
            'integration': await self.test_agent.run_integration_tests(),
            'compliance': await self.audit_agent.check_compliance()
        }

    async def create_and_test_agent(self, name: str, purpose: str, capabilities: list):
        """Create agent and test it"""
        config = await self.create_agent.create_agent_config(
            name, purpose, capabilities
        )
        test_result = await self.create_agent.test_agent(config)

        return {
            'config': config,
            'test_result': test_result
        }

    async def migration_with_audit(self, task_id: str, target_model: str):
        """Migrate task and log to audit"""
        result = await self.migration_agent.migrate_task(
            task_id, target_model
        )

        await self.audit_agent.log_event(
            event_type="migration",
            user="system",
            action="migrate_task",
            resource=task_id,
            status=result['status'],
            details=result
        )

        return result


# Export workflow helper
__all__.append('AgentWorkflow')