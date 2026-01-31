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
        """Perform registry update using internal registry logic"""
        logger.info("Starting framework registry update...")
        
        try:
            # Check AND Apply updates internally to the registry
            updates = await self.registry.check_for_updates(apply=True)
            
            logger.info(f"Found {len(updates['updates_found'])} updates")
            
            # Log updates for audit
            for update in updates['updates_found']:
                await self._log_update(update)
            
            # Update database if available
            if self.db_manager:
                await self._sync_to_database()
            
            logger.info("Framework registry update completed successfully")
            
        except Exception as e:
            logger.error(f"Failed to update framework registry: {e}")
            import traceback
            logger.error(traceback.format_exc())

    async def _log_update(self, update: Dict[str, Any]):
        """Log update for audit/history"""
        if not self.db_manager:
            return
            
        u_type = update.get("type")
        if u_type == "framework":
            await self.db_manager.log_update(
                update_type='framework',
                language=update.get('language'),
                framework=update.get('package'),
                old_version="unknown", # Internal application already updated it
                new_version=update.get('latest_version'),
                source=update.get('source', 'registry')
            )
        elif u_type == "database":
            await self.db_manager.log_update(
                update_type='database',
                language=update.get('db_type'),
                framework=update.get('package'),
                old_version="unknown",
                new_version=update.get('latest_version'),
                source="docker"
            )

    async def _sync_to_database(self):
        """Sync registry to database by traversing categorized structure"""
        if not self.db_manager:
            return
        
        logger.info("Syncing categorized registry to database...")
        
        # 1. Sync Frameworks
        for cat, languages in self.registry.frameworks.items():
            for language, frameworks in languages.items():
                for framework, info in frameworks.items():
                    await self.db_manager.save_framework_version(
                        language=language,
                        framework=framework,
                        version=info.get('latest_version'),
                        is_latest=True,
                        category=cat # Passing category if supported by db_manager
                    )
                    
                    if 'best_practices' in info:
                        await self.db_manager.save_best_practices(language, framework, info['best_practices'])
                    
                    if 'required_packages' in info:
                        await self.db_manager.save_required_packages(language, framework, info['required_packages'])

        # 2. Sync Databases
        for db_type, dbs in self.registry.databases.items():
            for name, info in dbs.items():
                await self.db_manager.save_database_metadata(
                    name=name,
                    db_type=db_type,
                    version=info.get('latest_version')
                )
        
        logger.info("Database sync completed")
