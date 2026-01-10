"""
Daily Registry Updater
Automatically checks for framework updates daily
"""
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class DailyRegistryUpdater:
    """Automatically update framework registry daily"""
    
    def __init__(self, framework_registry, db_manager=None):
        self.registry = framework_registry
        self.db_manager = db_manager
        self.update_task = None
        self.is_running = False
    
    async def start(self):
        """Start daily update task"""
        if self.is_running:
            return
        
        self.is_running = True
        self.update_task = asyncio.create_task(self._daily_update_loop())
        logger.info("Daily registry updater started")
    
    async def stop(self):
        """Stop daily update task"""
        self.is_running = False
        if self.update_task:
            self.update_task.cancel()
            try:
                await self.update_task
            except asyncio.CancelledError:
                pass
        logger.info("Daily registry updater stopped")
    
    async def _daily_update_loop(self):
        """Main update loop - runs daily"""
        while self.is_running:
            try:
                # Calculate next update time (2 AM UTC)
                now = datetime.utcnow()
                next_update = now.replace(hour=2, minute=0, second=0, microsecond=0)
                
                if next_update <= now:
                    next_update += timedelta(days=1)
                
                # Wait until next update time
                wait_seconds = (next_update - now).total_seconds()
                logger.info(f"Next registry update in {wait_seconds/3600:.1f} hours")
                
                await asyncio.sleep(wait_seconds)
                
                # Perform update
                await self.perform_update()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in daily update loop: {e}")
                await asyncio.sleep(3600)  # Wait 1 hour on error
    
    async def perform_update(self):
        """Perform registry update"""
        logger.info("Starting framework registry update...")
        
        try:
            # Check for updates
            updates = await self.registry.check_for_updates()
            
            logger.info(f"Found {len(updates['updates_found'])} updates")
            
            # Apply updates
            for update in updates['updates_found']:
                await self._apply_update(update)
            
            # Update database if available
            if self.db_manager:
                await self._sync_to_database()
            
            logger.info("Framework registry update completed successfully")
            
        except Exception as e:
            logger.error(f"Failed to update framework registry: {e}")
    
    async def _apply_update(self, update: Dict[str, Any]):
        """Apply a single update"""
        language = update['language']
        package = update['package']
        new_version = update['latest_version']
        
        logger.info(f"Updating {language}/{package} to {new_version}")
        
        # Update in-memory registry
        if language in self.registry.frameworks:
            if package in self.registry.frameworks[language]:
                self.registry.frameworks[language][package]['latest_version'] = new_version
        
        # Log to database
        if self.db_manager:
            await self.db_manager.log_update(
                update_type='framework',
                language=language,
                framework=package,
                old_version=update['current_version'],
                new_version=new_version,
                source=update['source']
            )
    
    async def _sync_to_database(self):
        """Sync registry to database"""
        if not self.db_manager:
            return
        
        logger.info("Syncing registry to database...")
        
        for language, frameworks in self.registry.frameworks.items():
            for framework, info in frameworks.items():
                # Save framework version
                await self.db_manager.save_framework_version(
                    language=language,
                    framework=framework,
                    version=info.get('latest_version'),
                    is_latest=True,
                    is_lts=info.get('lts_version') == info.get('latest_version')
                )
                
                # Save best practices
                if 'best_practices' in info:
                    await self.db_manager.save_best_practices(
                        language,
                        framework,
                        info['best_practices']
                    )
                
                # Save required packages
                if 'required_packages' in info:
                    await self.db_manager.save_required_packages(
                        language,
                        framework,
                        info['required_packages']
                    )
                
                # Save SDK/JDK versions
                if 'sdk_versions' in info:
                    for sdk_version in info['sdk_versions']:
                        await self.db_manager.save_sdk_version(
                            language=language,
                            sdk_type='SDK',
                            version=sdk_version,
                            is_latest=sdk_version == info.get('recommended_sdk')
                        )
                
                if 'jdk_versions' in info:
                    for jdk_version in info['jdk_versions']:
                        await self.db_manager.save_sdk_version(
                            language=language,
                            sdk_type='JDK',
                            version=jdk_version,
                            is_latest=jdk_version == info.get('recommended_jdk')
                        )
        
        logger.info("Database sync completed")
