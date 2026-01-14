"""MongoDB connection and configuration"""
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from typing import Optional
from app.config import settings
from app.core.logging import get_logger


logger = get_logger(__name__)


class MongoDB:
    """MongoDB connection manager"""
    
    client: Optional[AsyncIOMotorClient] = None
    database = None


mongodb = MongoDB()


async def connect_to_mongo() -> None:
    """Create database connection and initialize Beanie"""
    try:
        logger.info("Connecting to MongoDB", mongodb_url=settings.mongodb_url)
        
        # Create Motor client
        mongodb.client = AsyncIOMotorClient(
            settings.mongodb_url,
            maxPoolSize=10,
            minPoolSize=1,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=10000,
            socketTimeoutMS=10000
        )
        
        # Get database
        mongodb.database = mongodb.client[settings.mongodb_database]
        
        # Test connection
        await mongodb.client.admin.command('ping')
        logger.info("MongoDB connection successful")
        
        # Initialize Beanie with document models
        # Models will be imported and registered here
        from app.domain.entities.user import User, Role, Permission, UserSession
        from app.domain.entities.search import Search, Resume, Concept
        from app.domain.entities.evaluation_criteria import EvaluationCriteria
        from app.domain.entities.candidate import Candidate, Interaction
        from app.domain.entities.vacancy import Vacancy
        from app.domain.entities.comment import Comment
        from app.domain.entities.notification import Notification
        
        await init_beanie(
            database=mongodb.database,
            document_models=[
                User, Role, Permission, UserSession,
                Search, Resume, Concept,
                EvaluationCriteria,
                Candidate, Interaction,
                Vacancy,
                Comment,
                Notification
            ],
            allow_index_dropping=True,  # Allow dropping indexes to recreate them
        )
        
        logger.info("Beanie initialized with document models")
        logger.info(
            "Connected to MongoDB",
            database=settings.mongodb_database,
            mongodb_url=settings.mongodb_url
        )
        
    except Exception as e:
        logger.error("Failed to connect to MongoDB", error=str(e), exc_info=True)
        raise


async def close_mongo_connection() -> None:
    """Close database connection"""
    try:
        if mongodb.client:
            mongodb.client.close()
            logger.info("MongoDB connection closed")
    except Exception as e:
        logger.error("Error closing MongoDB connection", error=str(e))


async def get_database():
    """Get database instance"""
    return mongodb.database


async def check_mongodb_health() -> bool:
    """Check MongoDB connection health"""
    try:
        if mongodb.client is None:
            return False
        
        await mongodb.client.admin.command('ping')
        return True
    except Exception as e:
        logger.error("MongoDB health check failed", error=str(e))
        return False
