"""
Universal Project Scanner Agent
The "X-Ray" - Manifest-based project analysis
"""
import os
import json
import logging
from typing import Dict, Any, List, Optional
from agents.base import BaseAgent
from core.workbench.blueprint import BlueprintRegistry

logger = logging.getLogger(__name__)

class UniversalProjectMap:
    """Structured representation of a project's architecture"""
    
    def __init__(self):
        self.source_stack: Optional[str] = None
        self.source_version: Optional[str] = None
        self.target_stack: Optional[str] = None
        self.target_version: Optional[str] = None
        self.manifest_files: List[str] = []
        self.dependencies: List[Dict[str, str]] = []
        self.entry_points: List[str] = []
        self.file_structure: Dict[str, Any] = {}
        self.migration_complexity: str = "unknown"
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": {
                "stack": self.source_stack,
                "version": self.source_version
            },
            "target": {
                "stack": self.target_stack,
                "version": self.target_version
            },
            "manifests": self.manifest_files,
            "dependencies": self.dependencies,
            "entry_points": self.entry_points,
            "structure": self.file_structure,
            "complexity": self.migration_complexity
        }

class ProjectScannerAgent(BaseAgent):
    """Universal project scanner - detects any tech stack"""
    
    def __init__(self, orchestrator=None):
        super().__init__(
            name="ProjectScanner",
            role="Universal X-Ray Agent",
            system_prompt="""You are a Universal Project Scanner.
            Your job is to analyze any codebase and identify its technology stack
            by examining manifest files, not file extensions.
            You produce a Universal Project Map."""
        )
        self.orchestrator = orchestrator
        self.blueprint_registry = BlueprintRegistry()
    
    async def act(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Scan a project directory and generate Universal Project Map"""
        project_path = context.get("project_path") if context else None
        if not project_path:
            return {"error": "No project_path provided"}
        
        logger.info(f"Scanning project at: {project_path}")
        
        project_map = await self.scan_project(project_path)
        
        return {
            "status": "success",
            "project_map": project_map.to_dict()
        }
    
    async def scan_project(self, project_path: str) -> UniversalProjectMap:
        """Deep scan of project directory"""
        project_map = UniversalProjectMap()
        
        # Step 1: Find all manifest files
        manifests = self._find_manifests(project_path)
        project_map.manifest_files = manifests
        
        # Step 2: Detect stack from manifests
        detected_stack = self._detect_stack(manifests)
        project_map.source_stack = detected_stack
        
        # Step 3: Parse manifest for version and dependencies
        if detected_stack:
            await self._parse_manifest_details(project_path, manifests, project_map)
        
        # Step 4: Analyze file structure
        project_map.file_structure = self._analyze_structure(project_path)
        
        # Step 5: Find entry points
        project_map.entry_points = self._find_entry_points(project_path, detected_stack)
        
        # Step 6: Estimate complexity
        project_map.migration_complexity = self._estimate_complexity(project_map)
        
        # Step 7: Index files for Semantic RAG
        await self._index_project_files(project_path)
        
        return project_map
    
    def _find_manifests(self, project_path: str) -> List[str]:
        """Find all manifest files in project"""
        manifests = []
        manifest_patterns = [
            "pom.xml", "build.gradle", "*.csproj", "*.sln",
            "go.mod", "Cargo.toml", "package.json", "requirements.txt",
            "pyproject.toml", "pubspec.yaml", "angular.json", "tauri.conf.json"
        ]
        
        for root, dirs, files in os.walk(project_path):
            for file in files:
                for pattern in manifest_patterns:
                    if pattern.startswith("*"):
                        if file.endswith(pattern[1:]):
                            manifests.append(os.path.join(root, file))
                    elif file == pattern:
                        manifests.append(os.path.join(root, file))
        
        return manifests
    
    def _detect_stack(self, manifests: List[str]) -> Optional[str]:
        """Detect technology stack from manifest files"""
        for manifest in manifests:
            basename = os.path.basename(manifest)
            
            # Java
            if basename == "pom.xml":
                return "java-21"
            if basename == "build.gradle":
                return "java-21"
            
            # .NET
            if basename.endswith(".csproj"):
                return "dotnet-9"
            if basename.endswith(".sln"):
                return "dotnet-9"
            
            # Go
            if basename == "go.mod":
                return "go-1.22"
            
            # Python
            if basename == "requirements.txt":
                return "python-3.12"
            if basename == "pyproject.toml":
                return "python-3.12"
            
            # Node/JavaScript
            if basename == "package.json":
                # Need to check content for Angular/React/Vue
                return "node-20"
            
            # Flutter
            if basename == "pubspec.yaml":
                return "flutter-3.16"
            
            # Rust
            if basename == "Cargo.toml":
                return "rust-1.75"
        
        return None
    
    async def _parse_manifest_details(
        self,
        project_path: str,
        manifests: List[str],
        project_map: UniversalProjectMap
    ):
        """Parse manifest files for version and dependencies"""
        for manifest in manifests:
            basename = os.path.basename(manifest)
            
            try:
                if basename == "package.json":
                    await self._parse_package_json(manifest, project_map)
                elif basename == "pom.xml":
                    await self._parse_pom_xml(manifest, project_map)
                elif basename == "requirements.txt":
                    await self._parse_requirements_txt(manifest, project_map)
                elif basename == "pubspec.yaml":
                    await self._parse_pubspec_yaml(manifest, project_map)
            except Exception as e:
                logger.warning(f"Failed to parse {manifest}: {e}")
    
    async def _parse_package_json(self, path: str, project_map: UniversalProjectMap):
        """Parse package.json for Node/Angular/React"""
        with open(path, 'r') as f:
            data = json.load(f)
            
        # Detect framework
        deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
        
        if "@angular/core" in deps:
            project_map.source_stack = "angular-18"
            project_map.source_version = deps.get("@angular/core", "unknown")
        elif "react" in deps:
            project_map.source_stack = "react-18"
            project_map.source_version = deps.get("react", "unknown")
        elif "vue" in deps:
            project_map.source_stack = "vue-3"
            project_map.source_version = deps.get("vue", "unknown")
        
        # Extract dependencies
        for dep, version in deps.items():
            project_map.dependencies.append({"name": dep, "version": version})
    
    async def _parse_pom_xml(self, path: str, project_map: UniversalProjectMap):
        """Parse pom.xml for Java version and dependencies"""
        # Simplified - would use XML parser in production
        with open(path, 'r') as f:
            content = f.read()
            
        if "<java.version>21</java.version>" in content:
            project_map.source_version = "21"
        elif "<java.version>17</java.version>" in content:
            project_map.source_version = "17"
    
    async def _parse_requirements_txt(self, path: str, project_map: UniversalProjectMap):
        """Parse requirements.txt for Python dependencies"""
        with open(path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    parts = line.split("==")
                    name = parts[0]
                    version = parts[1] if len(parts) > 1 else "latest"
                    project_map.dependencies.append({"name": name, "version": version})
    
    async def _parse_pubspec_yaml(self, path: str, project_map: UniversalProjectMap):
        """Parse pubspec.yaml for Flutter"""
        # Would use YAML parser in production
        with open(path, 'r') as f:
            content = f.read()
            if "flutter:" in content:
                project_map.source_stack = "flutter-3.16"
    
    def _analyze_structure(self, project_path: str) -> Dict[str, Any]:
        """Analyze directory structure"""
        structure = {
            "total_files": 0,
            "directories": [],
            "file_types": {}
        }
        
        for root, dirs, files in os.walk(project_path):
            structure["total_files"] += len(files)
            structure["directories"].extend(dirs)
            
            for file in files:
                ext = os.path.splitext(file)[1]
                structure["file_types"][ext] = structure["file_types"].get(ext, 0) + 1
        
        return structure
    
    def _find_entry_points(self, project_path: str, stack: Optional[str]) -> List[str]:
        """Find main entry points based on stack"""
        entry_points = []
        
        common_entries = [
            "main.py", "app.py", "index.js", "main.ts",
            "Main.java", "Program.cs", "main.go", "main.dart"
        ]
        
        for root, dirs, files in os.walk(project_path):
            for file in files:
                if file in common_entries:
                    entry_points.append(os.path.join(root, file))
        
        return entry_points
    
    def _estimate_complexity(self, project_map: UniversalProjectMap) -> str:
        """Estimate migration complexity"""
        total_files = project_map.file_structure.get("total_files", 0)
        dep_count = len(project_map.dependencies)
        
        if total_files < 50 and dep_count < 10:
            return "low"
        elif total_files < 200 and dep_count < 30:
            return "medium"
        else:
            return "high"
    async def _index_project_files(self, project_path: str):
        """Index all source files for semantic search"""
        try:
            from core.memory.vector_store import VectorStoreService
            vector_store = VectorStoreService()
            
            all_files = []
            for root, _, files in os.walk(project_path):
                # Ignore common junk and internal directories
                if any(ignored in root for ignored in ['.git', '__pycache__', 'node_modules', '.venv', '.gemini']):
                    continue
                for file in files:
                    # Ignore common non-source/large files
                    if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.pdf', '.zip', '.exe')):
                        continue
                    all_files.append(os.path.join(root, file))
            
            logger.info(f"Indexing {len(all_files)} files for project at {project_path}")
            # Run in a separate thread if needed, but for now we'll do it sequentially
            # since indexing can be slow
            vector_store.index_files(all_files)
            logger.info(f"Successfully indexed project context for {project_path}")
        except Exception as e:
            logger.error(f"Failed to index project files: {e}")
