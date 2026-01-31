"""
Framework Registry - 2026 Edition
Manages versions, logos, best practices, and architecture mappings 
with DB persistence and auto-update capabilities.
"""
import logging
import asyncio
import aiohttp
from typing import Dict, Any, List, Optional
from datetime import datetime
from services.database.base import SessionLocal
from services.registry.persistence import FrameworkMetadata, LanguageMetadata, DatabaseMetadata
from sqlalchemy import select, update, insert

logger = logging.getLogger(__name__)

class FrameworkRegistry:
    """Central registry for technology stack metadata with Category Support"""
    
    def __init__(self):
        # Structured as: {category: {language: {framework: data}}}
        self.frameworks: Dict[str, Dict[str, Dict[str, Any]]] = {
            "backend": {},
            "frontend": {},
            "mobile": {}
        }
        self.languages: Dict[str, Dict[str, Any]] = {}
        # Structured as: {db_type: {name: data}}
        self.databases: Dict[str, Dict[str, Any]] = {
            "SQL": {},
            "NoSQL": {},
            "Vector": {}
        }
        self.last_updated: Optional[datetime] = None
        self._initialize_from_db()
    
    def _initialize_from_db(self):
        """Load data from database or initialize with defaults"""
        try:
            with SessionLocal() as db:
                # 1. Load Languages
                res_lang = db.execute(select(LanguageMetadata)).scalars().all()
                if not res_lang:
                    logger.info("Initializing Framework Registry with defaults...")
                    self._load_defaults()
                    self._save_to_db()
                    return

                for item in res_lang:
                    self.languages[item.name] = {
                        "logo_url": item.logo_url,
                        "description": item.description,
                        "is_compiled": item.is_compiled,
                        "update_source": item.update_source,
                        "update_identifier": item.update_identifier
                    }

                # 2. Load Frameworks
                res_fw = db.execute(select(FrameworkMetadata)).scalars().all()
                for item in res_fw:
                    cat = item.category or "backend"
                    lang = item.language
                    fw = item.framework
                    
                    if cat not in self.frameworks: self.frameworks[cat] = {}
                    if lang not in self.frameworks[cat]: self.frameworks[cat][lang] = {}
                    
                    self.frameworks[cat][lang][fw] = {
                        "logo_url": item.logo_url,
                        "latest_version": item.latest_version,
                        "lts_version": item.lts_version,
                        "versions": item.versions,
                        "architectures": item.architectures,
                        "best_practices": item.best_practices,
                        "required_packages": item.required_packages,
                        "update_source": item.update_source,
                        "update_identifier": item.update_identifier
                    }

                # 3. Load Databases
                res_db = db.execute(select(DatabaseMetadata)).scalars().all()
                for item in res_db:
                    db_cat = item.db_type if item.db_type in ["SQL", "NoSQL", "Vector"] else "SQL"
                    if db_cat not in self.databases: self.databases[db_cat] = {}
                    
                    self.databases[db_cat][item.name] = {
                        "logo_url": item.logo_url,
                        "db_type": item.db_type,
                        "latest_version": item.latest_version,
                        "update_source": item.update_source,
                        "update_identifier": item.update_identifier
                    }
        except Exception as e:
             logger.error(f"Database unavailable during registry initialization: {e}")
             self._load_defaults()

    def _load_defaults(self):
        """Set premium metadata for 2026 with full categorization and smart defaults"""
        # 1. Languages
        self.languages = {
            "python": {
                "logo_url": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg",
                "description": "AI, Backend & Data Science Leader",
                "update_source": "pypi", "update_identifier": "python",
                "recommended_sdk": "3.12", "sdk_versions": ["3.12", "3.11", "3.10"]
            },
            "typescript": {
                "logo_url": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/typescript/typescript-original.svg",
                "description": "Typed JavaScript for FullStack Enterprise",
                "update_source": "npm", "update_identifier": "typescript",
                "recommended_sdk": "5.6", "sdk_versions": ["5.6", "5.5", "5.4"]
            },
            "dart": {
                "logo_url": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/dart/dart-original.svg",
                "description": "Client-optimized language for fast apps",
                "update_source": "npm", "update_identifier": "dart",
                "recommended_sdk": "3.5", "sdk_versions": ["3.5", "3.4"]
            }
        }

        # 2. Frameworks by Category
        self.frameworks = {
            "backend": {
                "python": {
                    "fastapi": {
                        "logo_url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png",
                        "latest_version": "0.115.6",
                        "update_source": "pypi", "update_identifier": "fastapi",
                        "architectures": [
                            {
                                "name": "Clean Architecture", 
                                "structure": ["domain/", "application/", "infrastructure/", "api/v1/"],
                                "description": "Strict separation of concerns using DDD."
                            },
                            {
                                "name": "Layered Architecture",
                                "structure": ["models/", "services/", "controllers/", "schemas/"],
                                "description": "Simple 3-tier architecture."
                            }
                        ],
                        "best_practices": [
                            "Use Pydantic V2 for 5x performance",
                            "Async-first dependency injection",
                            "Structured logging with OTel integration",
                            "Use APIRouter for modularity"
                        ],
                        "required_packages": ["fastapi", "uvicorn", "pydantic[email]", "python-multipart"]
                    }
                },
                "typescript": {
                    "nestjs": {
                        "logo_url": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/nestjs/nestjs-plain.svg",
                        "latest_version": "11.0.0",
                        "update_source": "npm", "update_identifier": "@nestjs/core",
                        "architectures": [
                            {
                                "name": "Modular Architecture", 
                                "structure": ["src/modules/", "src/common/", "src/core/", "src/shared/"],
                                "description": "Highly scalable modular pattern."
                            }
                        ],
                        "best_practices": [
                            "Use Dependency Injection",
                            "Strict Type Checking",
                            "Custom Decorators for clean code",
                            "Interceptor-based logging"
                        ],
                        "required_packages": ["@nestjs/core", "@nestjs/common", "reflect-metadata", "rxjs"]
                    }
                }
            },
            "frontend": {
                "typescript": {
                    "angular": {
                        "logo_url": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/angularjs/angularjs-original.svg",
                        "latest_version": "19.1.4",
                        "update_source": "npm", "update_identifier": "@angular/core",
                        "architectures": [
                            {
                                "name": "Signal-First", 
                                "structure": ["src/app/features/", "src/app/core/", "src/app/shared/"],
                                "description": "Modern reactive Angular using signals."
                            }
                        ],
                        "best_practices": [
                            "Signals for state management",
                            "@if/@for control flow everywhere",
                            "Standalone components only",
                            "Functional interceptors"
                        ],
                        "required_packages": ["@angular/core", "@angular/common", "@angular/router"]
                    },
                    "react": {
                        "logo_url": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/react/react-original.svg",
                        "latest_version": "19.0.0",
                        "update_source": "npm", "update_identifier": "react",
                        "architectures": [
                            {
                                "name": "Atomic Design", 
                                "structure": ["src/components/atoms/", "src/components/molecules/", "src/pages/"],
                                "description": "Component-driven design."
                            }
                        ],
                        "best_practices": [
                            "React 19 Server Components",
                            "Use hooks efficiently",
                            "Zustand/Signals for state",
                            "Tailwind CSS for styling"
                        ],
                        "required_packages": ["react", "react-dom", "lucide-react"]
                    }
                }
            },
            "mobile": {
                "dart": {
                    "flutter": {
                        "logo_url": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/flutter/flutter-original.svg",
                        "latest_version": "3.27.0",
                        "update_source": "npm", "update_identifier": "flutter",
                        "architectures": [
                            {
                                "name": "BLoC Pattern", 
                                "structure": ["lib/presentation/blocs/", "lib/domain/models/", "lib/data/repositories/"],
                                "description": "Business Logic Component pattern."
                            }
                        ],
                        "best_practices": [
                            "Keep UI logic out of widgets",
                            "Use Riverpod or BLoC",
                            "Lazy loading for large lists",
                            "Adaptive layout support"
                        ],
                        "required_packages": ["flutter", "flutter_bloc", "get_it"]
                    }
                }
            }
        }

        # 3. Databases by Type with Driver Mappings
        self.databases = {
            "SQL": {
                "postgresql": {
                    "logo_url": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/postgresql/postgresql-original.svg",
                    "db_type": "SQL", "latest_version": "17.2",
                    "update_source": "docker", "update_identifier": "postgres",
                    "drivers": {
                        "python": "sqlalchemy[asyncio], asyncpg",
                        "typescript": "@mikro-orm/postgresql",
                        "java": "postgresql",
                        "go": "github.com/lib/pq"
                    }
                },
                "mysql": {
                    "logo_url": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/mysql/mysql-original.svg",
                    "db_type": "SQL", "latest_version": "9.0",
                    "drivers": {
                        "python": "aiomysql",
                        "typescript": "mysql2"
                    }
                }
            },
            "NoSQL": {
                "mongodb": {
                    "logo_url": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/mongodb/mongodb-original.svg",
                    "db_type": "NoSQL", "latest_version": "8.0.0",
                    "update_source": "docker", "update_identifier": "mongo",
                    "drivers": {
                        "python": "motor",
                        "typescript": "mongoose"
                    }
                },
                "redis": {
                    "logo_url": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/redis/redis-original.svg",
                    "db_type": "NoSQL", "latest_version": "7.4.0",
                    "drivers": {
                        "python": "redis",
                        "typescript": "ioredis"
                    }
                }
            }
        }

    def _save_to_db(self):
        """Save current metadata to database with category awareness"""
        try:
            with SessionLocal() as db:
                # 1. Languages
                for name, info in self.languages.items():
                    existing = db.execute(select(LanguageMetadata).where(LanguageMetadata.name == name)).scalar_one_or_none()
                    vals = {
                        "logo_url": info.get("logo_url"),
                        "description": info.get("description"),
                        "update_source": info.get("update_source"),
                        "update_identifier": info.get("update_identifier")
                    }
                    if existing:
                        db.execute(update(LanguageMetadata).where(LanguageMetadata.name == name).values(**vals))
                    else:
                        db.execute(insert(LanguageMetadata).values(name=name, **vals))

                # 2. Databases
                for db_type, dbs in self.databases.items():
                    for name, info in dbs.items():
                        existing = db.execute(select(DatabaseMetadata).where(DatabaseMetadata.name == name)).scalar_one_or_none()
                        vals = {
                            "logo_url": info.get("logo_url"),
                            "db_type": db_type,
                            "latest_version": info.get("latest_version"),
                            "update_source": info.get("update_source"),
                            "update_identifier": info.get("update_identifier")
                        }
                        if existing:
                            db.execute(update(DatabaseMetadata).where(DatabaseMetadata.name == name).values(**vals))
                        else:
                            db.execute(insert(DatabaseMetadata).values(name=name, **vals))

                # 3. Frameworks
                for cat, langs in self.frameworks.items():
                    for lang, fws in langs.items():
                        for fw_name, info in fws.items():
                            existing = db.execute(select(FrameworkMetadata).where(
                                FrameworkMetadata.language == lang, 
                                FrameworkMetadata.framework == fw_name
                            )).scalar_one_or_none()
                            vals = {
                                "category": cat,
                                "logo_url": info.get("logo_url"),
                                "latest_version": info.get("latest_version"),
                                "lts_version": info.get("lts_version"),
                                "versions": info.get("versions", []),
                                "architectures": info.get("architectures", []),
                                "best_practices": info.get("best_practices", []),
                                "required_packages": info.get("required_packages", []),
                                "update_source": info.get("update_source"),
                                "update_identifier": info.get("update_identifier"),
                                "last_updated": datetime.utcnow()
                            }
                            if existing:
                                db.execute(update(FrameworkMetadata).where(
                                    FrameworkMetadata.language == lang, 
                                    FrameworkMetadata.framework == fw_name
                                ).values(**vals))
                            else:
                                db.execute(insert(FrameworkMetadata).values(language=lang, framework=fw_name, **vals))
                db.commit()
                logger.info("Saved all categorized metadata to database")
        except Exception as e:
            logger.error(f"Failed to save registry to database: {e}")
    
    def get_framework_info(self, category: Optional[str], language: Optional[str], framework: str) -> Optional[Dict[str, Any]]:
        """Smarter lookup that can search if category/language are unknown"""
        fw = framework.lower()
        
        # 1. Exact match if possible
        if category and language:
            return self.frameworks.get(category.lower(), {}).get(language.lower(), {}).get(fw)
        
        # 2. Search across categories and languages
        for cat, langs in self.frameworks.items():
            if category and cat != category.lower(): continue
            for lang, fws in langs.items():
                if language and lang != language.lower(): continue
                if fw in fws:
                    return fws[fw]
        return None

    def get_framework_language(self, framework: str) -> Optional[str]:
        """Find the language for a given framework"""
        fw = framework.lower()
        for langs in self.frameworks.values():
            for lang, fws in langs.items():
                if fw in fws:
                    return lang
        return None

    def get_required_packages(self, language: str, framework: str, database: Optional[str] = None) -> List[str]:
        """Get all required packages including framework defaults and database drivers"""
        info = self.get_framework_info(None, language, framework)
        if not info: return []
        
        packages = info.get("required_packages", []).copy()
        
        # Add DB Driver if applicable
        if database:
            db_info = None
            # Search in all DB categories
            for cat_dbs in self.databases.values():
                if database.lower() in cat_dbs:
                    db_info = cat_dbs[database.lower()]
                    break
            
            if db_info and "drivers" in db_info:
                driver = db_info["drivers"].get(language.lower())
                if driver: packages.append(driver)
                
        return list(set(packages))

    def get_best_practices(self, language: str, framework: str) -> List[str]:
        """Retrieve best practices for the given stack"""
        info = self.get_framework_info(None, language, framework)
        return info.get("best_practices", []) if info else []

    def get_supported_architectures(self, language: str, framework: str) -> List[str]:
        """Get list of supported architectures"""
        info = self.get_framework_info(None, language, framework)
        if not info: return ["Layered"]
        return [arch["name"] for arch in info.get("architectures", [])]

    def get_architecture_template(self, architecture: str, language: Optional[str] = None, framework: Optional[str] = None) -> Dict[str, Any]:
        """Get detailed structure for a specific architecture"""
        # 1. Try to find specialized template in framework info
        if framework:
            info = self.get_framework_info(None, language, framework)
            if info:
                for arch in info.get("architectures", []):
                    if arch["name"].lower() == architecture.lower():
                        return arch

        # 2. Fallback to global standard templates
        templates = {
            "clean architecture": {
                "structure": ["domain/entities", "domain/repositories", "application/use_cases", "infrastructure/db", "api/v1"],
                "description": "Standard Domain Driven Design (DDD) Clean Architecture"
            },
            "hexagonal": {
                "structure": ["core/domain", "core/ports", "adapters/in/web", "adapters/out/persistence"],
                "description": "Port & Adapters Architecture"
            },
            "mvc": {
                "structure": ["models", "views", "controllers", "services"],
                "description": "Classic Model-View-Controller"
            }
        }
        return templates.get(architecture.lower(), templates["clean architecture"])
    
    def get_all_frameworks(self) -> Dict[str, Any]:
        """Returns all frameworks categorized"""
        return self.frameworks

    def update_framework(self, category: str, language: str, framework: str, data: Dict[str, Any]):
        """Update or Add a framework to the registry with category support"""
        cat, lang, fw = category.lower(), language.lower(), framework.lower()
        if cat not in self.frameworks:
            self.frameworks[cat] = {}
        if lang not in self.frameworks[cat]:
            self.frameworks[cat][lang] = {}
        
        if fw not in self.frameworks[cat][lang]:
            self.frameworks[cat][lang][fw] = {}
            
        self.frameworks[cat][lang][fw].update(data)
        self._save_to_db()
        logger.info(f"Updated framework: {cat}/{lang}/{fw}")

    async def check_for_updates(self, apply: bool = True) -> Dict[str, Any]:
        """Check for updates across categories and databases"""
        updates = {"checked_at": datetime.utcnow().isoformat(), "updates_found": []}
        
        async with aiohttp.ClientSession() as session:
            # 1. Frameworks
            for cat, langs in self.frameworks.items():
                for lang, fws in langs.items():
                    for fw_name, info in fws.items():
                        if info.get("update_source") and info.get("update_identifier"):
                            new_v = await self._fetch_version(session, info["update_source"], info["update_identifier"])
                            if new_v and new_v != info.get("latest_version"):
                                updates["updates_found"].append({
                                    "type": "framework", "category": cat, "language": lang,
                                    "package": fw_name, "latest_version": new_v
                                })
            
            # 2. Databases
            for db_type, dbs in self.databases.items():
                for name, info in dbs.items():
                    if info.get("update_source") and info.get("update_identifier"):
                        new_v = await self._fetch_version(session, info["update_source"], info["update_identifier"])
                        if new_v and new_v != info.get("latest_version"):
                            updates["updates_found"].append({
                                "type": "database", "db_type": db_type,
                                "package": name, "latest_version": new_v
                            })

        if apply and updates["updates_found"]:
            self._apply_updates(updates["updates_found"])
            self._save_to_db()
            
        return updates

    async def _fetch_version(self, session, source: str, identifier: str) -> Optional[str]:
        """Specialized fetchers for different package managers"""
        try:
            if source == "pypi":
                async with session.get(f"https://pypi.org/pypi/{identifier}/json") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data["info"]["version"]
            
            elif source == "npm":
                async with session.get(f"https://registry.npmjs.org/{identifier}") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data["dist-tags"]["latest"]
        
            elif source == "docker":
                # Basic public hub check
                async with session.get(f"https://hub.docker.com/v2/repositories/library/{identifier}/tags/latest") as resp:
                    if resp.status == 200: return "checked" # Docker versioning is complex
        except Exception as e:
            logger.warning(f"Fetch failed for {identifier} via {source}: {e}")

        return None

    def _apply_updates(self, updates_found):
        """Apply found updates to memory"""
        for item in updates_found:
            if item["type"] == "framework":
                cat, lang, fw, v = item["category"], item["language"], item["package"], item["latest_version"]
                if cat in self.frameworks and lang in self.frameworks[cat] and fw in self.frameworks[cat][lang]:
                    info = self.frameworks[cat][lang][fw]
                    if "versions" not in info: info["versions"] = []
                    if v not in info["versions"]: info["versions"].insert(0, v)
                    info["latest_version"] = v
                    logger.info(f"Auto-applied framework update: {cat}/{lang}/{fw} -> {v}")
            elif item["type"] == "database":
                db_cat, name, v = item["db_type"], item["package"], item["latest_version"]
                if db_cat in self.databases and name in self.databases[db_cat]:
                    self.databases[db_cat][name]["latest_version"] = v
                    logger.info(f"Auto-applied database update: {db_cat}/{name} -> {v}")

# Global registry instance
framework_registry = FrameworkRegistry()
