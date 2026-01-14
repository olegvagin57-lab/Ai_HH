"""Vacancy management service"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.domain.entities.vacancy import Vacancy
from app.domain.entities.user import User
from app.domain.entities.search import Search
from app.core.logging import get_logger
from app.core.exceptions import NotFoundException, ValidationException


logger = get_logger(__name__)


class VacancyService:
    """Service for managing vacancies"""
    
    async def create_vacancy(
        self,
        user: User,
        title: str,
        description: str,
        requirements: str,
        city: str,
        search_query: str,
        search_city: str,
        remote: bool = False,
        salary_min: Optional[int] = None,
        salary_max: Optional[int] = None,
        currency: str = "RUR"
    ) -> Vacancy:
        """Create a new vacancy"""
        vacancy = Vacancy(
            user_id=str(user.id),
            title=title,
            description=description,
            requirements=requirements,
            city=city,
            remote=remote,
            salary_min=salary_min,
            salary_max=salary_max,
            currency=currency,
            search_query=search_query,
            search_city=search_city,
            status="draft"
        )
        await vacancy.create()
        
        logger.info("Vacancy created", vacancy_id=str(vacancy.id), user_id=str(user.id))
        return vacancy
    
    async def get_vacancy(self, vacancy_id: str, user: User) -> Vacancy:
        """Get vacancy by ID"""
        vacancy = await Vacancy.get(vacancy_id)
        if not vacancy:
            raise NotFoundException("Vacancy not found")
        
        # Check permissions
        if str(vacancy.user_id) != str(user.id) and not user.can_view_all_searches():
            raise ValidationException("Access denied")
        
        return vacancy
    
    async def update_vacancy(
        self,
        vacancy_id: str,
        user: User,
        title: Optional[str] = None,
        description: Optional[str] = None,
        requirements: Optional[str] = None,
        city: Optional[str] = None,
        remote: Optional[bool] = None,
        salary_min: Optional[int] = None,
        salary_max: Optional[int] = None,
        currency: Optional[str] = None,
        search_query: Optional[str] = None,
        search_city: Optional[str] = None
    ) -> Vacancy:
        """Update vacancy"""
        vacancy = await self.get_vacancy(vacancy_id, user)
        
        if title is not None:
            vacancy.title = title
        if description is not None:
            vacancy.description = description
        if requirements is not None:
            vacancy.requirements = requirements
        if city is not None:
            vacancy.city = city
        if remote is not None:
            vacancy.remote = remote
        if salary_min is not None:
            vacancy.salary_min = salary_min
        if salary_max is not None:
            vacancy.salary_max = salary_max
        if currency is not None:
            vacancy.currency = currency
        if search_query is not None:
            vacancy.search_query = search_query
        if search_city is not None:
            vacancy.search_city = search_city
        
        vacancy.updated_at = datetime.utcnow()
        await vacancy.save()
        
        logger.info("Vacancy updated", vacancy_id=vacancy_id)
        return vacancy
    
    async def update_vacancy_status(
        self,
        vacancy_id: str,
        status: str,
        user: User
    ) -> Vacancy:
        """Update vacancy status"""
        vacancy = await self.get_vacancy(vacancy_id, user)
        
        if status == "active":
            vacancy.activate()
        elif status == "paused":
            vacancy.pause()
        elif status == "closed":
            vacancy.close()
        elif status == "filled":
            vacancy.fill()
        else:
            raise ValidationException(f"Invalid status: {status}")
        
        await vacancy.save()
        
        logger.info("Vacancy status updated", vacancy_id=vacancy_id, status=status)
        return vacancy
    
    async def update_auto_matching_settings(
        self,
        vacancy_id: str,
        user: User,
        enabled: Optional[bool] = None,
        frequency: Optional[str] = None,
        min_score: Optional[int] = None,
        max_notifications: Optional[int] = None
    ) -> Vacancy:
        """Update auto-matching settings"""
        vacancy = await self.get_vacancy(vacancy_id, user)
        
        if enabled is not None:
            vacancy.auto_matching_enabled = enabled
        if frequency is not None:
            if frequency not in ["daily", "twice_weekly", "weekly", "manual"]:
                raise ValidationException(f"Invalid frequency: {frequency}")
            vacancy.auto_matching_frequency = frequency
        if min_score is not None:
            if not (1 <= min_score <= 10):
                raise ValidationException("min_score must be between 1 and 10")
            vacancy.auto_matching_min_score = min_score
        if max_notifications is not None:
            if not (1 <= max_notifications <= 50):
                raise ValidationException("max_notifications must be between 1 and 50")
            vacancy.auto_matching_max_notifications = max_notifications
        
        vacancy.updated_at = datetime.utcnow()
        await vacancy.save()
        
        logger.info("Auto-matching settings updated", vacancy_id=vacancy_id)
        return vacancy
    
    async def list_vacancies(
        self,
        user: User,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """List vacancies"""
        query_dict = {}
        
        # Filter by user or all if admin
        if not user.can_view_all_searches():
            query_dict["user_id"] = str(user.id)
        
        # Filter by status
        if status:
            query_dict["status"] = status
        
        skip = (page - 1) * page_size
        vacancies = await Vacancy.find(query_dict).sort(-Vacancy.created_at).skip(skip).limit(page_size).to_list()
        total = await Vacancy.find(query_dict).count()
        
        return {
            "vacancies": vacancies,
            "total": total,
            "page": page,
            "page_size": page_size
        }
    
    async def get_active_vacancies_for_auto_matching(self) -> List[Vacancy]:
        """Get active vacancies with auto-matching enabled"""
        vacancies = await Vacancy.find({
            "status": "active",
            "auto_matching_enabled": True
        }).to_list()
        
        return vacancies
    
    async def add_candidate_to_vacancy(
        self,
        vacancy_id: str,
        resume_id: str,
        user: User
    ) -> Vacancy:
        """Add candidate to vacancy"""
        vacancy = await self.get_vacancy(vacancy_id, user)
        vacancy.add_candidate(resume_id)
        await vacancy.save()
        
        logger.info("Candidate added to vacancy", vacancy_id=vacancy_id, resume_id=resume_id)
        return vacancy
    
    async def remove_candidate_from_vacancy(
        self,
        vacancy_id: str,
        resume_id: str,
        user: User
    ) -> Vacancy:
        """Remove candidate from vacancy"""
        vacancy = await self.get_vacancy(vacancy_id, user)
        vacancy.remove_candidate(resume_id)
        await vacancy.save()
        
        logger.info("Candidate removed from vacancy", vacancy_id=vacancy_id, resume_id=resume_id)
        return vacancy
    
    async def add_search_to_vacancy(
        self,
        vacancy_id: str,
        search_id: str
    ) -> Vacancy:
        """Add search to vacancy history"""
        vacancy = await Vacancy.get(vacancy_id)
        if vacancy:
            vacancy.add_search(search_id)
            await vacancy.save()
        
        return vacancy


# Global service instance
vacancy_service = VacancyService()
