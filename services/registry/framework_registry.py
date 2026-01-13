"""
Enhanced Language and Framework Registry with Version Management
Tracks framework versions, SDKs, JDKs, and best practices
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import aiohttp
from pydantic import BaseModel


class FrameworkVersion(BaseModel):
    """Framework version information"""
    name: str
    version: str
    latest_version: str
    release_date: Optional[str] = None
    is_lts: bool = False
    is_deprecated: bool = False


class LanguageSpec(BaseModel):
    """Enhanced language specification"""
    language: str
    framework: str
    version: str
    architecture: str  # MVP, MVC, MVVM, Clean Architecture, Hexagonal, etc.
    sdk: Optional[str] = None  # For .NET
    jdk: Optional[str] = None  # For Java
    best_practices: List[str] = []
    required_packages: List[str] = []


from services.database.base import SessionLocal
from services.registry.persistence import FrameworkMetadata
from sqlalchemy import select, update, insert

class FrameworkRegistry:
    """Registry for framework versions and metadata with DB persistence"""
    
    def __init__(self):
        self.frameworks: Dict[str, Dict[str, Any]] = {}
        self.last_updated: Optional[datetime] = None
        self._initialize_from_db()
    
    def _initialize_from_db(self):
        """Load framework data from database or initialize with defaults"""
        with SessionLocal() as db:
            # Check if we have any data
            results = db.execute(select(FrameworkMetadata)).scalars().all()
            
            if not results:
                logger.info("Initializing Framework Registry with default 2026 metadata...")
                self._load_defaults()
                self._save_to_db()
            else:
                logger.info(f"Loading {len(results)} frameworks from database")
                for item in results:
                    lang = item.language
                    fw = item.framework
                    
                    if lang not in self.frameworks:
                        self.frameworks[lang] = {}
                        
                    self.frameworks[lang][fw] = {
                        "latest_version": item.latest_version,
                        "lts_version": item.lts_version,
                        "versions": item.versions,
                        "architectures": item.architectures,
                        "best_practices": item.best_practices,
                        "required_packages": item.required_packages
                    }
                    if not self.last_updated or (item.last_updated and item.last_updated > self.last_updated):
                        self.last_updated = item.last_updated

    def _load_defaults(self):
        """Set default framework metadata"""
        self.frameworks = {
            # Python Frameworks
            "python": {
                "django": {
                    "latest_version": "5.1.4",
                    "lts_version": "5.1.x",
                    "versions": ["5.1.4", "5.0.1", "4.2.17"],
                    "architectures": ["MVT", "Clean Architecture", "Hexagonal", "AIOPS-Pattern"],
                    "best_practices": [
                        "Use Django REST Framework 4.0 (2025 Edition)",
                        "Implement custom user model with MFA support",
                        "Use environment variables for settings (python-dotenv 2026)",
                        "Enable CORS and CSP headers properly",
                        "Use Django ORM with Async support",
                        "Implement proper authentication (OIDC/JWT)",
                        "Use Django migrations with zero-downtime strategies"
                    ],
                    "required_packages": [
                        "django",
                        "djangorestframework",
                        "django-cors-headers",
                        "psycopg-binary",
                        "django-filter",
                        "drf-spectacular",
                        "celery",
                        "redis"
                    ]
                },
                "fastapi": {
                    "latest_version": "0.115.6",
                    "versions": ["0.115.6", "0.111.0", "0.109.0"],
                    "architectures": ["Clean Architecture", "Hexagonal", "Repository Pattern", "Micro-Core"],
                    "best_practices": [
                        "Use Pydantic V2.x models for high-performance validation",
                        "Implement advanced Dependency Injection with lifespan events",
                        "Use Python 3.13+ structural pattern matching for routers",
                        "Add complete OpenAPI 3.1 documentation",
                        "Use background tasks or TaskGroups for concurrency",
                        "Integrate with Vector Databases (Chroma/Pinecone) for AI features",
                        "Use SQLAlchemy 2.0+ with modern Mapped types"
                    ],
                    "required_packages": [
                        "fastapi",
                        "uvicorn[standard]",
                        "sqlalchemy>=2.0",
                        "pydantic[email]",
                        "alembic",
                        "python-jose[cryptography]",
                        "passlib[bcrypt]",
                        "redis",
                        "celery"
                    ]
                },
                "flask": {
                    "latest_version": "3.1.0",
                    "versions": ["3.1.0", "3.0.1", "2.3.x"],
                    "architectures": ["MVC", "Blueprint Pattern", "Application Factory"],
                    "best_practices": [
                        "Use application factory pattern for scalability",
                        "Organize with blueprints and modern CLI commands",
                        "Use Flask-SQLAlchemy 3.1+",
                        "Implement Flask-JWT-Extended for secure auth",
                        "Use Flask-Migrate for robust schema management",
                        "Implement proper error handlers and custom response classes"
                    ],
                    "required_packages": [
                        "flask",
                        "flask-sqlalchemy",
                        "flask-migrate",
                        "flask-jwt-extended",
                        "flask-cors",
                        "python-dotenv",
                        "psycopg-binary",
                        "redis"
                    ]
                }
            },
            
            # JavaScript/TypeScript Frameworks
            "javascript": {
                "express": {
                    "latest_version": "5.0.0",
                    "versions": ["5.0.0", "4.19.2", "4.18.x"],
                    "architectures": ["MVC", "Clean Architecture", "Layered", "Micro-services"],
                    "best_practices": [
                        "Use Express 5.0 native Promise support",
                        "Implement Node.js 23.x native test runners",
                        "Use TypeScript 5.7+ for strict type safety",
                        "Implement Zod for runtime schema validation",
                        "Add security headers with Helmet 8.0",
                        "Use Pino for high-performance structured logging"
                    ],
                    "required_packages": [
                        "express",
                        "cors",
                        "helmet",
                        "jsonwebtoken",
                        "bcryptjs",
                        "zod",
                        "pino",
                        "dotenv",
                        "prisma"
                    ]
                },
                "nestjs": {
                    "latest_version": "11.0.0",
                    "versions": ["11.0.0", "10.4.0", "10.3.x"],
                    "architectures": ["Clean Architecture", "CQRS", "Microservices", "Event-Driven"],
                    "best_practices": [
                        "Use NestJS 11 modern dependency injection",
                        "Implement guards and interceptors for cross-cutting concerns",
                        "Use DTOs with Class-Validator 2026 edition",
                        "Follow strictly decoupled module structure",
                        "Use Prisma 6.x or Drizzle for type-safe DB access",
                        "Implement Observability with OpenTelemetry"
                    ],
                    "required_packages": [
                        "@nestjs/core",
                        "@nestjs/common",
                        "@nestjs/jwt",
                        "@nestjs/passport",
                        "prisma",
                        "class-validator",
                        "class-transformer"
                    ]
                }
            },
            
            # Java Frameworks
            "java": {
                "spring_boot": {
                    "latest_version": "3.4.1",
                    "lts_version": "3.4.x",
                    "versions": ["3.4.1", "3.3.0", "3.2.5"],
                    "jdk_versions": ["21", "23", "17"],
                    "recommended_jdk": "21",
                    "architectures": ["Clean Architecture", "Hexagonal", "Stateless", "Reactive"],
                    "best_practices": [
                        "Use Java 21+ Virtual Threads (Project Loom) for high concurrency",
                        "Integrate Spring AI for LLM orchestration",
                        "Implement Spring Security 6.4+ with OIDC/OAuth2",
                        "Use GraalVM native images for instant startup",
                        "Adopt Micrometer 2.0 for advanced metrics",
                        "Use Spring Data JPA 3.x with modern QueryDSL"
                    ],
                    "required_packages": [
                        "spring-boot-starter-web",
                        "spring-boot-starter-data-jpa",
                        "spring-boot-starter-security",
                        "spring-ai-openai-spring-boot-starter",
                        "postgresql",
                        "lombok",
                        "mapstruct"
                    ]
                }
            },
            
            # .NET Frameworks
            "csharp": {
                "aspnet_core": {
                    "latest_version": "9.0.0",
                    "lts_version": "8.0",
                    "versions": ["9.0.0", "8.0.0", "7.0.x"],
                    "sdk_versions": ["9.0.100", "8.0.400"],
                    "recommended_sdk": "9.0.100",
                    "architectures": ["Clean Architecture", "Vertical Slices", "CQRS", "DAPR"],
                    "best_practices": [
                        "Use C# 13 structural improvements and params collections",
                        "Implement Minimal APIs for ultra-fast performance",
                        "Use EF Core 9.0 with JSON column mapping and interceptors",
                        "Apply Resilience patterns with Microsoft.Extensions.Http.Resilience",
                        "Use Scalar or OpenAPI 3.1 for modern documentation",
                        "Implement Native AOT for serverless deployments"
                    ],
                    "required_packages": [
                        "Microsoft.AspNetCore.OpenApi",
                        "Microsoft.EntityFrameworkCore.SqlServer",
                        "Microsoft.Extensions.Http.Resilience",
                        "Scalar.AspNetCore",
                        "MediatR"
                    ]
                }
            },
            
            # Go Frameworks
            "go": {
                "gin": {
                    "latest_version": "1.10.x",
                    "versions": ["1.10.0", "1.9.1"],
                    "architectures": ["Clean Architecture", "Hexagonal", "Domain-Driven"],
                    "best_practices": [
                        "Use Go 1.25+ iterators and modern generics",
                        "Implement structured logging with slog",
                        "Use GORM 2.5+ with automated migrations",
                        "Add request validation with playground/validator v11",
                        "Implement graceful shutdown and context propagation",
                        "Use OIDC for modern authentication"
                    ],
                    "required_packages": [
                        "github.com/gin-gonic/gin",
                        "github.com/golang-jwt/jwt/v5",
                        "gorm.io/gorm",
                        "github.com/joho/godotenv"
                    ]
                }
            },
            
            # Frontend Frameworks
            "frontend": {
                "angular": {
                    "latest_version": "19.1.0",
                    "lts_version": "18.x",
                    "versions": ["19.1.0", "18.2.0", "17.x"],
                    "architectures": ["Component-based", "Signal-based", "Standalone"],
                    "best_practices": [
                        "Use Angular Signals for reactive state management",
                        "Implement Standalone Components and functional routers",
                        "Use Hydration for improved SSR performance",
                        "Adopt modern Control Flow syntax (@if, @for)",
                        "Implement route guards with functional approach",
                        "Use modern deferrable views for lazy loading"
                    ],
                    "required_packages": [
                        "@angular/core",
                        "@angular/common",
                        "@angular/router",
                        "@angular/forms",
                        "@angular/material",
                        "rxjs"
                    ]
                },
                "react": {
                    "latest_version": "19.0.0",
                    "versions": ["19.0.0", "18.3.x"],
                    "architectures": ["Component-based", "Server Components", "Atomic Design"],
                    "best_practices": [
                        "Use React Server Components (RSC) where applicable",
                        "Implement simplified Actions and the 'use' hook",
                        "Use TanStack Query V6 for stateful data fetching",
                        "Adopt Zustand 5.x for lightweight global state",
                        "Implement strict TypeScript 5.x patterns",
                        "Use shadcn/ui for consistent design system"
                    ],
                    "required_packages": [
                        "react",
                        "react-dom",
                        "react-router-dom",
                        "@tanstack/react-query",
                        "zustand",
                        "zod"
                    ]
                },
                "vue": {
                    "latest_version": "3.5.x",
                    "versions": ["3.5.0", "3.4.15"],
                    "architectures": ["Composition API", "SFC", "Script Setup"],
                    "best_practices": [
                        "Use Composition API with <script setup>",
                        "Implement Pinia for modern state management",
                        "Use Vite 6.x for lightning-fast HMR",
                        "Adopt Vue Router 4.x functional navigation",
                        "Use Volar for enhanced TS support",
                        "Implement specialized composables for logic reuse"
                    ],
                    "required_packages": [
                        "vue",
                        "vue-router",
                        "pinia",
                        "axios",
                        "vee-validate"
                    ]
                }
            }
        }

    def _save_to_db(self):
        """Save current framework metadata to database"""
        with SessionLocal() as db:
            for lang, frameworks in self.frameworks.items():
                for fw_name, info in frameworks.items():
                    # Check if exists
                    existing = db.execute(
                        select(FrameworkMetadata).where(
                            FrameworkMetadata.language == lang,
                            FrameworkMetadata.framework == fw_name
                        )
                    ).scalar_one_or_none()
                    
                    if existing:
                        db.execute(
                            update(FrameworkMetadata).where(
                                FrameworkMetadata.language == lang,
                                FrameworkMetadata.framework == fw_name
                            ).values(
                                latest_version=info.get("latest_version"),
                                lts_version=info.get("lts_version"),
                                versions=info.get("versions"),
                                architectures=info.get("architectures"),
                                best_practices=info.get("best_practices"),
                                required_packages=info.get("required_packages"),
                                last_updated=datetime.utcnow()
                            )
                        )
                    else:
                        db.execute(
                            insert(FrameworkMetadata).values(
                                language=lang,
                                framework=fw_name,
                                latest_version=info.get("latest_version"),
                                lts_version=info.get("lts_version"),
                                versions=info.get("versions"),
                                architectures=info.get("architectures"),
                                best_practices=info.get("best_practices"),
                                required_packages=info.get("required_packages"),
                                last_updated=datetime.utcnow()
                            )
                        )
            db.commit()
            logger.info("Saved framework metadata to database")
    
    def get_framework_info(
        self,
        language: str,
        framework: str
    ) -> Optional[Dict[str, Any]]:
        """Get framework information"""
        lang_frameworks = self.frameworks.get(language.lower(), {})
        return lang_frameworks.get(framework.lower())
    
    def get_recommended_version(
        self,
        language: str,
        framework: str,
        prefer_lts: bool = False
    ) -> Optional[str]:
        """Get recommended framework version"""
        info = self.get_framework_info(language, framework)
        if not info:
            return None
        
        if prefer_lts and "lts_version" in info:
            return info["lts_version"]
        
        return info.get("latest_version")
    
    def get_required_packages(
        self,
        language: str,
        framework: str,
        database: Optional[str] = None
    ) -> List[str]:
        """Get required packages for framework"""
        info = self.get_framework_info(language, framework)
        if not info:
            return []
        
        packages = info.get("required_packages", []).copy()
        
        # Add database-specific packages
        if database:
            db_packages = self._get_database_packages(language, database)
            packages.extend(db_packages)
        
        return list(set(packages))  # Remove duplicates
    
    def _get_database_packages(
        self,
        language: str,
        database: str
    ) -> List[str]:
        """Get database-specific packages"""
        db_map = {
            "python": {
                "postgresql": ["psycopg2-binary", "asyncpg"],
                "mysql": ["mysqlclient", "aiomysql"],
                "mongodb": ["pymongo", "motor"],
                "redis": ["redis", "aioredis"]
            },
            "javascript": {
                "postgresql": ["pg"],
                "mysql": ["mysql2"],
                "mongodb": ["mongoose"],
                "redis": ["redis"]
            },
            "java": {
                "postgresql": ["postgresql"],
                "mysql": ["mysql-connector-java"],
                "mongodb": ["spring-boot-starter-data-mongodb"]
            },
            "csharp": {
                "postgresql": ["Npgsql.EntityFrameworkCore.PostgreSQL"],
                "mysql": ["Pomelo.EntityFrameworkCore.MySql"],
                "mongodb": ["MongoDB.Driver"],
                "sqlserver": ["Microsoft.EntityFrameworkCore.SqlServer"]
            }
        }
        
        lang_dbs = db_map.get(language.lower(), {})
        return lang_dbs.get(database.lower(), [])
    
    def get_best_practices(
        self,
        language: str,
        framework: str
    ) -> List[str]:
        """Get best practices for framework"""
        info = self.get_framework_info(language, framework)
        if not info:
            return []
        
        return info.get("best_practices", [])
    
    def get_supported_architectures(
        self,
        language: str,
        framework: str
    ) -> List[str]:
        """Get supported architectures"""
        info = self.get_framework_info(language, framework)
        if not info:
            return []
        
        return info.get("architectures", [])
    
    async def check_for_updates(self, apply: bool = True) -> Dict[str, Any]:
        """Check for framework updates from official sources"""
        updates = {
            "checked_at": datetime.utcnow().isoformat(),
            "updates_found": []
        }
        
        # Check Python packages from PyPI
        python_updates = await self._check_pypi_updates()
        updates["updates_found"].extend(python_updates)
        
        # Check npm packages
        npm_updates = await self._check_npm_updates()
        updates["updates_found"].extend(npm_updates)
        
        # Check Maven packages (Java)
        maven_updates = await self._check_maven_updates()
        updates["updates_found"].extend(maven_updates)
        
        # Check NuGet packages (.NET)
        nuget_updates = await self._check_nuget_updates()
        updates["updates_found"].extend(nuget_updates)
        
        if apply and updates["updates_found"]:
            self._apply_updates(updates["updates_found"])
            self._save_to_db()
            logger.info(f"Applied and saved {len(updates['updates_found'])} updates to database")
            
        self.last_updated = datetime.utcnow()
        return updates

    def _apply_updates(self, updates_found: List[Dict[str, Any]]):
        """Apply found updates to in-memory registry"""
        for update_item in updates_found:
            lang = update_item["language"]
            fw = update_item["package"].replace("@nestjs/", "nestjs")
            if fw == "@angular/core": fw = "angular"
            
            new_version = update_item["latest_version"]
            
            if lang in self.frameworks and fw in self.frameworks[lang]:
                info = self.frameworks[lang][fw]
                if new_version not in info["versions"]:
                    info["versions"].insert(0, new_version)
                info["latest_version"] = new_version
                logger.info(f"Updated {lang}/{fw} to version {new_version}")

    async def run_auto_update(self):
        """Background task for auto-updating the registry"""
        logger.info("Running automatic framework registry update check...")
        try:
            results = await self.check_for_updates(apply=True)
            if results["updates_found"]:
                logger.info(f"Auto-update found and applied {len(results['updates_found'])} updates")
            else:
                logger.info("No updates found during auto-update check")
        except Exception as e:
            logger.error(f"Auto-update failed: {e}")
    
    async def _check_pypi_updates(self) -> List[Dict[str, Any]]:
        """Check PyPI for Python package updates"""
        updates = []
        packages_to_check = ["django", "fastapi", "flask"]
        
        async with aiohttp.ClientSession() as session:
            for package in packages_to_check:
                try:
                    async with session.get(f"https://pypi.org/pypi/{package}/json") as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            latest_version = data["info"]["version"]
                            
                            # Check if update needed
                            current_info = self.frameworks.get("python", {}).get(package, {})
                            current_version = current_info.get("latest_version")
                            
                            if current_version and latest_version != current_version:
                                updates.append({
                                    "language": "python",
                                    "package": package,
                                    "current_version": current_version,
                                    "latest_version": latest_version,
                                    "source": "PyPI"
                                })
                except Exception as e:
                    print(f"Error checking {package}: {e}")
        
        return updates
    
    async def _check_npm_updates(self) -> List[Dict[str, Any]]:
        """Check npm for JavaScript package updates"""
        updates = []
        packages_to_check = ["express", "@nestjs/core", "react", "vue", "@angular/core"]
        
        async with aiohttp.ClientSession() as session:
            for package in packages_to_check:
                try:
                    async with session.get(f"https://registry.npmjs.org/{package}") as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            latest_version = data["dist-tags"]["latest"]
                            
                            # Determine language and framework
                            if package.startswith("@angular"):
                                lang, fw = "frontend", "angular"
                            elif package == "react":
                                lang, fw = "frontend", "react"
                            elif package == "vue":
                                lang, fw = "frontend", "vue"
                            else:
                                lang, fw = "javascript", package.replace("@nestjs/", "nestjs")
                            
                            current_info = self.frameworks.get(lang, {}).get(fw, {})
                            current_version = current_info.get("latest_version")
                            
                            if current_version and latest_version != current_version:
                                updates.append({
                                    "language": lang,
                                    "package": package,
                                    "current_version": current_version,
                                    "latest_version": latest_version,
                                    "source": "npm"
                                })
                except Exception as e:
                    print(f"Error checking {package}: {e}")
        
        return updates
    
    async def _check_maven_updates(self) -> List[Dict[str, Any]]:
        """Check Maven Central for Java package updates"""
        # Would implement Maven Central API check
        return []
    
    async def _check_nuget_updates(self) -> List[Dict[str, Any]]:
        """Check NuGet for .NET package updates"""
        # Would implement NuGet API check
        return []


# Global registry instance
framework_registry = FrameworkRegistry()
