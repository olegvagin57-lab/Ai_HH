"""Pytest configuration and fixtures"""
import pytest
import asyncio
import os
import sys
from typing import AsyncGenerator

# Allow nested event loops for testing Celery tasks
try:
    import nest_asyncio
    nest_asyncio.apply()
except ImportError:
    pass  # nest_asyncio not installed, tasks tests will be skipped

# Python 3.13 compatibility fix
if sys.version_info >= (3, 13):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from app.config import settings
from app.domain.entities.user import User, Role, Permission, UserSession
from app.domain.entities.search import Search, Resume, Concept
from app.domain.entities.vacancy import Vacancy
from app.domain.entities.candidate import Candidate, Interaction
from app.domain.entities.comment import Comment
from app.domain.entities.notification import Notification
from app.domain.entities.evaluation_criteria import EvaluationCriteria
from app.application.services.auth_service import AuthService

# Disable rate limiting for tests
os.environ["RATE_LIMIT_ENABLED"] = "false"

# Prevent FastAPI app from connecting to MongoDB on import
# We'll handle connection in test_db fixture
os.environ["SKIP_MONGODB_CONNECTION"] = "true"


@pytest.fixture(autouse=True, scope="session")
def disable_rate_limiting():
    """Disable rate limiting for all tests"""
    import app.config
    # Override rate_limit_enabled setting
    app.config.settings.rate_limit_enabled = False
    yield
    # Restore original value after tests
    app.config.settings.rate_limit_enabled = True


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    import nest_asyncio
    nest_asyncio.apply()  # Apply nest_asyncio to allow nested event loops
    
    if sys.version_info >= (3, 13):
        # For Python 3.13, create a new event loop with proper policy
        policy = asyncio.WindowsSelectorEventLoopPolicy()
        asyncio.set_event_loop_policy(policy)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    else:
        loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    # Упрощенный cleanup - просто закрываем loop
    # Pending tasks будут завершены автоматически при закрытии процесса
    # Это предотвращает зависание
    try:
        # Просто закрываем loop без ожидания задач
        # Это безопасно, так как все тесты уже завершены
        loop.close()
    except Exception:
        pass  # Игнорируем ошибки при закрытии


def check_mongodb_connection():
    """Check if MongoDB is available"""
    import socket
    from urllib.parse import urlparse
    
    try:
        parsed = urlparse(settings.mongodb_url)
        host = parsed.hostname or 'localhost'
        port = parsed.port or 27017
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False


# Global variable to store client for cleanup
_test_mongodb_client = None

@pytest.fixture(scope="session")
async def test_db() -> AsyncGenerator:
    """Create test database connection"""
    import logging
    logger = logging.getLogger(__name__)
    global _test_mongodb_client
    
    logger.info("=== test_db fixture: Starting ===")
    
    # Check MongoDB availability
    logger.info("test_db: Checking MongoDB connection...")
    if not check_mongodb_connection():
        logger.warning("test_db: MongoDB connection check failed")
        pytest.skip(
            "MongoDB недоступен. Запустите MongoDB через Docker: "
            "docker-compose up -d mongodb или используйте скрипт: "
            "backend/scripts/start_mongodb_test.ps1"
        )
    
    # Use test database
    test_db_name = f"{settings.mongodb_database}_test"
    logger.info(f"test_db: Using test database: {test_db_name}")
    
    try:
        logger.info("test_db: Creating MongoDB client...")
        client = AsyncIOMotorClient(settings.mongodb_url, serverSelectionTimeoutMS=5000)
        # Test connection
        logger.info("test_db: Testing connection with ping...")
        await client.admin.command('ping')
        logger.info("test_db: MongoDB connection successful")
    except Exception as e:
        logger.error(f"test_db: MongoDB connection failed: {e}")
        pytest.skip(
            f"Не удалось подключиться к MongoDB: {e}. "
            "Убедитесь, что MongoDB запущен и доступен."
        )
    
    # Store client globally for cleanup
    _test_mongodb_client = client
    
    database = client[test_db_name]
    
    # Initialize Beanie - CRITICAL: This must be done before any Beanie operations
    try:
        logger.info("test_db: Initializing Beanie...")
        await init_beanie(
            database=database,
            document_models=[
                User, Role, Permission, UserSession,
                Search, Resume, Concept,
                Vacancy, Candidate, Interaction,
                Comment, Notification, EvaluationCriteria
            ],
            allow_index_dropping=True
        )
        logger.info("test_db: Beanie initialized successfully")
    except Exception as e:
        logger.error(f"test_db: Beanie initialization failed: {e}")
        client.close()
        _test_mongodb_client = None
        pytest.skip(f"Не удалось инициализировать Beanie: {e}")
    
    # IMPORTANT: Override the global MongoDB connection to use test database
    # This ensures that when FastAPI app tries to use MongoDB, it uses test database
    from app.infrastructure.database.mongodb import mongodb
    mongodb.client = client
    mongodb.database = database
    logger.info("test_db: Global MongoDB connection overridden")
    
    logger.info("=== test_db fixture: Ready ===")
    yield database
    
    logger.info("=== test_db fixture: Cleanup started ===")
    # Minimal cleanup - skip if it might hang
    # Collections will be cleaned on next test run or manually
    # This prevents hanging during test cleanup
    logger.info("test_db: Skipping cleanup to prevent hanging")
    # Don't reset or close client here - keep it alive for all tests
    # Client will be closed by pytest_sessionfinish at the very end
    logger.info("=== test_db fixture: Cleanup finished ===")


