"""
Real-time Registry Version Checker
Fetches latest versions directly from package registries
"""
import asyncio
import aiohttp
import json
from pathlib import Path
from typing import Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LiveVersionChecker:
    """Check live versions from package registries"""
    
    async def get_npm_version(self, package: str) -> Optional[str]:
        """Get latest npm package version"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"https://registry.npmjs.org/{package}/latest"
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        version = data.get("version")
                        logger.info(f"✓ {package}: {version}")
                        return version
        except Exception as e:
            logger.error(f"✗ Failed to fetch {package}: {e}")
        return None
    
    async def get_pypi_version(self, package: str) -> Optional[str]:
        """Get latest PyPI package version"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"https://pypi.org/pypi/{package}/json"
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        version = data.get("info", {}).get("version")
                        logger.info(f"✓ {package}: {version}")
                        return version
        except Exception as e:
            logger.error(f"✗ Failed to fetch {package}: {e}")
        return None
    
    async def update_javascript_registry(self):
        """Update JavaScript registry with live versions"""
        logger.info("\n=== Updating JavaScript Registry ===")
        
        registry_path = Path("platform/registry/registries/javascript_registry.json")
        with open(registry_path, 'r') as f:
            registry = json.load(f)
        
        # Check critical packages
        packages_to_check = {
            "@angular/cli": "Angular",
            "react": "React",
            "vue": "Vue",
            "next": "Next.js",
            "@nestjs/core": "NestJS",
            "express": "Express",
            "typescript": "TypeScript"
        }
        
        updates = {}
        for npm_package, framework_name in packages_to_check.items():
            version = await self.get_npm_version(npm_package)
            if version:
                updates[framework_name] = version
        
        # Update frameworks
        for framework in registry.get("frameworks", []):
            if framework["name"] in updates:
                old_version = framework["version"]
                new_version = updates[framework["name"]]
                if old_version != new_version:
                    framework["version"] = new_version
                    logger.info(f"  Updated {framework['name']}: {old_version} → {new_version}")
        
        # Update packages
        npm_packages = {
            "typescript": "typescript",
            "webpack": "webpack",
            "vite": "vite",
            "axios": "axios",
            "react-router-dom": "react-router-dom",
            "eslint": "eslint",
            "prettier": "prettier"
        }
        
        for pkg_key, npm_name in npm_packages.items():
            if pkg_key in registry.get("packages", {}):
                version = await self.get_npm_version(npm_name)
                if version:
                    old_version = registry["packages"][pkg_key]
                    if old_version != version:
                        registry["packages"][pkg_key] = version
                        logger.info(f"  Updated package {pkg_key}: {old_version} → {version}")
        
        # Save updated registry
        with open(registry_path, 'w') as f:
            json.dump(registry, f, indent=4)
        
        logger.info("✓ JavaScript registry updated\n")
        return registry
    
    async def update_python_registry(self):
        """Update Python registry with live versions"""
        logger.info("=== Updating Python Registry ===")
        
        registry_path = Path("platform/registry/registries/python_registry.json")
        with open(registry_path, 'r') as f:
            registry = json.load(f)
        
        # Check critical packages
        pypi_packages = {
            "fastapi": "FastAPI",
            "django": "Django",
            "flask": "Flask",
            "pydantic": "Pydantic"
        }
        
        updates = {}
        for pypi_package, framework_name in pypi_packages.items():
            version = await self.get_pypi_version(pypi_package)
            if version:
                updates[framework_name] = version
        
        # Update frameworks
        for framework in registry.get("frameworks", []):
            if framework["name"] in updates:
                old_version = framework["version"]
                new_version = updates[framework["name"]]
                if old_version != new_version:
                    framework["version"] = new_version
                    logger.info(f"  Updated {framework['name']}: {old_version} → {new_version}")
        
        # Update packages
        package_mapping = {
            "pydantic": "pydantic",
            "sqlalchemy": "sqlalchemy",
            "numpy": "numpy",
            "pandas": "pandas",
            "pytest": "pytest",
            "requests": "requests"
        }
        
        for pkg_key, pypi_name in package_mapping.items():
            if pkg_key in registry.get("packages", {}):
                version = await self.get_pypi_version(pypi_name)
                if version:
                    old_version = registry["packages"][pkg_key]
                    if old_version != version:
                        registry["packages"][pkg_key] = version
                        logger.info(f"  Updated package {pkg_key}: {old_version} → {version}")
        
        # Save updated registry
        with open(registry_path, 'w') as f:
            json.dump(registry, f, indent=4)
        
        logger.info("✓ Python registry updated\n")
        return registry
    
    async def update_typescript_registry(self):
        """Update TypeScript registry"""
        logger.info("=== Updating TypeScript Registry ===")
        registry_path = Path("platform/registry/registries/typescript_registry.json")
        with open(registry_path, 'r') as f:
            registry = json.load(f)
        
        packages = {"@nestjs/core": "NestJS", "next": "Next.js", "prisma": "Prisma", "typescript": "TypeScript"}
        for npm_pkg, fw_name in packages.items():
            version = await self.get_npm_version(npm_pkg)
            if version:
                for framework in registry.get("frameworks", []):
                    if framework["name"] == fw_name:
                        old = framework["version"]
                        if old != version:
                            framework["version"] = version
                            logger.info(f"  Updated {fw_name}: {old} → {version}")
        
        with open(registry_path, 'w') as f:
            json.dump(registry, f, indent=4)
        logger.info("✓ TypeScript registry updated\n")
    
    async def update_rust_registry(self):
        """Update Rust registry from crates.io"""
        logger.info("=== Updating Rust Registry ===")
        registry_path = Path("platform/registry/registries/rust_registry.json")
        with open(registry_path, 'r') as f:
            registry = json.load(f)
        
        crates = {"actix-web": "Actix-web", "rocket": "Rocket", "axum": "Axum", "tokio": "Tokio", "diesel": "Diesel", "sea-orm": "SeaORM"}
        for crate, fw_name in crates.items():
            version = await self.get_cargo_version(crate)
            if version:
                for framework in registry.get("frameworks", []):
                    if framework["name"] == fw_name:
                        old = framework["version"]
                        if old != version:
                            framework["version"] = version
                            logger.info(f"  Updated {fw_name}: {old} → {version}")
        
        with open(registry_path, 'w') as f:
            json.dump(registry, f, indent=4)
        logger.info("✓ Rust registry updated\n")
    
    async def get_cargo_version(self, crate: str) -> Optional[str]:
        """Get latest Rust crate version"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"https://crates.io/api/v1/crates/{crate}"
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        version = data.get("crate", {}).get("max_version")
                        logger.info(f"✓ {crate}: {version}")
                        return version
        except Exception as e:
            logger.error(f"✗ Failed to fetch {crate}: {e}")
        return None
    
    async def update_dart_registry(self):
        """Update Dart/Flutter registry"""
        logger.info("=== Updating Dart/Flutter Registry ===")
        registry_path = Path("platform/registry/registries/dart_registry.json")
        with open(registry_path, 'r') as f:
            registry = json.load(f)
        
        # Update Flutter framework version (check pub.dev for flutter package)
        packages = {"riverpod": "Riverpod", "bloc": "Bloc", "get": "GetX"}
        for pkg, fw_name in packages.items():
            version = await self.get_pub_version(pkg)
            if version:
                for framework in registry.get("frameworks", []):
                    if framework["name"] == fw_name:
                        old = framework["version"]
                        if old != version:
                            framework["version"] = version
                            logger.info(f"  Updated {fw_name}: {old} → {version}")
        
        with open(registry_path, 'w') as f:
            json.dump(registry, f, indent=4)
        logger.info("✓ Dart registry updated\n")
    
    async def get_pub_version(self, package: str) -> Optional[str]:
        """Get latest Dart package version from pub.dev"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"https://pub.dev/api/packages/{package}"
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        version = data.get("latest", {}).get("version")
                        logger.info(f"✓ {package}: {version}")
                        return version
        except Exception as e:
            logger.error(f"✗ Failed to fetch {package}: {e}")
        return None
    
    async def get_nuget_version(self, package: str) -> Optional[str]:
        """Get latest NuGet package version"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"https://api.nuget.org/v3-flatcontainer/{package.lower()}/index.json"
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        versions = data.get("versions", [])
                        if versions:
                            # Get latest stable version (not preview/rc)
                            stable = [v for v in versions if not any(x in v.lower() for x in ['alpha', 'beta', 'rc', 'preview'])]
                            version = stable[-1] if stable else versions[-1]
                            logger.info(f"✓ {package}: {version}")
                            return version
        except Exception as e:
            logger.error(f"✗ Failed to fetch {package}: {e}")
        return None
    
    async def get_maven_version(self, group_id: str, artifact_id: str) -> Optional[str]:
        """Get latest Maven package version"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"https://search.maven.org/solrsearch/select?q=g:{group_id}+AND+a:{artifact_id}&rows=1&wt=json"
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        docs = data.get("response", {}).get("docs", [])
                        if docs:
                            version = docs[0].get("latestVersion")
                            logger.info(f"✓ {group_id}:{artifact_id}: {version}")
                            return version
        except Exception as e:
            logger.error(f"✗ Failed to fetch {group_id}:{artifact_id}: {e}")
        return None
    
    async def get_go_module_version(self, module_path: str) -> Optional[str]:
        """Get latest Go module version"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"https://proxy.golang.org/{module_path}/@latest"
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        version = data.get("Version", "").replace("v", "")
                        logger.info(f"✓ {module_path}: {version}")
                        return version
        except Exception as e:
            logger.error(f"✗ Failed to fetch {module_path}: {e}")
        return None
    
    async def get_rubygems_version(self, gem: str) -> Optional[str]:
        """Get latest RubyGems version"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"https://rubygems.org/api/v1/gems/{gem}.json"
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        version = data.get("version")
                        logger.info(f"✓ {gem}: {version}")
                        return version
        except Exception as e:
            logger.error(f"✗ Failed to fetch {gem}: {e}")
        return None
    
    async def get_packagist_version(self, package: str) -> Optional[str]:
        """Get latest Packagist (PHP) version"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"https://repo.packagist.org/p2/{package}.json"
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        packages = data.get("packages", {}).get(package, [])
                        if packages:
                            # Get latest stable version
                            versions = [p["version"] for p in packages if "dev" not in p["version"].lower()]
                            if versions:
                                version = versions[0]
                                logger.info(f"✓ {package}: {version}")
                                return version
        except Exception as e:
            logger.error(f"✗ Failed to fetch {package}: {e}")
        return None
    
    async def update_dotnet_registry(self):
        """Update .NET registry from NuGet"""
        logger.info("=== Updating .NET Registry ===")
        registry_path = Path("platform/registry/registries/dotnet_registry.json")
        with open(registry_path, 'r') as f:
            registry = json.load(f)
        
        packages = {
            "Microsoft.AspNetCore.App": "ASP.NET Core",
            "Newtonsoft.Json": "Newtonsoft.Json",
            "Serilog": "Serilog",
            "AutoMapper": "AutoMapper",
            "Dapper": "Dapper"
        }
        
        for nuget_pkg, name in packages.items():
            version = await self.get_nuget_version(nuget_pkg)
            if version:
                # Update in packages section
                if name in registry.get("packages", {}):
                    old = registry["packages"][name]
                    if old != version:
                        registry["packages"][name] = version
                        logger.info(f"  Updated {name}: {old} → {version}")
        
        with open(registry_path, 'w') as f:
            json.dump(registry, f, indent=4)
        logger.info("✓ .NET registry updated\n")
    
    async def update_java_registry(self):
        """Update Java registry from Maven Central"""
        logger.info("=== Updating Java Registry ===")
        registry_path = Path("platform/registry/registries/java_registry.json")
        with open(registry_path, 'r') as f:
            registry = json.load(f)
        
        maven_packages = {
            ("org.springframework.boot", "spring-boot"): "Spring Boot",
            ("io.quarkus", "quarkus-core"): "Quarkus",
            ("org.hibernate.orm", "hibernate-core"): "Hibernate"
        }
        
        for (group_id, artifact_id), fw_name in maven_packages.items():
            version = await self.get_maven_version(group_id, artifact_id)
            if version:
                for framework in registry.get("frameworks", []):
                    if framework["name"] == fw_name:
                        old = framework["version"]
                        if old != version:
                            framework["version"] = version
                            logger.info(f"  Updated {fw_name}: {old} → {version}")
        
        with open(registry_path, 'w') as f:
            json.dump(registry, f, indent=4)
        logger.info("✓ Java registry updated\n")
    
    async def update_go_registry(self):
        """Update Go registry from Go Proxy"""
        logger.info("=== Updating Go Registry ===")
        registry_path = Path("platform/registry/registries/go_registry.json")
        with open(registry_path, 'r') as f:
            registry = json.load(f)
        
        modules = {
            "github.com/gin-gonic/gin": "Gin",
            "github.com/labstack/echo/v4": "Echo",
            "github.com/gofiber/fiber/v2": "Fiber",
            "gorm.io/gorm": "GORM"
        }
        
        for module_path, fw_name in modules.items():
            version = await self.get_go_module_version(module_path)
            if version:
                for framework in registry.get("frameworks", []):
                    if framework["name"] == fw_name:
                        old = framework["version"]
                        if old != version:
                            framework["version"] = version
                            logger.info(f"  Updated {fw_name}: {old} → {version}")
        
        with open(registry_path, 'w') as f:
            json.dump(registry, f, indent=4)
        logger.info("✓ Go registry updated\n")
    
    async def update_ruby_registry(self):
        """Update Ruby registry from RubyGems"""
        logger.info("=== Updating Ruby Registry ===")
        registry_path = Path("platform/registry/registries/ruby_registry.json")
        with open(registry_path, 'r') as f:
            registry = json.load(f)
        
        gems = {"rails": "Rails", "sinatra": "Sinatra", "hanami": "Hanami"}
        
        for gem, fw_name in gems.items():
            version = await self.get_rubygems_version(gem)
            if version:
                for framework in registry.get("frameworks", []):
                    if framework["name"] == fw_name:
                        old = framework["version"]
                        if old != version:
                            framework["version"] = version
                            logger.info(f"  Updated {fw_name}: {old} → {version}")
        
        with open(registry_path, 'w') as f:
            json.dump(registry, f, indent=4)
        logger.info("✓ Ruby registry updated\n")
    
    async def update_php_registry(self):
        """Update PHP registry from Packagist"""
        logger.info("=== Updating PHP Registry ===")
        registry_path = Path("platform/registry/registries/php_registry.json")
        with open(registry_path, 'r') as f:
            registry = json.load(f)
        
        packages = {
            "laravel/framework": "Laravel",
            "symfony/symfony": "Symfony",
            "codeigniter4/framework": "CodeIgniter"
        }
        
        for package, fw_name in packages.items():
            version = await self.get_packagist_version(package)
            if version:
                for framework in registry.get("frameworks", []):
                    if framework["name"] == fw_name:
                        old = framework["version"]
                        if old != version:
                            framework["version"] = version
                            logger.info(f"  Updated {fw_name}: {old} → {version}")
        
        with open(registry_path, 'w') as f:
            json.dump(registry, f, indent=4)
        logger.info("✓ PHP registry updated\n")
    
    async def update_all_registries(self):
        """Update all registries with live versions"""
        logger.info("\n" + "="*60)
        logger.info("LIVE VERSION UPDATE - ALL LANGUAGES")
        logger.info("="*60 + "\n")
        
        # Update all registries
        await self.update_javascript_registry()
        await self.update_typescript_registry()
        await self.update_python_registry()
        await self.update_rust_registry()
        await self.update_dart_registry()
        await self.update_dotnet_registry()
        await self.update_java_registry()
        await self.update_go_registry()
        await self.update_ruby_registry()
        await self.update_php_registry()
        
        logger.info("="*60)
        logger.info("✓ ALL 10 REGISTRIES UPDATED WITH LIVE VERSIONS!")
        logger.info("="*60 + "\n")

async def main():
    checker = LiveVersionChecker()
    await checker.update_all_registries()

if __name__ == "__main__":
    asyncio.run(main())
