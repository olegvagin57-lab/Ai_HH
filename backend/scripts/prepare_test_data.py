"""Script to prepare comprehensive test data for manual testing"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import settings
from app.core.logging import configure_logging, get_logger
from app.infrastructure.database.mongodb import connect_to_mongo, close_mongo_connection
from app.application.services.auth_service import AuthService
from app.domain.entities.user import User
from app.domain.entities.search import Search, Resume
from app.domain.entities.vacancy import Vacancy
from app.domain.entities.candidate import Candidate
from app.domain.entities.notification import Notification

configure_logging()
logger = get_logger(__name__)


async def create_test_users(auth_service: AuthService) -> Dict[str, User]:
    """Create test users"""
    logger.info("Creating test users...")
    
    test_users_data = [
        {
            "email": "admin@test.com",
            "username": "admin",
            "password": "Admin123!",
            "full_name": "Admin User",
            "role_names": ["admin"]
        },
        {
            "email": "hr@test.com",
            "username": "hr",
            "password": "Hr123456!",
            "full_name": "HR Specialist",
            "role_names": ["hr_specialist"]
        },
        {
            "email": "manager@test.com",
            "username": "manager",
            "password": "Manager123!",
            "full_name": "HR Manager",
            "role_names": ["hr_manager"]
        }
    ]
    
    users = {}
    
    for user_data in test_users_data:
        try:
            existing = await User.find_one({"email": user_data["email"]})
            if existing:
                logger.info(f"User {user_data['email']} already exists")
                users[user_data["email"]] = existing
                continue
            
            user = await auth_service.register_user(
                email=user_data["email"],
                username=user_data["username"],
                password=user_data["password"],
                full_name=user_data["full_name"],
                role_names=user_data["role_names"]
            )
            users[user_data["email"]] = user
            logger.info(f"Created user: {user_data['email']}")
        except Exception as e:
            logger.error(f"Error creating user {user_data['email']}: {e}")
    
    return users


async def create_test_vacancies(users: Dict[str, User]) -> List[Vacancy]:
    """Create test vacancies"""
    logger.info("Creating test vacancies...")
    
    hr_user = users.get("hr@test.com")
    if not hr_user:
        logger.warning("HR user not found, skipping vacancies")
        return []
    
    vacancies_data = [
        {
            "title": "Senior Python Developer",
            "description": "We are looking for an experienced Python developer with 5+ years of experience in backend development.",
            "requirements": "Python, FastAPI, PostgreSQL, Docker, Kubernetes",
            "salary_min": 200000,
            "salary_max": 350000,
            "location": "Москва",
            "status": "active",
            "auto_matching_enabled": True,
            "auto_matching_frequency": "daily"
        },
        {
            "title": "Frontend React Developer",
            "description": "Looking for a skilled React developer to join our frontend team.",
            "requirements": "React, TypeScript, Redux, CSS",
            "salary_min": 150000,
            "salary_max": 250000,
            "location": "Санкт-Петербург",
            "status": "active",
            "auto_matching_enabled": True,
            "auto_matching_frequency": "weekly"
        },
        {
            "title": "DevOps Engineer",
            "description": "We need an experienced DevOps engineer to manage our infrastructure.",
            "requirements": "Docker, Kubernetes, AWS, CI/CD, Terraform",
            "salary_min": 180000,
            "salary_max": 300000,
            "location": "Москва",
            "status": "draft",
            "auto_matching_enabled": False
        }
    ]
    
    vacancies = []
    
    for vacancy_data in vacancies_data:
        try:
            # Check if vacancy already exists
            existing = await Vacancy.find_one({
                "user_id": str(hr_user.id),
                "title": vacancy_data["title"]
            })
            
            if existing:
                logger.info(f"Vacancy '{vacancy_data['title']}' already exists")
                vacancies.append(existing)
                continue
            
            vacancy = Vacancy(
                user_id=str(hr_user.id),
                title=vacancy_data["title"],
                description=vacancy_data["description"],
                requirements=vacancy_data["requirements"],
                city=vacancy_data.get("location", "Москва"),
                search_query=vacancy_data["title"],
                search_city=vacancy_data.get("location", "Москва"),
                salary_min=vacancy_data.get("salary_min"),
                salary_max=vacancy_data.get("salary_max"),
                status=vacancy_data["status"],
                auto_matching_enabled=vacancy_data.get("auto_matching_enabled", False),
                auto_matching_frequency=vacancy_data.get("auto_matching_frequency", "weekly"),
                created_at=datetime.utcnow()
            )
            
            await vacancy.create()
            vacancies.append(vacancy)
            logger.info(f"Created vacancy: {vacancy_data['title']}")
        except Exception as e:
            logger.error(f"Error creating vacancy '{vacancy_data['title']}': {e}")
    
    return vacancies


async def create_test_searches(users: Dict[str, User]) -> List[Search]:
    """Create test searches"""
    logger.info("Creating test searches...")
    
    hr_user = users.get("hr@test.com")
    if not hr_user:
        logger.warning("HR user not found, skipping searches")
        return []
    
    searches_data = [
        {
            "query": "Python разработчик",
            "area": "Москва",
            "specialization": "Разработка",
            "status": "completed"
        },
        {
            "query": "React frontend developer",
            "area": "Санкт-Петербург",
            "specialization": "Разработка",
            "status": "pending"
        },
        {
            "query": "DevOps инженер",
            "area": "Москва",
            "specialization": "Администрирование",
            "status": "processing"
        }
    ]
    
    searches = []
    
    for search_data in searches_data:
        try:
            # Check if search already exists
            existing = await Search.find_one({
                "user_id": str(hr_user.id),
                "query": search_data["query"]
            })
            
            if existing:
                logger.info(f"Search '{search_data['query']}' already exists")
                searches.append(existing)
                continue
            
            search = Search(
                user_id=str(hr_user.id),
                city=search_data.get("area", "Москва"),
                query=search_data["query"],
                status=search_data["status"],
                created_at=datetime.utcnow()
            )
            
            await search.create()
            searches.append(search)
            logger.info(f"Created search: {search_data['query']}")
        except Exception as e:
            logger.error(f"Error creating search '{search_data['query']}': {e}")
    
    return searches


async def create_test_resumes(searches: List[Search]) -> List[Resume]:
    """Create test resumes for searches"""
    logger.info("Creating test resumes...")
    
    if not searches:
        logger.warning("No searches found, skipping resumes")
        return []
    
    resumes = []
    search = searches[0]  # Use first search
    
    resumes_data = [
        {
            "hh_id": "test_resume_1",
            "title": "Senior Python Developer",
            "first_name": "Иван",
            "last_name": "Петров",
            "age": 32,
            "experience_years": 7,
            "location": "Москва",
            "salary": 300000,
            "skills": ["Python", "FastAPI", "PostgreSQL", "Docker"],
            "education": "Высшее техническое",
            "status": "active"
        },
        {
            "hh_id": "test_resume_2",
            "title": "Python Backend Developer",
            "first_name": "Мария",
            "last_name": "Сидорова",
            "age": 28,
            "experience_years": 5,
            "location": "Москва",
            "salary": 250000,
            "skills": ["Python", "Django", "Redis", "Celery"],
            "education": "Высшее техническое",
            "status": "active"
        },
        {
            "hh_id": "test_resume_3",
            "title": "React Frontend Developer",
            "first_name": "Алексей",
            "last_name": "Иванов",
            "age": 26,
            "experience_years": 4,
            "location": "Санкт-Петербург",
            "salary": 200000,
            "skills": ["React", "TypeScript", "Redux", "CSS"],
            "education": "Высшее техническое",
            "status": "active"
        }
    ]
    
    for resume_data in resumes_data:
        try:
            # Check if resume already exists
            existing = await Resume.find_one({"hh_id": resume_data["hh_id"]})
            
            if existing:
                logger.info(f"Resume '{resume_data['hh_id']}' already exists")
                resumes.append(existing)
                continue
            
            resume = Resume(
                search_id=str(search.id),
                hh_id=resume_data["hh_id"],
                title=resume_data["title"],
                first_name=resume_data.get("first_name"),
                last_name=resume_data.get("last_name"),
                age=resume_data.get("age"),
                experience_years=resume_data.get("experience_years"),
                location=resume_data.get("location"),
                salary=resume_data.get("salary"),
                skills=resume_data.get("skills", []),
                education=resume_data.get("education"),
                status=resume_data.get("status", "active"),
                created_at=datetime.utcnow()
            )
            
            await resume.create()
            resumes.append(resume)
            logger.info(f"Created resume: {resume_data['hh_id']}")
        except Exception as e:
            logger.error(f"Error creating resume '{resume_data['hh_id']}': {e}")
    
    return resumes


async def create_test_candidates(users: Dict[str, User], resumes: List[Resume], vacancies: List[Vacancy]) -> List[Candidate]:
    """Create test candidates"""
    logger.info("Creating test candidates...")
    
    hr_user = users.get("hr@test.com")
    if not hr_user:
        logger.warning("HR user not found, skipping candidates")
        return []
    
    if not resumes:
        logger.warning("No resumes found, skipping candidates")
        return []
    
    candidates = []
    
    for i, resume in enumerate(resumes[:2]):  # Create candidates for first 2 resumes
        try:
            # Check if candidate already exists
            existing = await Candidate.find_one({"resume_id": resume.id})
            
            if existing:
                logger.info(f"Candidate for resume '{resume.hh_id}' already exists")
                candidates.append(existing)
                continue
            
            candidate = Candidate(
                resume_id=str(resume.id),
                user_id=str(hr_user.id),
                status="new",
                folder="inbox",
                created_at=datetime.utcnow()
            )
            
            # Add to first vacancy if exists
            if vacancies:
                candidate.vacancy_ids = [str(vacancies[0].id)]
            
            await candidate.create()
            candidates.append(candidate)
            logger.info(f"Created candidate for resume: {resume.hh_id}")
        except Exception as e:
            logger.error(f"Error creating candidate for resume '{resume.hh_id}': {e}")
    
    return candidates


async def create_test_notifications(users: Dict[str, User]) -> List[Notification]:
    """Create test notifications"""
    logger.info("Creating test notifications...")
    
    hr_user = users.get("hr@test.com")
    if not hr_user:
        logger.warning("HR user not found, skipping notifications")
        return []
    
    notifications_data = [
        {
            "type": "new_candidate",
            "title": "Новый кандидат",
            "message": "Добавлен новый кандидат в поиск",
            "read": False
        },
        {
            "type": "auto_match",
            "title": "Автоподбор",
            "message": "Найден подходящий кандидат для вакансии",
            "read": False
        },
        {
            "type": "status_changed",
            "title": "Изменение статуса",
            "message": "Статус кандидата изменен",
            "read": True
        }
    ]
    
    notifications = []
    
    for notif_data in notifications_data:
        try:
            notification = Notification(
                user_id=str(hr_user.id),
                type=notif_data["type"],
                title=notif_data["title"],
                message=notif_data["message"],
                read=notif_data.get("read", False),
                created_at=datetime.utcnow()
            )
            
            await notification.create()
            notifications.append(notification)
            logger.info(f"Created notification: {notif_data['type']}")
        except Exception as e:
            logger.error(f"Error creating notification '{notif_data['type']}': {e}")
    
    return notifications


async def main():
    """Main function"""
    print("=" * 60)
    print("Prepare Test Data for Manual Testing")
    print("=" * 60)
    print(f"Database: {settings.mongodb_database}")
    print()
    
    try:
        # Connect to MongoDB
        await connect_to_mongo()
        logger.info("Connected to MongoDB")
        
        # Initialize auth service
        auth_service = AuthService()
        await auth_service.initialize_default_roles_and_permissions()
        logger.info("Roles and permissions initialized")
        
        # Create test data
        users = await create_test_users(auth_service)
        vacancies = await create_test_vacancies(users)
        searches = await create_test_searches(users)
        resumes = await create_test_resumes(searches)
        candidates = await create_test_candidates(users, resumes, vacancies)
        notifications = await create_test_notifications(users)
        
        # Summary
        print()
        print("=" * 60)
        print("✅ Test data preparation completed!")
        print("=" * 60)
        print()
        print("Created/Updated:")
        print(f"  👥 Users: {len(users)}")
        print(f"  💼 Vacancies: {len(vacancies)}")
        print(f"  🔍 Searches: {len(searches)}")
        print(f"  📄 Resumes: {len(resumes)}")
        print(f"  👤 Candidates: {len(candidates)}")
        print(f"  🔔 Notifications: {len(notifications)}")
        print()
        print("Test Users Credentials:")
        print("  - admin@test.com / Admin123! (admin)")
        print("  - hr@test.com / Hr123456! (hr_specialist)")
        print("  - manager@test.com / Manager123! (hr_manager)")
        print()
        print("You can now use these credentials for manual testing!")
        print()
        
        return 0
        
    except Exception as e:
        logger.error("Error preparing test data", error=str(e), exc_info=True)
        print(f"❌ Error: {e}")
        return 1
    finally:
        await close_mongo_connection()


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
