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
    """Central registry for technology stack metadata"""
    
    def __init__(self):
        self.frameworks: Dict[str, Dict[str, Any]] = {}
        self.languages: Dict[str, Dict[str, Any]] = {}
        self.databases: Dict[str, Dict[str, Any]] = {}
        self.last_updated: Optional[datetime] = None
        self._initialize_from_db()
    
    def _initialize_from_db(self):
        """Load data from database or initialize with defaults"""
        try:
            with SessionLocal() as db:
                # 1. Load Frameworks
                res_fw = db.execute(select(FrameworkMetadata)).scalars().all()
                if not res_fw:
                    logger.info("Initializing Framework Registry with defaults...")
                    self._load_defaults()
                    self._save_to_db()
                else:
                    for item in res_fw:
                        lang = item.language
                        fw = item.framework
                        if lang not in self.frameworks: self.frameworks[lang] = {}
                        self.frameworks[lang][fw] = {
                            "logo_url": item.logo_url,
                            "latest_version": item.latest_version,
                            "lts_version": item.lts_version,
                            "versions": item.versions,
                            "architectures": item.architectures,
                            "best_practices": item.best_practices,
                            "required_packages": item.required_packages
                        }

                # 2. Load Languages
                res_lang = db.execute(select(LanguageMetadata)).scalars().all()
                for item in res_lang:
                    self.languages[item.name] = {
                        "logo_url": item.logo_url,
                        "description": item.description,
                        "is_compiled": item.is_compiled
                    }

                # 3. Load Databases
                res_db = db.execute(select(DatabaseMetadata)).scalars().all()
                for item in res_db:
                    self.databases[item.name] = {
                        "logo_url": item.logo_url,
                        "db_type": item.db_type,
                        "latest_version": item.latest_version
                    }
        except Exception as e:
             logger.error(f"Database unavailable during registry initialization: {e}")
             self._load_defaults()

    def _load_defaults(self):
        """Set premium metadata for 2026 with dynamic update sources"""
        # Languages
        self.languages = {
            "python": {
                "logo_url": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg",
                "description": "AI & Data Science Leader",
                "update_source": "pypi",
                "update_identifier": "python"
            },
            "typescript": {
                "logo_url": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/typescript/typescript-original.svg",
                "description": "Typed JavaScript for Enterprise",
                "update_source": "npm",
                "update_identifier": "typescript"
            },
            "java": {
                "logo_url": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/java/java-original.svg", 
                "description": "Robust Backend Language",
                "update_source": "maven",
                "update_identifier": "org.springframework.boot:spring-boot-starter"
            }
        }

        # Databases
        self.databases = {
            "postgresql": {
                "logo_url": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/postgresql/postgresql-original.svg",
                "db_type": "SQL",
                "latest_version": "17.2",
                "update_source": "docker",
                "update_identifier": "postgres"
            }
        }

        # Frameworks - 2026 Premium Standards
        self.frameworks = {
            "python": {
                "fastapi": {
                    "logo_url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png",
                    "latest_version": "0.115.6",
                    "versions": ["0.115.6", "0.111.0"],
                    "update_source": "pypi",
                    "update_identifier": "fastapi",
                    "architectures": [
                        {
                            "name": "Enterprise Clean Architecture",
                            "description": "Domain-driven design with clear separation of concerns.",
                            "structure": ["domain/", "application/", "infrastructure/", "api/"]
                        }
                    ],
                    "best_practices": [
                        "Use Pydantic V2 for 5x performance",
                        "Async-first dependency injection",
                        "Structured logging with OTel integration"
                    ],
                    "required_packages": ["fastapi", "uvicorn", "pydantic[email]"]
                }
            },
            "typescript": { 
                "angular": {
                    "logo_url": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/angularjs/angularjs-original.svg",
                    "latest_version": "19.1.0",
                    "lts_version": "18.x",
                    "versions": ["19.1.0", "18.2.0"],
                    "update_source": "npm",
                    "update_identifier": "@angular/core",
                    "architectures": [
                        {
                            "name": "Signal-First Architecture",
                            "description": "Highly reactive Angular 19+ apps using fine-grained signals.",
                            "structure": ["src/app/features/", "src/app/core/", "src/app/shared/"]
                        }
                    ],
                    "best_practices": [
                        "Use @if/@for control flow for better performance",
                        "Signal-based components as default",
                        "Standalone components only"
                    ],
                    "required_packages": ["@angular/core", "@angular/signals", "@angular/cdk"]
                }
            },
            "java": {
                "spring_boot": {
                    "logo_url": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/spring/spring-original.svg",
                    "latest_version": "3.4.1",
                    "versions": ["3.4.1", "3.3.0"],
                    "update_source": "maven",
                    "update_identifier": "org.springframework.boot:spring-boot-starter-web",
                    "architectures": [
                        {
                            "name": "Loom-Based Reactive Architecture",
                            "description": "Using Java 21+ Virtual Threads for high concurrency without complexity.",
                            "structure": ["src/main/java/com/example/domain/", "src/main/java/com/example/service/"]
                        }
                    ],
                    "best_practices": [
                        "Enable Virtual Threads (Project Loom)",
                        "Use Spring Boot 3.4+ native image support with GraalVM",
                        "Adopt Java 21 Record patterns for DTOs"
                    ],
                    "required_packages": ["spring-boot-starter-web", "spring-boot-starter-data-jpa"]
                }
            }
        }

    def _save_to_db(self):
        """Save current metadata to database"""
        try:
            with SessionLocal() as db:
                # 1. Save Languages
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

                # 2. Save Databases
                for name, info in self.databases.items():
                    existing = db.execute(select(DatabaseMetadata).where(DatabaseMetadata.name == name)).scalar_one_or_none()
                    vals = {
                        "logo_url": info.get("logo_url"),
                        "db_type": info.get("db_type"),
                        "latest_version": info.get("latest_version"),
                        "update_source": info.get("update_source"),
                        "update_identifier": info.get("update_identifier")
                    }
                    if existing:
                        db.execute(update(DatabaseMetadata).where(DatabaseMetadata.name == name).values(**vals))
                    else:
                        db.execute(insert(DatabaseMetadata).values(name=name, **vals))

                # 3. Save Frameworks
                for lang, frameworks in self.frameworks.items():
                    for fw_name, info in frameworks.items():
                        existing = db.execute(select(FrameworkMetadata).where(FrameworkMetadata.language == lang, FrameworkMetadata.framework == fw_name)).scalar_one_or_none()
                        vals = {
                            "logo_url": info.get("logo_url"),
                            "latest_version": info.get("latest_version"),
                            "lts_version": info.get("lts_version"),
                            "versions": info.get("versions"),
                            "architectures": info.get("architectures"),
                            "best_practices": info.get("best_practices"),
                            "required_packages": info.get("required_packages"),
                            "update_source": info.get("update_source"),
                            "update_identifier": info.get("update_identifier"),
                            "last_updated": datetime.utcnow()
                        }
                        if existing:
                            db.execute(update(FrameworkMetadata).where(FrameworkMetadata.language == lang, FrameworkMetadata.framework == fw_name).values(**vals))
                        else:
                            db.execute(insert(FrameworkMetadata).values(language=lang, framework=fw_name, **vals))
                db.commit()
                logger.info("Saved all metadata to database")
        except Exception as e:
            logger.error(f"Failed to save registry to database: {e}")
    
    def get_framework_info(self, language: str, framework: str) -> Optional[Dict[str, Any]]:
        return self.frameworks.get(language.lower(), {}).get(framework.lower())
    
    def get_all_frameworks(self) -> Dict[str, Any]:
        """Returns all frameworks and their metadata"""
        return self.frameworks

    def update_framework(self, language: str, framework: str, data: Dict[str, Any]):
        """Update or Add a framework to the registry"""
        lang = language.lower()
        fw = framework.lower()
        if lang not in self.frameworks:
            self.frameworks[lang] = {}
        
        if fw not in self.frameworks[lang]:
            self.frameworks[lang][fw] = {}
            
        self.frameworks[lang][fw].update(data)
        self._save_to_db()
        logger.info(f"Updated framework: {lang}/{fw}")

    async def check_for_updates(self, apply: bool = True) -> Dict[str, Any]:
        """Check for updates using dynamic sources defined in DB/Registry"""
        updates = {"checked_at": datetime.utcnow().isoformat(), "updates_found": []}
        
        async with aiohttp.ClientSession() as session:
            # Aggregate all items that have update sources
            packages_to_check = []
            
            # 1. Frameworks
            for lang, fws in self.frameworks.items():
                for fw_name, info in fws.items():
                    if info.get("update_source") and info.get("update_identifier"):
                        packages_to_check.append({
                            "type": "framework",
                            "lang": lang,
                            "name": fw_name,
                            "source": info["update_source"],
                            "id": info["update_identifier"],
                            "current": info.get("latest_version")
                        })
            
            # 2. Languages
            for lang, info in self.languages.items():
                if info.get("update_source") and info.get("update_identifier"):
                    packages_to_check.append({
                        "type": "language",
                        "name": lang,
                        "source": info["update_source"],
                        "id": info["update_identifier"]
                    })

            for item in packages_to_check:
                try:
                    new_version = await self._fetch_version(session, item["source"], item["id"])
                    if new_version and new_version != item.get("current"):
                        updates["updates_found"].append({
                            "type": item["type"],
                            "language": item.get("lang"),
                            "package": item["name"],
                            "latest_version": new_version
                        })
                except Exception as e:
                    logger.warning(f"Failed to check update for {item['id']} via {item['source']}: {e}")

        if apply and updates["updates_found"]:
            self._apply_updates(updates["updates_found"])
            self._save_to_db()
            
        return updates

    async def _fetch_version(self, session, source: str, identifier: str) -> Optional[str]:
        """Specialized fetchers for different package managers"""
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
        
        elif source == "maven":
            # identifier format: "group:artifact"
            if ":" not in identifier: return None
            g, a = identifier.split(":")
            url = f"https://search.maven.org/solrsearch/select?q=g:{g}+AND+a:{a}&rows=1&wt=json"
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    docs = data.get("response", {}).get("docs", [])
                    return docs[0].get("latestVersion") if docs else None
        
        elif source == "nuget":
            url = f"https://api.nuget.org/v3-flatcontainer/{identifier.lower()}/index.json"
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    vs = [v for v in data.get("versions", []) if "-" not in v]
                    return vs[-1] if vs else None

        return None

    def _apply_updates(self, updates_found):
        for item in updates_found:
            if item["type"] == "framework":
                lang, fw, v = item["language"], item["package"], item["latest_version"]
                if lang in self.frameworks and fw in self.frameworks[lang]:
                    info = self.frameworks[lang][fw]
                    if "versions" not in info: info["versions"] = []
                    if v not in info["versions"]: info["versions"].insert(0, v)
                    info["latest_version"] = v
                    logger.info(f"Auto-applied framework update: {lang}/{fw} -> {v}")
            elif item["type"] == "language":
                lang, v = item["package"], item["latest_version"]
                if lang in self.languages:
                    self.languages[lang]["latest_version"] = v
                    logger.info(f"Auto-applied language update: {lang} -> {v}")

# Global registry instance
framework_registry = FrameworkRegistry()
