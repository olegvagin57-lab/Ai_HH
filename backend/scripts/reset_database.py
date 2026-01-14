"""Script to reset MongoDB database - drop database and recreate"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import settings
from app.core.logging import configure_logging, get_logger
from motor.motor_asyncio import AsyncIOMotorClient

configure_logging()
logger = get_logger(__name__)


async def reset_database():
    """Drop and recreate database"""
    client = AsyncIOMotorClient(settings.mongodb_url)
    
    # Drop database
    await client.drop_database(settings.mongodb_database)
    logger.info(f"Database {settings.mongodb_database} dropped")
    
    # Recreate (just by connecting)
    db = client[settings.mongodb_database]
    await db.command('ping')
    logger.info(f"Database {settings.mongodb_database} recreated")
    
    client.close()
    logger.info("Database reset complete")


async def main():
    """Main function"""
    print("=" * 60)
    print("MongoDB Database Reset")
    print("=" * 60)
    print(f"Database: {settings.mongodb_database}")
    print(f"MongoDB URL: {settings.mongodb_url}")
    print()
    print("⚠️  WARNING: This will DELETE ALL DATA in the database!")
    print()
    
    response = input("Type 'RESET' to confirm: ")
    if response != 'RESET':
        print("Cancelled.")
        return 0
    
    try:
        await reset_database()
        print()
        print("✅ Database reset successfully!")
        print("Now restart the backend - it will create indexes automatically.")
    except Exception as e:
        logger.error("Error resetting database", error=str(e))
        print(f"❌ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
