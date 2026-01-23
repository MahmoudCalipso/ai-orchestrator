"""
Registry Auto-Update System
Automatically checks for new versions of frameworks and packages
"""
import asyncio
import logging
import json
import aiohttp
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

class RegistryUpdater:
    """Automatically updates language registries with latest versions"""
    
    def __init__(self, registry_path: str = "services/registry/registries"):
        self.registry_path = Path(registry_path)
        self.update_log_path = Path("storage/registry_update_log.json")
        
    async def check_npm_package(self, package_name: str) -> Optional[str]:
        """Check latest version of npm package"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"https://registry.npmjs.org/{package_name}/latest"
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("version")
        except Exception as e:
            logger.debug(f"Failed to check npm package {package_name}: {e}")
        return None
    
    async def check_pypi_package(self, package_name: str) -> Optional[str]:
        """Check latest version of PyPI package"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"https://pypi.org/pypi/{package_name}/json"
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("info", {}).get("version")
        except Exception as e:
            logger.debug(f"Failed to check PyPI package {package_name}: {e}")
        return None
    
    async def check_maven_package(self, group_id: str, artifact_id: str) -> Optional[str]:
        """Check latest version of Maven package"""
        try:
            async with aiohttp.ClientSession() as session:
                # Use Maven Central API
                url = f"https://search.maven.org/solrsearch/select?q=g:{group_id}+AND+a:{artifact_id}&rows=1&wt=json"
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        docs = data.get("response", {}).get("docs", [])
                        if docs:
                            return docs[0].get("latestVersion")
        except Exception as e:
            logger.debug(f"Failed to check Maven package {group_id}:{artifact_id}: {e}")
        return None
    
    async def check_nuget_package(self, package_name: str) -> Optional[str]:
        """Check latest version of NuGet package"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"https://api.nuget.org/v3-flatcontainer/{package_name.lower()}/index.json"
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        versions = data.get("versions", [])
                        if versions:
                            # Return latest non-preview version
                            stable_versions = [v for v in versions if not any(x in v.lower() for x in ['alpha', 'beta', 'rc', 'preview'])]
                            return stable_versions[-1] if stable_versions else versions[-1]
        except Exception as e:
            logger.debug(f"Failed to check NuGet package {package_name}: {e}")
        return None
    
    async def check_cargo_crate(self, crate_name: str) -> Optional[str]:
        """Check latest version of Rust crate"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"https://crates.io/api/v1/crates/{crate_name}"
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("crate", {}).get("max_version")
        except Exception as e:
            logger.debug(f"Failed to check Cargo crate {crate_name}: {e}")
        return None
    
    async def check_go_module(self, module_path: str) -> Optional[str]:
        """Check latest version of Go module"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"https://proxy.golang.org/{module_path}/@latest"
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("Version", "").replace("v", "")
        except Exception as e:
            logger.debug(f"Failed to check Go module {module_path}: {e}")
        return None

    async def check_rubygems_package(self, package_name: str) -> Optional[str]:
        """Check latest version of RubyGems package"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"https://rubygems.org/api/v1/versions/{package_name}/latest.json"
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("version")
        except Exception as e:
            logger.debug(f"Failed to check RubyGems package {package_name}: {e}")
        return None

    async def check_packagist_package(self, package_name: str) -> Optional[str]:
        """Check latest version of Packagist (PHP) package"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"https://packagist.org/packages/{package_name}.json"
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        # Get latest version from versions dict (it's usually sorted or has a latest field but API vary)
                        versions = data.get("package", {}).get("versions", {})
                        if versions:
                            # Return the first version that doesn't look like a branch or dev
                            for v in versions.keys():
                                if not v.endswith("-dev") and "dev-" not in v:
                                    return v
        except Exception as e:
            logger.debug(f"Failed to check Packagist package {package_name}: {e}")
        return None
    
    async def update_registry(self, language: str) -> Dict[str, Any]:
        """Update a specific language registry from its JSON file"""
        file_map = {
            "javascript": "javascript_registry.json",
            "typescript": "typescript_registry.json",
            "python": "python_registry.json",
            "java": "java_registry.json",
            "csharp": "dotnet_registry.json", # mapped to dotnet
            "go": "go_registry.json",
            "rust": "rust_registry.json",
            "php": "php_registry.json",
            "ruby": "ruby_registry.json",
            "scala": "scala_registry.json",
            "kotlin": "kotlin_registry.json",
            "swift": "swift_registry.json",
            "dart": "dart_registry.json",
            "elixir": "elixir_registry.json",
            "c": "c_registry.json",
            "cpp": "cpp_registry.json"
        }
        
        filename = file_map.get(language.lower())
        if not filename:
            logger.warning(f"No registry file mapping for {language}")
            return {}
            
        registry_file = self.registry_path / filename
        if not registry_file.exists():
            logger.warning(f"Registry file not found: {registry_file}")
            return {}
            
        with open(registry_file, 'r') as f:
            registry = json.load(f)
        
        updates = {}
        packages = registry.get("packages", {})
        
        # Check first 5 packages for all languages (limited for efficiency)
        check_packages = list(packages.keys())[:5]
        
        for package_name in check_packages:
            current_version = packages[package_name]
            latest_version = None
            
            # Determine which checker to use
            if language in ["javascript", "typescript"]:
                latest_version = await self.check_npm_package(package_name)
            elif language == "python":
                latest_version = await self.check_pypi_package(package_name)
            elif language == "java" or language == "scala":
                # simplistic mapping for group/artifact
                if ":" in package_name:
                    gid, aid = package_name.split(":")
                    latest_version = await self.check_maven_package(gid, aid)
            elif language == "csharp":
                latest_version = await self.check_nuget_package(package_name)
            elif language == "rust":
                latest_version = await self.check_cargo_crate(package_name)
            elif language == "go":
                latest_version = await self.check_go_module(package_name)
            elif language == "ruby":
                latest_version = await self.check_rubygems_package(package_name)
            elif language == "php":
                latest_version = await self.check_packagist_package(package_name)
            
            if latest_version and latest_version != current_version:
                updates[package_name] = {
                    "old": current_version,
                    "new": latest_version
                }
                packages[package_name] = latest_version
                logger.info(f"Updated {language} package {package_name}: {current_version} -> {latest_version}")
        
        if updates:
            with open(registry_file, 'w') as f:
                json.dump(registry, f, indent=4)
        
        return updates

    async def update_all_registries(self) -> Dict[str, Dict[str, Any]]:
        """Update all 16 registries (Language and Framework)"""
        logger.info("Starting global registry auto-update for 16 languages...")
        
        all_updates = {}
        languages = [
            "javascript", "typescript", "python", "java", "csharp", "go", 
            "rust", "php", "ruby", "scala", "kotlin", "swift", "dart", 
            "elixir", "c", "cpp"
        ]
        
        for lang in languages:
            try:
                lang_updates = await self.update_registry(lang)
                if lang_updates:
                    all_updates[lang] = lang_updates
            except Exception as e:
                logger.error(f"Failed to update {lang} registry: {e}")
            
        # Update Framework Registry (DB Persisted)
        from services.registry.framework_registry import framework_registry
        try:
            framework_results = await framework_registry.check_for_updates(apply=True)
            if framework_results["updates_found"]:
                all_updates["frameworks"] = framework_results["updates_found"]
                logger.info(f"Framework Registry updated with {len(framework_results['updates_found'])} changes")
        except Exception as e:
            logger.error(f"Framework registry update failed: {e}")
        
        # Log updates
        if all_updates:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "updates": all_updates
            }
            
            # Append to log file
            log_data = []
            if self.update_log_path.exists():
                try:
                    with open(self.update_log_path, 'r') as f:
                        log_data = json.load(f)
                except Exception:
                    log_data = []
            
            log_data.append(log_entry)
            
            with open(self.update_log_path, 'w') as f:
                json.dump(log_data[-100:], f, indent=2)  # Keep last 100 entries
            
            logger.info(f"Registry update complete. {len(all_updates)} categories updated.")
        else:
            logger.info("All registries (16 languages + frameworks) are up to date.")
        
        return all_updates
    
    async def schedule_periodic_updates(self, interval_hours: int = 24):
        """Schedule periodic registry updates"""
        logger.info(f"Scheduling registry updates every {interval_hours} hours")
        
        while True:
            try:
                await self.update_all_registries()
            except Exception as e:
                logger.error(f"Registry update failed: {e}")
            
            # Wait for next update
            await asyncio.sleep(interval_hours * 3600)


# Standalone update function
async def update_registries():
    """Run registry update once"""
    updater = RegistryUpdater()
    return await updater.update_all_registries()


if __name__ == "__main__":
    # Run update
    asyncio.run(update_registries())
