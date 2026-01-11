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


class FrameworkRegistry:
    """Registry for framework versions and metadata"""
    
    def __init__(self):
        self.frameworks: Dict[str, Dict[str, Any]] = {}
        self.last_updated: Optional[datetime] = None
        self._initialize_registry()
    
    def _initialize_registry(self):
        """Initialize framework registry with current versions"""
        self.frameworks = {
            # Python Frameworks
            "python": {
                "django": {
                    "latest_version": "5.0.1",
                    "lts_version": "4.2.9",
                    "versions": ["5.0.1", "4.2.9", "3.2.23"],
                    "architectures": ["MVT", "Clean Architecture", "Hexagonal"],
                    "best_practices": [
                        "Use Django REST Framework for APIs",
                        "Implement custom user model",
                        "Use environment variables for settings",
                        "Enable CORS properly",
                        "Use Django ORM efficiently",
                        "Implement proper authentication (JWT)",
                        "Use Django migrations properly",
                        "Follow Django coding style (PEP 8)"
                    ],
                    "required_packages": [
                        "djangorestframework",
                        "djangorestframework-simplejwt",
                        "django-cors-headers",
                        "python-decouple",
                        "psycopg2-binary",  # PostgreSQL
                        "mysqlclient",  # MySQL
                        "django-filter",
                        "drf-spectacular",  # API documentation
                        "celery",  # Async tasks
                        "redis"
                    ]
                },
                "fastapi": {
                    "latest_version": "0.109.0",
                    "versions": ["0.109.0", "0.108.0", "0.107.0"],
                    "architectures": ["Clean Architecture", "Hexagonal", "Repository Pattern"],
                    "best_practices": [
                        "Use Pydantic models for validation",
                        "Implement dependency injection",
                        "Use async/await properly",
                        "Add API documentation with OpenAPI",
                        "Implement proper error handling",
                        "Use background tasks for long operations",
                        "Add request validation",
                        "Use SQLAlchemy ORM"
                    ],
                    "required_packages": [
                        "fastapi",
                        "uvicorn[standard]",
                        "sqlalchemy",
                        "alembic",
                        "python-jose[cryptography]",  # JWT
                        "passlib[bcrypt]",
                        "python-multipart",
                        "aiofiles",
                        "httpx",
                        "redis",
                        "celery"
                    ]
                },
                "flask": {
                    "latest_version": "3.0.1",
                    "versions": ["3.0.1", "2.3.7"],
                    "architectures": ["MVC", "Blueprint Pattern", "Application Factory"],
                    "best_practices": [
                        "Use application factory pattern",
                        "Organize with blueprints",
                        "Use Flask-SQLAlchemy",
                        "Implement Flask-JWT-Extended",
                        "Add Flask-CORS",
                        "Use Flask-Migrate for migrations",
                        "Implement proper error handlers"
                    ],
                    "required_packages": [
                        "flask",
                        "flask-sqlalchemy",
                        "flask-migrate",
                        "flask-jwt-extended",
                        "flask-cors",
                        "flask-restful",
                        "python-dotenv",
                        "psycopg2-binary",
                        "redis"
                    ]
                }
            },
            
            # JavaScript/TypeScript Frameworks
            "javascript": {
                "express": {
                    "latest_version": "4.18.2",
                    "versions": ["4.18.2", "4.18.1"],
                    "architectures": ["MVC", "Clean Architecture", "Layered"],
                    "best_practices": [
                        "Use middleware properly",
                        "Implement error handling middleware",
                        "Use async/await",
                        "Add request validation (joi/express-validator)",
                        "Implement JWT authentication",
                        "Use environment variables",
                        "Add security headers (helmet)",
                        "Implement rate limiting"
                    ],
                    "required_packages": [
                        "express",
                        "cors",
                        "helmet",
                        "express-rate-limit",
                        "jsonwebtoken",
                        "bcryptjs",
                        "dotenv",
                        "joi",
                        "mongoose",  # MongoDB
                        "pg",  # PostgreSQL
                        "mysql2"
                    ]
                },
                "nestjs": {
                    "latest_version": "10.3.0",
                    "versions": ["10.3.0", "10.2.10"],
                    "architectures": ["Clean Architecture", "CQRS", "Microservices"],
                    "best_practices": [
                        "Use dependency injection",
                        "Implement guards and interceptors",
                        "Use DTOs for validation",
                        "Follow module structure",
                        "Use TypeORM or Prisma",
                        "Implement proper exception filters",
                        "Use configuration module"
                    ],
                    "required_packages": [
                        "@nestjs/core",
                        "@nestjs/common",
                        "@nestjs/platform-express",
                        "@nestjs/jwt",
                        "@nestjs/passport",
                        "@nestjs/typeorm",
                        "@nestjs/config",
                        "typeorm",
                        "class-validator",
                        "class-transformer",
                        "bcrypt",
                        "passport-jwt"
                    ]
                }
            },
            
            # Java Frameworks
            "java": {
                "spring_boot": {
                    "latest_version": "3.2.1",
                    "lts_version": "3.1.7",
                    "versions": ["3.2.1", "3.1.7", "2.7.18"],
                    "jdk_versions": ["21", "17", "11"],
                    "recommended_jdk": "17",
                    "architectures": ["Clean Architecture", "Hexagonal", "Layered", "Microservices"],
                    "best_practices": [
                        "Use Spring Data JPA",
                        "Implement Spring Security with JWT",
                        "Use @RestController for APIs",
                        "Add validation with @Valid",
                        "Use application.properties/yml",
                        "Implement proper exception handling",
                        "Use Lombok to reduce boilerplate",
                        "Follow SOLID principles"
                    ],
                    "required_packages": [
                        "spring-boot-starter-web",
                        "spring-boot-starter-data-jpa",
                        "spring-boot-starter-security",
                        "spring-boot-starter-validation",
                        "jjwt-api",
                        "jjwt-impl",
                        "jjwt-jackson",
                        "lombok",
                        "postgresql",
                        "mysql-connector-java",
                        "springdoc-openapi-starter-webmvc-ui"
                    ]
                }
            },
            
            # .NET Frameworks
            "csharp": {
                "aspnet_core": {
                    "latest_version": "8.0",
                    "lts_version": "6.0",
                    "versions": ["8.0", "7.0", "6.0"],
                    "sdk_versions": ["8.0.101", "7.0.405", "6.0.418"],
                    "recommended_sdk": "8.0.101",
                    "architectures": ["Clean Architecture", "Onion Architecture", "CQRS", "Vertical Slice"],
                    "best_practices": [
                        "Use Entity Framework Core",
                        "Implement JWT authentication",
                        "Use dependency injection",
                        "Add FluentValidation",
                        "Use AutoMapper for DTOs",
                        "Implement MediatR for CQRS",
                        "Add Swagger/OpenAPI",
                        "Use async/await properly"
                    ],
                    "required_packages": [
                        "Microsoft.AspNetCore.Authentication.JwtBearer",
                        "Microsoft.EntityFrameworkCore",
                        "Microsoft.EntityFrameworkCore.SqlServer",
                        "Npgsql.EntityFrameworkCore.PostgreSQL",
                        "AutoMapper.Extensions.Microsoft.DependencyInjection",
                        "FluentValidation.AspNetCore",
                        "MediatR",
                        "Swashbuckle.AspNetCore",
                        "Serilog.AspNetCore"
                    ]
                }
            },
            
            # Go Frameworks
            "go": {
                "gin": {
                    "latest_version": "1.9.1",
                    "versions": ["1.9.1", "1.9.0"],
                    "architectures": ["Clean Architecture", "Hexagonal", "Layered"],
                    "best_practices": [
                        "Use middleware for common tasks",
                        "Implement JWT authentication",
                        "Use GORM for database",
                        "Add request validation",
                        "Use environment variables",
                        "Implement proper error handling",
                        "Use goroutines wisely"
                    ],
                    "required_packages": [
                        "github.com/gin-gonic/gin",
                        "github.com/golang-jwt/jwt/v5",
                        "gorm.io/gorm",
                        "gorm.io/driver/postgres",
                        "gorm.io/driver/mysql",
                        "github.com/joho/godotenv",
                        "golang.org/x/crypto/bcrypt"
                    ]
                }
            },
            
            # Frontend Frameworks
            "frontend": {
                "angular": {
                    "latest_version": "17.1.0",
                    "lts_version": "16.2.12",
                    "versions": ["17.1.0", "16.2.12", "15.2.10"],
                    "architectures": ["Component-based", "Module-based", "Standalone Components"],
                    "best_practices": [
                        "Use standalone components (Angular 14+)",
                        "Implement lazy loading",
                        "Use RxJS properly",
                        "Add Angular Material",
                        "Use services for business logic",
                        "Implement route guards",
                        "Use reactive forms",
                        "Add interceptors for HTTP"
                    ],
                    "required_packages": [
                        "@angular/core",
                        "@angular/common",
                        "@angular/router",
                        "@angular/forms",
                        "@angular/material",
                        "rxjs",
                        "@ngrx/store",  # State management
                        "@ngrx/effects",
                        "ngx-toastr"
                    ]
                },
                "react": {
                    "latest_version": "18.2.0",
                    "versions": ["18.2.0", "18.1.0"],
                    "architectures": ["Component-based", "Atomic Design", "Feature-based"],
                    "best_practices": [
                        "Use functional components and hooks",
                        "Implement React Router",
                        "Use Redux or Zustand for state",
                        "Add React Query for data fetching",
                        "Use TypeScript",
                        "Implement code splitting",
                        "Add error boundaries"
                    ],
                    "required_packages": [
                        "react",
                        "react-dom",
                        "react-router-dom",
                        "@reduxjs/toolkit",
                        "react-redux",
                        "@tanstack/react-query",
                        "axios",
                        "react-hook-form",
                        "zod"
                    ]
                },
                "vue": {
                    "latest_version": "3.4.15",
                    "versions": ["3.4.15", "3.3.13"],
                    "architectures": ["Component-based", "Composition API", "Options API"],
                    "best_practices": [
                        "Use Composition API",
                        "Implement Vue Router",
                        "Use Pinia for state management",
                        "Add Vite for build tool",
                        "Use TypeScript",
                        "Implement lazy loading"
                    ],
                    "required_packages": [
                        "vue",
                        "vue-router",
                        "pinia",
                        "axios",
                        "vee-validate",
                        "vue-toastification"
                    ]
                }
            }
        }
    
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
    
    async def check_for_updates(self) -> Dict[str, Any]:
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
        
        self.last_updated = datetime.utcnow()
        
        return updates
    
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
