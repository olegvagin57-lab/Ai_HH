#!/usr/bin/env python3
"""Run database migrations"""
import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings
from app.infrastructure.database.mongodb import connect_to_mongo, close_mongo_connection
from app.migrations.migration_manager import MigrationManager
from app.core.logging import get_logger, configure_logging

configure_logging()
logger = get_logger(__name__)


async def main():
    """Main migration function"""
    try:
        logger.info("Starting database migrations")
        
        # Connect to MongoDB
        await connect_to_mongo()
        logger.info("Connected to MongoDB")
        
        # Run migrations
        manager = MigrationManager()
        await manager.run_migrations()
        
        logger.info("Migrations completed successfully")
        
    except Exception as e:
        logger.error("Migration failed", error=str(e), exc_info=True)
        sys.exit(1)
    finally:
        await close_mongo_connection()


if __name__ == "__main__":
    asyncio.run(main())
