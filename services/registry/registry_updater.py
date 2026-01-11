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
    
    def __init__(self, registry_path: str = "platform/registry/registries"):
        self.registry_path = Path(registry_path)
        self.update_log_path = Path("platform/registry/update_log.json")
        
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
    
    async def update_javascript_registry(self) -> Dict[str, Any]:
        """Update JavaScript/TypeScript registry"""
        registry_file = self.registry_path / "javascript_registry.json"
        
        with open(registry_file, 'r') as f:
            registry = json.load(f)
        
        updates = {}
        packages = registry.get("packages", {})
        
        # Sample packages to check (check all in production)
        check_packages = list(packages.keys())[:10]  # Check first 10 for demo
        
        for package_name in check_packages:
            current_version = packages[package_name]
            latest_version = await self.check_npm_package(package_name)
            
            if latest_version and latest_version != current_version:
                updates[package_name] = {
                    "old": current_version,
                    "new": latest_version
                }
                packages[package_name] = latest_version
                logger.info(f"Updated {package_name}: {current_version} -> {latest_version}")
        
        if updates:
            with open(registry_file, 'w') as f:
                json.dump(registry, f, indent=4)
        
        return updates
    
    async def update_python_registry(self) -> Dict[str, Any]:
        """Update Python registry"""
        registry_file = self.registry_path / "python_registry.json"
        
        with open(registry_file, 'r') as f:
            registry = json.load(f)
        
        updates = {}
        packages = registry.get("packages", {})
        
        check_packages = list(packages.keys())[:10]
        
        for package_name in check_packages:
            current_version = packages[package_name]
            latest_version = await self.check_pypi_package(package_name)
            
            if latest_version and latest_version != current_version:
                updates[package_name] = {
                    "old": current_version,
                    "new": latest_version
                }
                packages[package_name] = latest_version
                logger.info(f"Updated {package_name}: {current_version} -> {latest_version}")
        
        if updates:
            with open(registry_file, 'w') as f:
                json.dump(registry, f, indent=4)
        
        return updates
    
    async def update_all_registries(self) -> Dict[str, Dict[str, Any]]:
        """Update all language registries"""
        logger.info("Starting registry auto-update...")
        
        all_updates = {}
        
        # Update JavaScript/TypeScript
        js_updates = await self.update_javascript_registry()
        if js_updates:
            all_updates["javascript"] = js_updates
        
        # Update Python
        py_updates = await self.update_python_registry()
        if py_updates:
            all_updates["python"] = py_updates
        
        # Log updates
        if all_updates:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "updates": all_updates
            }
            
            # Append to log file
            log_data = []
            if self.update_log_path.exists():
                with open(self.update_log_path, 'r') as f:
                    log_data = json.load(f)
            
            log_data.append(log_entry)
            
            with open(self.update_log_path, 'w') as f:
                json.dump(log_data, f, indent=2)
            
            logger.info(f"Registry update complete. {len(all_updates)} registries updated.")
        else:
            logger.info("All registries are up to date.")
        
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
