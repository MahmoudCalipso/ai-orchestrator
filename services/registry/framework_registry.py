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
        """Set default metadata for 2026 including logos and TS-native Angular"""
        # Languages
        self.languages = {
            "python": {"logo_url": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg", "description": "AI & Data Science Leader"},
            "typescript": {"logo_url": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/typescript/typescript-original.svg", "description": "Typed JavaScript for Enterprise"},
            "javascript": {"logo_url": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/javascript/javascript-original.svg", "description": "The Web Standard"},
            "java": {"logo_url": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/java/java-original.svg", "description": "Robust Backend Language"},
            "csharp": {"logo_url": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/csharp/csharp-original.svg", "description": ".NET Core Hero"},
            "go": {"logo_url": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/go/go-original.svg", "description": "Cloud Native Expert"},
            "rust": {"logo_url": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/rust/rust-original.svg", "description": "High Performance & Safety"},
            "ruby": {"logo_url": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/ruby/ruby-original.svg", "description": "Developer Happiness"},
            "php": {"logo_url": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/php/php-original.svg", "description": "Web Veteran"}
        }

        # Databases
        self.databases = {
            "postgresql": {"logo_url": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/postgresql/postgresql-original.svg", "db_type": "SQL", "latest_version": "17.2"},
            "mongodb": {"logo_url": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/mongodb/mongodb-original.svg", "db_type": "NoSQL", "latest_version": "8.0"},
            "redis": {"logo_url": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/redis/redis-original.svg", "db_type": "Key-Value", "latest_version": "7.4"},
            "chromadb": {"logo_url": "https://raw.githubusercontent.com/chroma-core/chroma/main/docs/static/img/chroma-logo.png", "db_type": "Vector", "latest_version": "0.5.23"}
        }

        # Frameworks
        self.frameworks = {
            "python": {
                "fastapi": {
                    "logo_url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png",
                    "latest_version": "0.115.6",
                    "versions": ["0.115.6", "0.111.0"],
                    "architectures": ["Clean Architecture", "Hexagonal"],
                    "best_practices": ["Use Pydantic V2", "Inject Dependencies via Lifespan"],
                    "required_packages": ["fastapi", "uvicorn", "pydantic"]
                },
                "django": {
                    "logo_url": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/django/django-plain.svg",
                    "latest_version": "5.1.4",
                    "versions": ["5.1.4", "5.0.1"],
                    "architectures": ["MVT", "Clean Architecture"],
                    "best_practices": ["Use DRF 4.0", "Custom User Model"],
                    "required_packages": ["django", "djangorestframework"]
                }
            },
            "typescript": { 
                "angular": {
                    "logo_url": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/angularjs/angularjs-original.svg",
                    "latest_version": "19.1.0",
                    "lts_version": "18.x",
                    "versions": ["19.1.0", "18.2.0"],
                    "architectures": ["Signal-based", "Standalone"],
                    "best_practices": ["Use Signals for state", "Avoid Legacy Module Pattern"],
                    "required_packages": ["@angular/core", "@angular/signals"]
                },
                "nestjs": {
                    "logo_url": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/nodejs/nodejs-original.svg",
                    "latest_version": "11.0.0",
                    "versions": ["11.0.0", "10.4.0"],
                    "architectures": ["Clean Architecture", "CQRS"],
                    "best_practices": ["Modular Decoupling", "Use Guards/Interceptors"],
                    "required_packages": ["@nestjs/core", "@nestjs/common"]
                }
            },
            "javascript": {
                "express": {
                    "logo_url": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/express/express-original.svg",
                    "latest_version": "5.0.0",
                    "versions": ["5.0.0", "4.19.2"],
                    "architectures": ["MVC", "Layered"],
                    "best_practices": ["Use Express 5 native async support"],
                    "required_packages": ["express", "cors", "helmet"]
                },
                "angularjs": { # Legacy Angular
                    "logo_url": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/angularjs/angularjs-original.svg",
                    "latest_version": "1.8.3",
                    "versions": ["1.8.3"],
                    "architectures": ["MVC"],
                    "best_practices": ["Upgrade to modern Angular"],
                    "required_packages": ["angular"]
                },
                "react": {
                    "logo_url": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/react/react-original.svg",
                    "latest_version": "19.0.0",
                    "versions": ["19.0.0", "18.3.1"],
                    "architectures": ["Component-based", "Server Components"],
                    "best_practices": ["Use RSC", "Atomic Design"],
                    "required_packages": ["react", "react-dom"]
                }
            },
            "java": {
                "spring_boot": {
                    "logo_url": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/spring/spring-original.svg",
                    "latest_version": "3.4.1",
                    "versions": ["3.4.1", "3.3.0"],
                    "architectures": ["Clean Architecture", "Microservices"],
                    "best_practices": ["Use Java 21+ Virtual Threads", "Spring Boot 3 conventions"],
                    "required_packages": ["spring-boot-starter-web", "spring-boot-starter-data-jpa"]
                }
            },
            "csharp": {
                "aspnet_core": {
                    "logo_url": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/dot-net/dot-net-original.svg",
                    "latest_version": "9.0.0",
                    "versions": ["9.0.0", "8.0.0"],
                    "architectures": ["Clean Architecture", "Vertical Slices"],
                    "best_practices": ["Use Minimal APIs", "EF Core 9 interceptors"],
                    "required_packages": ["Microsoft.AspNetCore.OpenApi", "Microsoft.EntityFrameworkCore"]
                }
            },
            "go": {
                "gin": {
                    "logo_url": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/gin/gin-original.svg",
                    "latest_version": "1.10.x",
                    "versions": ["1.10.0"],
                    "architectures": ["Clean Architecture"],
                    "best_practices": ["Use structural logging with slog", "Graceful shutdown"],
                    "required_packages": ["github.com/gin-gonic/gin"]
                }
            },
            "rust": {
                "actix": {
                    "logo_url": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/rust/rust-original.svg",
                    "latest_version": "4.x",
                    "versions": ["4.7.0"],
                    "architectures": ["Clean Architecture"],
                    "best_practices": ["Zero-copy deserialization", "Async-trait"],
                    "required_packages": ["actix-web", "serde"]
                }
            },
            "ruby": {
                "rails": {
                    "logo_url": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/rails/rails-original-wordmark.svg",
                    "latest_version": "8.0.0",
                    "versions": ["8.0.0", "7.2.1"],
                    "architectures": ["MVC"],
                    "best_practices": ["Solid Queue for jobs", "Turbo/Hotwire"],
                    "required_packages": ["rails", "pg"]
                }
            },
            "php": {
                "laravel": {
                    "logo_url": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/laravel/laravel-original.svg",
                    "latest_version": "11.x",
                    "versions": ["11.33.0"],
                    "architectures": ["MVC", "Action-based"],
                    "best_practices": ["Pint for styling", "Pest for testing"],
                    "required_packages": ["laravel/framework", "lucascudo/laravel-pt-br-localization"]
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
                    if existing:
                        db.execute(update(LanguageMetadata).where(LanguageMetadata.name == name).values(
                            logo_url=info.get("logo_url"), description=info.get("description")
                        ))
                    else:
                        db.execute(insert(LanguageMetadata).values(
                            name=name, logo_url=info.get("logo_url"), description=info.get("description")
                        ))

                # 2. Save Databases
                for name, info in self.databases.items():
                    existing = db.execute(select(DatabaseMetadata).where(DatabaseMetadata.name == name)).scalar_one_or_none()
                    if existing:
                        db.execute(update(DatabaseMetadata).where(DatabaseMetadata.name == name).values(
                            logo_url=info.get("logo_url"), db_type=info.get("db_type"), latest_version=info.get("latest_version")
                        ))
                    else:
                        db.execute(insert(DatabaseMetadata).values(
                            name=name, logo_url=info.get("logo_url"), db_type=info.get("db_type"), latest_version=info.get("latest_version")
                        ))

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
                            "last_updated": datetime.utcnow()
                        }
                        if existing:
                            db.execute(update(FrameworkMetadata).where(FrameworkMetadata.language == lang, FrameworkMetadata.framework == fw_name).values(**vals))
                        else:
                            db.execute(insert(FrameworkMetadata).values(language=lang, framework=fw_name, **vals))
                db.commit()
                logger.info("Saved all metadata (including logos) to database")
        except Exception as e:
            logger.error(f"Failed to save registry to database: {e}")
    
    def get_framework_info(self, language: str, framework: str) -> Optional[Dict[str, Any]]:
        return self.frameworks.get(language.lower(), {}).get(framework.lower())
    
    def get_language_info(self, name: str) -> Optional[Dict[str, Any]]:
        return self.languages.get(name.lower())

    def get_database_info(self, name: str) -> Optional[Dict[str, Any]]:
        return self.databases.get(name.lower())

    def get_best_practices(self, language: str, framework: str) -> List[str]:
        info = self.get_framework_info(language, framework)
        return info.get("best_practices", []) if info else []

    async def check_for_updates(self, apply: bool = True) -> Dict[str, Any]:
        """Check for updates from all official sources (PyPI, npm, Maven, NuGet, Crates, Go, RubyGems, Packagist)"""
        updates = {"checked_at": datetime.utcnow().isoformat(), "updates_found": []}
        
        async with aiohttp.ClientSession() as session:
            # 1. Python (PyPI)
            for pkg in ["fastapi", "django", "flask"]:
                try:
                    async with session.get(f"https://pypi.org/pypi/{pkg}/json") as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            v = data["info"]["version"]
                            if self.frameworks.get("python", {}).get(pkg, {}).get("latest_version") != v:
                                updates["updates_found"].append({"language": "python", "package": pkg, "latest_version": v})
                except: continue

            # 2. JS/TS (npm)
            for pkg in ["express", "@angular/core", "react", "@nestjs/core"]:
                try:
                    async with session.get(f"https://registry.npmjs.org/{pkg}") as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            v = data["dist-tags"]["latest"]
                            lang = "typescript" if "angular" in pkg or "nest" in pkg else "javascript"
                            fw = "angular" if "angular" in pkg else pkg.split("/")[-1]
                            if self.frameworks.get(lang, {}).get(fw, {}).get("latest_version") != v:
                                updates["updates_found"].append({"language": lang, "package": fw, "latest_version": v})
                except: continue

            # 3. Java (Maven)
            for group, artifact, fw in [("org.springframework.boot", "spring-boot-starter", "spring_boot")]:
                try:
                    url = f"https://search.maven.org/solrsearch/select?q=g:{group}+AND+a:{artifact}&rows=1&wt=json"
                    async with session.get(url) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            docs = data.get("response", {}).get("docs", [])
                            if docs:
                                v = docs[0].get("latestVersion")
                                if self.frameworks.get("java", {}).get(fw, {}).get("latest_version") != v:
                                    updates["updates_found"].append({"language": "java", "package": fw, "latest_version": v})
                except: continue

            # 4. C# (NuGet)
            for pkg, fw in [("Microsoft.AspNetCore.App", "aspnet_core")]:
                try:
                    url = f"https://api.nuget.org/v3-flatcontainer/{pkg.lower()}/index.json"
                    async with session.get(url) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            vs = [v for v in data.get("versions", []) if "-" not in v] # Stable only
                            if vs:
                                v = vs[-1]
                                if self.frameworks.get("csharp", {}).get(fw, {}).get("latest_version") != v:
                                    updates["updates_found"].append({"language": "csharp", "package": fw, "latest_version": v})
                except: continue

            # 5. Rust (Crates.io)
            for pkg, fw in [("actix-web", "actix")]:
                try:
                    async with session.get(f"https://crates.io/api/v1/crates/{pkg}") as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            v = data.get("crate", {}).get("max_version")
                            if self.frameworks.get("rust", {}).get(fw, {}).get("latest_version") != v:
                                updates["updates_found"].append({"language": "rust", "package": fw, "latest_version": v})
                except: continue

            # 6. Go (Go Proxy)
            for mod, fw in [("github.com/gin-gonic/gin", "gin")]:
                try:
                    async with session.get(f"https://proxy.golang.org/{mod}/@latest") as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            v = data.get("Version", "").replace("v", "")
                            if self.frameworks.get("go", {}).get(fw, {}).get("latest_version") != v:
                                updates["updates_found"].append({"language": "go", "package": fw, "latest_version": v})
                except: continue

            # 7. Ruby (RubyGems)
            for pkg, fw in [("rails", "rails")]:
                try:
                    async with session.get(f"https://rubygems.org/api/v1/versions/{pkg}/latest.json") as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            v = data.get("version")
                            if self.frameworks.get("ruby", {}).get(fw, {}).get("latest_version") != v:
                                updates["updates_found"].append({"language": "ruby", "package": fw, "latest_version": v})
                except: continue

            # 8. PHP (Packagist)
            for pkg, fw in [("laravel/framework", "laravel")]:
                try:
                    async with session.get(f"https://packagist.org/packages/{pkg}.json") as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            versions = data.get("package", {}).get("versions", {})
                            vs = [v for v in versions.keys() if not v.endswith("-dev") and "dev-" not in v and "x" not in v]
                            if vs:
                                v = vs[0] # Usually newest is first
                                if self.frameworks.get("php", {}).get(fw, {}).get("latest_version") != v:
                                    updates["updates_found"].append({"language": "php", "package": fw, "latest_version": v})
                except: continue

        if apply and updates["updates_found"]:
            self._apply_updates(updates["updates_found"])
            self._save_to_db()
            
        return updates

    def _apply_updates(self, updates_found):
        for item in updates_found:
            lang, fw, v = item["language"], item["package"], item["latest_version"]
            if lang in self.frameworks and fw in self.frameworks[lang]:
                info = self.frameworks[lang][fw]
                if v not in info["versions"]: info["versions"].insert(0, v)
                info["latest_version"] = v
                logger.info(f"Auto-applied update: {lang}/{fw} -> {v}")

# Global registry instance
framework_registry = FrameworkRegistry()
