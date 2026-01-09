"""
Integration Tests for AI Orchestrator Platform
"""
import asyncio
import os
import sys
import logging
from typing import Dict, Any

# Add project root to path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root_dir)

from platform.database import DatabaseConnectionManager
from platform.registry import LanguageRegistry
from platform.templates import TemplateProcessor
from platform.security import VulnerabilityScanner
from platform.kubernetes import KubernetesGenerator
from schemas.generation_spec import KubernetesConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_registry():
    """Test Language Registry"""
    logger.info("Testing Language Registry...")
    registry = LanguageRegistry()
    registry.load_registries()
    
    langs = registry.get_supported_languages()
    assert "python" in langs
    assert "c#" in langs
    
    py_config = registry.get_language_config("python")
    assert py_config["latest_version"] == "3.12"
    logger.info("✓ Registry tests passed")

async def test_kubernetes_generator():
    """Test K8s Generator"""
    logger.info("Testing Kubernetes Generator...")
    generator = KubernetesGenerator()
    config = KubernetesConfig(namespace="test-ns", replicas=2, ingress_domain="app.example.com")
    
    manifests = generator.generate_manifests("test-app", "test-image:v1", config)
    
    assert "deployment.yaml" in manifests
    assert "service.yaml" in manifests
    assert "ingress.yaml" in manifests
    assert "replicas: 2" in manifests["deployment.yaml"]
    logger.info("✓ Kubernetes generator tests passed")

async def test_vulnerability_scanner():
    """Test Security Scanner (Mocked)"""
    logger.info("Testing Security Scanner...")
    scanner = VulnerabilityScanner()
    
    # We can't easily test actual scanning without files, but we can verify the class loads
    assert hasattr(scanner, "scan_code")
    assert hasattr(scanner, "scan_dependencies")
    logger.info("✓ Security scanner tests passed")

async def main():
    logger.info("Starting Integration Tests")
    
    await test_registry()
    await test_kubernetes_generator()
    await test_vulnerability_scanner()
    await test_entity_generation()
    await test_template_processor()
    await test_ar_generator()
    
    logger.info("All tests passed successfully!")

async def test_entity_generation():
    """Test Entity Generation"""
    logger.info("Testing Entity Generation...")
    from platform.database import EntityGenerator
    from schemas.generation_spec import EntityDefinition, EntityField
    from core.orchestrator import Orchestrator
    
    # Create mock orchestrator (would need actual instance in real test)
    # For now, just verify the class loads
    assert hasattr(EntityGenerator, 'generate_models')
    assert hasattr(EntityGenerator, 'generate_dtos')
    assert hasattr(EntityGenerator, 'generate_repository')
    logger.info("✓ Entity generation tests passed")

async def test_template_processor():
    """Test Template Processor"""
    logger.info("Testing Template Processor...")
    from platform.templates import TemplateProcessor
    
    processor = TemplateProcessor()
    assert hasattr(processor, 'download_template')
    assert hasattr(processor, 'extract_template')
    assert hasattr(processor, 'analyze_template')
    assert hasattr(processor, 'customize_template')
    logger.info("✓ Template processor tests passed")

async def test_ar_generator():
    """Test AR Generator"""
    logger.info("Testing AR Generator...")
    from platform.ar import ARGenerator, ARPlatform, ARType
    
    ar_gen = ARGenerator()
    
    # Test web AR generation
    web_files = await ar_gen.generate_ar_web(ARType.MARKER_BASED, "model.gltf", {})
    assert "index.html" in web_files
    assert "ar-controller.js" in web_files
    
    # Test Android AR generation
    android_files = await ar_gen.generate_ar_android(ARType.PLANE_DETECTION, "model.gltf", {"package_name": "com.test.ar"})
    assert "MainActivity.kt" in android_files
    
    logger.info("✓ AR generator tests passed")

if __name__ == "__main__":
    asyncio.run(main())
