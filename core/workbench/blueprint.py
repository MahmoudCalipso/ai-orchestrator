"""
Docker Workbench Blueprint Registry
Defines base images and configurations for all supported tech stacks
"""
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class WorkbenchBlueprint:
    """Configuration for a technology stack workbench"""
    name: str
    base_image: str
    runtime_version: str
    package_manager: str
    build_command: str
    run_command: str
    default_port: int
    manifest_files: List[str]
    extensions: List[str]

class BlueprintRegistry:
    """Registry of all supported tech stack blueprints"""
    
    BLUEPRINTS: Dict[str, WorkbenchBlueprint] = {
        # Backend Stacks
        "java-21": WorkbenchBlueprint(
            name="Java 21 + Maven",
            base_image="openjdk:21-slim",
            runtime_version="21",
            package_manager="mvn",
            build_command="mvn clean package",
            run_command="java -jar target/*.jar",
            default_port=8080,
            manifest_files=["pom.xml", "build.gradle"],
            extensions=[".java"]
        ),
        "java-17-spring": WorkbenchBlueprint(
            name="Java 17 Spring Boot",
            base_image="openjdk:17-slim",
            runtime_version="17",
            package_manager="mvn",
            build_command="mvn spring-boot:run",
            run_command="java -jar target/*.jar",
            default_port=8080,
            manifest_files=["pom.xml"],
            extensions=[".java"]
        ),
        "dotnet-9": WorkbenchBlueprint(
            name=".NET 9",
            base_image="mcr.microsoft.com/dotnet/sdk:9.0",
            runtime_version="9.0",
            package_manager="dotnet",
            build_command="dotnet build",
            run_command="dotnet run",
            default_port=5000,
            manifest_files=["*.csproj", "*.sln"],
            extensions=[".cs"]
        ),
        "dotnet-8": WorkbenchBlueprint(
            name=".NET 8",
            base_image="mcr.microsoft.com/dotnet/sdk:8.0",
            runtime_version="8.0",
            package_manager="dotnet",
            build_command="dotnet build",
            run_command="dotnet run",
            default_port=5000,
            manifest_files=["*.csproj"],
            extensions=[".cs"]
        ),
        "go-1.22": WorkbenchBlueprint(
            name="Go 1.22",
            base_image="golang:1.22-alpine",
            runtime_version="1.22",
            package_manager="go",
            build_command="go build -o app .",
            run_command="./app",
            default_port=8080,
            manifest_files=["go.mod", "go.sum"],
            extensions=[".go"]
        ),
        "python-3.12": WorkbenchBlueprint(
            name="Python 3.12",
            base_image="python:3.12-slim",
            runtime_version="3.12",
            package_manager="pip",
            build_command="pip install -r requirements.txt",
            run_command="python main.py",
            default_port=8000,
            manifest_files=["requirements.txt", "pyproject.toml", "setup.py"],
            extensions=[".py"]
        ),
        "python-3.11-fastapi": WorkbenchBlueprint(
            name="Python 3.11 FastAPI",
            base_image="python:3.11-slim",
            runtime_version="3.11",
            package_manager="pip",
            build_command="pip install -r requirements.txt",
            run_command="uvicorn main:app --host 0.0.0.0 --port 8000",
            default_port=8000,
            manifest_files=["requirements.txt"],
            extensions=[".py"]
        ),
        "node-20": WorkbenchBlueprint(
            name="Node.js 20",
            base_image="node:20-alpine",
            runtime_version="20",
            package_manager="npm",
            build_command="npm install && npm run build",
            run_command="npm start",
            default_port=3000,
            manifest_files=["package.json"],
            extensions=[".js", ".ts"]
        ),
        "rust-1.75": WorkbenchBlueprint(
            name="Rust 1.75",
            base_image="rust:1.75-alpine",
            runtime_version="1.75",
            package_manager="cargo",
            build_command="cargo build --release",
            run_command="./target/release/app",
            default_port=8080,
            manifest_files=["Cargo.toml"],
            extensions=[".rs"]
        ),
        
        # Frontend Stacks
        "angular-18": WorkbenchBlueprint(
            name="Angular 18",
            base_image="node:20-alpine",
            runtime_version="18",
            package_manager="npm",
            build_command="npm install && npm run build",
            run_command="npm start",
            default_port=4200,
            manifest_files=["package.json", "angular.json"],
            extensions=[".ts", ".html", ".css"]
        ),
        "react-18": WorkbenchBlueprint(
            name="React 18",
            base_image="node:20-alpine",
            runtime_version="18",
            package_manager="npm",
            build_command="npm install && npm run build",
            run_command="npm start",
            default_port=3000,
            manifest_files=["package.json"],
            extensions=[".jsx", ".tsx"]
        ),
        "vue-3": WorkbenchBlueprint(
            name="Vue 3",
            base_image="node:20-alpine",
            runtime_version="3",
            package_manager="npm",
            build_command="npm install && npm run build",
            run_command="npm run dev",
            default_port=5173,
            manifest_files=["package.json", "vite.config.js"],
            extensions=[".vue"]
        ),
        
        # Mobile Stacks
        "flutter-3.16": WorkbenchBlueprint(
            name="Flutter 3.16",
            base_image="cirrusci/flutter:3.16.0",
            runtime_version="3.16.0",
            package_manager="flutter",
            build_command="flutter pub get && flutter build web",
            run_command="flutter run -d web-server --web-port=8080",
            default_port=8080,
            manifest_files=["pubspec.yaml"],
            extensions=[".dart"]
        ),
        "react-native": WorkbenchBlueprint(
            name="React Native",
            base_image="node:20-alpine",
            runtime_version="0.73",
            package_manager="npm",
            build_command="npm install",
            run_command="npm start",
            default_port=8081,
            manifest_files=["package.json", "app.json"],
            extensions=[".jsx", ".tsx"]
        ),
        
        # Desktop Stacks
        "electron": WorkbenchBlueprint(
            name="Electron",
            base_image="node:20-alpine",
            runtime_version="28",
            package_manager="npm",
            build_command="npm install && npm run build",
            run_command="npm start",
            default_port=3000,
            manifest_files=["package.json"],
            extensions=[".js", ".ts"]
        ),
        "tauri": WorkbenchBlueprint(
            name="Tauri",
            base_image="rust:1.75-alpine",
            runtime_version="1.5",
            package_manager="cargo",
            build_command="cargo tauri build",
            run_command="cargo tauri dev",
            default_port=1420,
            manifest_files=["Cargo.toml", "tauri.conf.json"],
            extensions=[".rs", ".ts"]
        )
    }
    
    @classmethod
    def get_blueprint(cls, stack: str) -> WorkbenchBlueprint:
        """Get blueprint by stack name"""
        return cls.BLUEPRINTS.get(stack)
    
    @classmethod
    def list_stacks(cls) -> List[str]:
        """List all available stacks"""
        return list(cls.BLUEPRINTS.keys())
    
    @classmethod
    def detect_stack_from_manifest(cls, manifest_file: str) -> str:
        """Detect stack from manifest filename"""
        for stack, blueprint in cls.BLUEPRINTS.items():
            if any(manifest_file.endswith(mf.replace("*", "")) for mf in blueprint.manifest_files):
                return stack
        return None