def pytest_sessionfinish(session, exitstatus):
    """Close MongoDB client after all tests complete"""
    global _test_mongodb_client
    
    # Минимальный cleanup - просто сбрасываем ссылку
    # MongoDB клиент закроется автоматически при завершении процесса
    # Это предотвращает зависание
    try:
        from app.infrastructure.database.mongodb import mongodb
        mongodb.client = None
        mongodb.database = None
    except Exception:
        pass
    
    # НЕ закрываем клиент явно - это может зависать
    # Пусть OS закроет соединение при завершении процесса
    _test_mongodb_client = None
    
    # Принудительно завершаем процесс после небольшой задержки
    # Motor создает фоновые потоки, которые могут держать процесс живым
    try:
        import threading
        import time
        
        # Даем немного времени на завершение, затем принудительно выходим
        def force_exit():
            time.sleep(0.1)  # Даем 100ms на cleanup
            # Принудительно выходим - это закроет все потоки
            os._exit(exitstatus)
        
        # Запускаем принудительный выход в отдельном потоке
        exit_thread = threading.Thread(target=force_exit, daemon=True)
        exit_thread.start()
    except Exception:
        # Если что-то пошло не так, просто выходим принудительно
        os._exit(exitstatus)


@pytest.fixture
async def auth_service() -> AuthService:
    """Create auth service instance"""
    return AuthService()


@pytest.fixture
async def test_user(test_db, auth_service: AuthService) -> User:
    """Create test user"""
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    email = f"test_{unique_id}@example.com"
    username = f"testuser_{unique_id}"
    
    # Try to delete if exists
    existing = await User.find_one({"email": email})
    if existing:
        await existing.delete()
    
    user = await auth_service.register_user(
        email=email,
        username=username,
        password="TestPassword123",
        full_name="Test User"
    )
    return user


@pytest.fixture
async def admin_user(test_db, auth_service: AuthService) -> User:
    """Create admin user"""
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    email = f"admin_{unique_id}@example.com"
    username = f"admin_{unique_id}"
    
    # Try to delete if exists
    existing = await User.find_one({"email": email})
    if existing:
        await existing.delete()
    
    user = await auth_service.register_user(
        email=email,
        username=username,
        password="AdminPassword123",
        full_name="Admin User",
        role_names=["admin"]
    )
    return user


@pytest.fixture
async def hr_manager_user(test_db, auth_service: AuthService) -> User:
    """Create HR manager user"""
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    email = f"hrmanager_{unique_id}@example.com"
    username = f"hrmanager_{unique_id}"
    
    # Try to delete if exists
    existing = await User.find_one({"email": email})
    if existing:
        await existing.delete()
    
    user = await auth_service.register_user(
        email=email,
        username=username,
        password="HrManager123!",
        full_name="HR Manager",
        role_names=["hr_manager"]
    )
    return user


@pytest.fixture
async def hr_specialist_user(test_db, auth_service: AuthService) -> User:
    """Create HR specialist user"""
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    email = f"hrspecialist_{unique_id}@example.com"
    username = f"hrspecialist_{unique_id}"
    
    # Try to delete if exists
    existing = await User.find_one({"email": email})
    if existing:
        await existing.delete()
    
    user = await auth_service.register_user(
        email=email,
        username=username,
        password="HrSpecialist123!",
        full_name="HR Specialist",
        role_names=["hr_specialist"]
    )
    return user


@pytest.fixture
async def test_search(test_db, test_user) -> Search:
    """Create test search"""
    search = Search(
        user_id=str(test_user.id),
        query="Python developer",
        city="Москва",
        status="completed"
    )
    await search.create()
    return search


@pytest.fixture
async def test_resume(test_db, test_search) -> Resume:
    """Create test resume"""
    import uuid
    # Generate unique hh_id to avoid duplicate key errors
    unique_hh_id = f"test_{uuid.uuid4().hex[:12]}"
    
    resume = Resume(
        search_id=str(test_search.id),
        name="John Doe",
        title="Python Developer",
        preliminary_score=8.5,
        ai_score=9.0,
        match_percentage=85.0,
        hh_id=unique_hh_id  # Set unique hh_id to avoid index conflicts
    )
    await resume.create()
    return resume


@pytest.fixture
async def test_vacancy(test_db, test_user) -> Vacancy:
    """Create test vacancy"""
    vacancy = Vacancy(
        user_id=str(test_user.id),
        title="Python Developer",
        description="We need a Python developer",
        requirements="Python, FastAPI, MongoDB",
        city="Москва",
        search_query="Python developer",
        search_city="Москва",
        status="active"
    )
    await vacancy.create()
    return vacancy


@pytest.fixture
async def test_candidate(test_db, test_resume) -> Candidate:
    """Create test candidate"""
    candidate = Candidate(
        resume_id=str(test_resume.id),
        status="new"
    )
    await candidate.create()
    return candidate
