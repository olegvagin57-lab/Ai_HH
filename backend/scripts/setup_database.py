"""Script to setup MongoDB database - drop and recreate indexes"""
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


async def drop_all_indexes():
    """Drop all indexes from all collections"""
    client = AsyncIOMotorClient(settings.mongodb_url)
    db = client[settings.mongodb_database]
    
    collections = await db.list_collection_names()
    
    logger.info("Dropping all indexes from collections", collections=collections)
    
    for collection_name in collections:
        collection = db[collection_name]
        try:
            # Get all indexes except _id
            indexes = await collection.list_indexes().to_list(length=None)
            for index in indexes:
                if index['name'] != '_id_':
                    await collection.drop_index(index['name'])
                    logger.info(f"Dropped index {index['name']} from {collection_name}")
        except Exception as e:
            logger.warning(f"Error dropping indexes from {collection_name}: {e}")
    
    client.close()
    logger.info("All indexes dropped")


async def main():
    """Main function"""
    print("=" * 60)
    print("MongoDB Database Setup")
    print("=" * 60)
    print(f"Database: {settings.mongodb_database}")
    print(f"MongoDB URL: {settings.mongodb_url}")
    print()
    
    response = input("This will drop ALL indexes from the database. Continue? (yes/no): ")
    if response.lower() != 'yes':
        print("Cancelled.")
        return
    
    try:
        await drop_all_indexes()
        print()
        print("✅ All indexes dropped successfully!")
        print("Now restart the backend - Beanie will recreate indexes automatically.")
    except Exception as e:
        logger.error("Error setting up database", error=str(e))
        print(f"❌ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
