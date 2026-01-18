"""Migration manager for database migrations"""
import importlib
import pkgutil
from typing import List, Dict, Optional
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings
from app.core.logging import get_logger
from app.migrations.base import Migration, MigrationRecord

logger = get_logger(__name__)


class MigrationManager:
    """Manages database migrations"""
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.database = None
        self.migrations_collection = "migrations"
    
    async def connect(self):
        """Connect to MongoDB"""
        from app.infrastructure.database.mongodb import mongodb
        self.client = mongodb.client
        self.database = mongodb.database
    
    async def get_applied_migrations(self) -> List[str]:
        """Get list of applied migration versions"""
        if not self.database:
            await self.connect()
        
        collection = self.database[self.migrations_collection]
        cursor = collection.find({}, {"version": 1})
        applied = await cursor.to_list(length=1000)
        return [m["version"] for m in applied]
    
    async def record_migration(self, migration: Migration):
        """Record that a migration was applied"""
        if not self.database:
            await self.connect()
        
        collection = self.database[self.migrations_collection]
        await collection.insert_one({
            "version": migration.version,
            "name": migration.name,
            "description": migration.description,
            "applied_at": datetime.utcnow()
        })
    
    async def discover_migrations(self) -> List[Migration]:
        """Discover all migration classes"""
        migrations = []
        
        try:
            import app.migrations.migrations as migrations_module
            for name in dir(migrations_module):
                obj = getattr(migrations_module, name)
                if isinstance(obj, type) and issubclass(obj, Migration) and obj != Migration:
                    migrations.append(obj())
        except ImportError:
            logger.warning("No migrations module found")
        
        # Sort by version
        migrations.sort(key=lambda m: m.version)
        return migrations
    
    async def run_migrations(self, target_version: Optional[str] = None) -> None:
        """Run all pending migrations"""
        if not self.database:
            await self.connect()
        
        applied = await self.get_applied_migrations()
        migrations = await self.discover_migrations()
        
        pending = [m for m in migrations if m.version not in applied]
        
        if not pending:
            logger.info("No pending migrations")
            return
        
        logger.info(f"Found {len(pending)} pending migrations")
        
        for migration in pending:
            if target_version and migration.version > target_version:
                break
            
            try:
                await migration.execute()
                await self.record_migration(migration)
            except Exception as e:
                logger.error(f"Migration {migration.version} failed", error=str(e))
                raise
