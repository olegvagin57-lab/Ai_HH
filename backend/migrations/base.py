"""Base migration class"""
from abc import ABC, abstractmethod
from typing import Optional
from datetime import datetime
from app.core.logging import get_logger

logger = get_logger(__name__)


class Migration(ABC):
    """Base class for database migrations"""
    
    def __init__(self):
        self.version = self.get_version()
        self.name = self.get_name()
        self.description = self.get_description()
    
    @abstractmethod
    def get_version(self) -> str:
        """Get migration version (e.g., '001', '002')"""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Get migration name"""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """Get migration description"""
        pass
    
    @abstractmethod
    async def up(self) -> None:
        """Apply migration"""
        pass
    
    @abstractmethod
    async def down(self) -> None:
        """Rollback migration"""
        pass
    
    async def execute(self) -> None:
        """Execute migration"""
        logger.info(f"Running migration {self.version}: {self.name}")
        try:
            await self.up()
            logger.info(f"Migration {self.version} completed successfully")
        except Exception as e:
            logger.error(f"Migration {self.version} failed", error=str(e), exc_info=True)
            raise


class MigrationRecord:
    """Migration record in database"""
    
    def __init__(
        self,
        version: str,
        name: str,
        applied_at: datetime,
        description: Optional[str] = None
    ):
        self.version = version
        self.name = name
        self.description = description
        self.applied_at = applied_at
