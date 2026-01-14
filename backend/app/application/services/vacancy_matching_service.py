"""Vacancy matching service for automatic resume matching"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from app.domain.entities.vacancy import Vacancy
from app.domain.entities.search import Search, Resume
from app.domain.entities.user import User
from app.application.services.search_service import search_service
from app.application.services.vacancy_service import vacancy_service
from app.application.services.evaluation_service import evaluation_service
from app.infrastructure.external.hh_client import hh_client
from app.core.logging import get_logger
from app.core.exceptions import NotFoundException, ValidationException
import redis.asyncio as redis
from app.config import settings


logger = get_logger(__name__)


class VacancyMatchingService:
    """Service for automatic resume matching to vacancies"""
    
    def __init__(self):
        self.redis_client = None
        if redis:
            try:
                self.redis_client = redis.from_url(settings.redis_url, decode_responses=True)
            except Exception as e:
                logger.warning("Redis not available for vacancy matching cache", error=str(e))
    
    async def should_run_auto_match(self, vacancy: Vacancy) -> bool:
        """Check if auto-matching should run for a vacancy"""
        if not vacancy.auto_matching_enabled or vacancy.status != "active":
            return False
        
        if vacancy.auto_matching_frequency == "manual":
            return False
        
        # Check last run time
        if not vacancy.last_auto_match_at:
            return True  # Never run before
        
        now = datetime.utcnow()
        last_run = vacancy.last_auto_match_at
        
        if vacancy.auto_matching_frequency == "daily":
            return (now - last_run).days >= 1
        elif vacancy.auto_matching_frequency == "twice_weekly":
            return (now - last_run).days >= 3
        elif vacancy.auto_matching_frequency == "weekly":
            return (now - last_run).days >= 7
        
        return False
    
    async def run_auto_match_for_vacancy(self, vacancy_id: str) -> Dict[str, Any]:
        """Run automatic matching for a vacancy"""
        vacancy = await Vacancy.get(vacancy_id)
        if not vacancy:
            raise NotFoundException("Vacancy not found")
        
        if not await self.should_run_auto_match(vacancy):
            logger.info("Auto-matching skipped", vacancy_id=vacancy_id, reason="not_due")
            return {"status": "skipped", "reason": "not_due"}
        
        logger.info("Starting auto-matching", vacancy_id=vacancy_id)
        
        # Get already viewed candidate IDs (from Redis cache or database)
        viewed_candidate_ids = await self._get_viewed_candidate_ids(vacancy_id)
        
        # Create search for this vacancy
        # Get or create a user for the vacancy owner
        from app.domain.entities.user import User
        user = await User.get(vacancy.user_id)
        if not user:
            logger.error("Vacancy owner not found", vacancy_id=vacancy_id, user_id=vacancy.user_id)
            return {"status": "error", "message": "Vacancy owner not found"}
        
        # Create search
        search = await search_service.create_search(
            user=user,
            query=vacancy.search_query,
            city=vacancy.search_city
        )
        
        # Add search to vacancy history
        await vacancy_service.add_search_to_vacancy(vacancy_id, str(search.id))
        
        # Extract concepts
        from app.application.services.ai_service import ai_service
        concepts = await ai_service.extract_concepts(vacancy.search_query)
        
        # Search resumes from HH
        all_resumes = []
        max_pages = 5  # Limit to 100 resumes for auto-matching
        
        for page in range(max_pages):
            hh_response = await hh_client.search_resumes(
                query=vacancy.search_query,
                city=vacancy.search_city,
                per_page=20,
                page=page
            )
            
            items = hh_response.get("items", [])
            if not items:
                break
            
            all_resumes.extend(items)
        
        # Process resumes and filter already viewed
        new_candidates = []
        for resume_data in all_resumes:
            hh_id = str(resume_data.get("id", ""))
            
            # Skip if already viewed
            if hh_id in viewed_candidate_ids:
                continue
            
            # Process resume
            resume = await search_service.process_resume_from_hh(search, resume_data, concepts)
            
            # Analyze with AI if score is high enough
            if resume.preliminary_score and resume.preliminary_score >= 6:
                # Get evaluation criteria for vacancy
                from app.domain.entities.evaluation_criteria import EvaluationCriteria
                criteria = await EvaluationCriteria.find_one({"vacancy_id": vacancy_id})
                if not criteria:
                    criteria = await evaluation_service.get_default_criteria()
                
                await search_service.analyze_resume_with_ai(resume, concepts, criteria)
            
            # Check if meets minimum score
            if resume.ai_score and resume.ai_score >= vacancy.auto_matching_min_score:
                new_candidates.append(resume)
                # Add to vacancy
                await vacancy_service.add_candidate_to_vacancy(vacancy_id, str(resume.id), user)
                # Mark as viewed
                await self._mark_candidate_viewed(vacancy_id, hh_id)
        
        # Limit to max_notifications
        new_candidates = new_candidates[:vacancy.auto_matching_max_notifications]
        
        # Send notifications if new candidates found
        if new_candidates:
            from app.application.services.notification_service import notification_service
            await notification_service.notify_auto_match_found(
                user_id=vacancy.user_id,
                vacancy_id=str(vacancy.id),
                vacancy_title=vacancy.title,
                candidates_count=len(new_candidates)
            )
        
        # Update vacancy
        vacancy.last_auto_match_at = datetime.utcnow()
        vacancy.auto_match_count += len(new_candidates)
        await vacancy.save()
        
        logger.info(
            "Auto-matching completed",
            vacancy_id=vacancy_id,
            new_candidates=len(new_candidates),
            total_found=len(all_resumes)
        )
        
        return {
            "status": "completed",
            "new_candidates": len(new_candidates),
            "total_found": len(all_resumes),
            "search_id": str(search.id)
        }
    
    async def _get_viewed_candidate_ids(self, vacancy_id: str) -> set:
        """Get set of already viewed candidate HH IDs for a vacancy"""
        viewed_ids = set()
        
        # Try Redis first
        if self.redis_client:
            try:
                key = f"vacancy:{vacancy_id}:viewed_candidates"
                ids = await self.redis_client.smembers(key)
                viewed_ids.update(ids)
            except Exception as e:
                logger.warning("Failed to get viewed candidates from Redis", error=str(e))
        
        # Also check from database (candidates already in vacancy)
        vacancy = await Vacancy.get(vacancy_id)
        if vacancy and vacancy.candidate_ids:
            # Get resumes and their hh_ids
            for resume_id in vacancy.candidate_ids:
                resume = await Resume.get(resume_id)
                if resume and resume.hh_id:
                    viewed_ids.add(resume.hh_id)
        
        return viewed_ids
    
    async def _mark_candidate_viewed(self, vacancy_id: str, hh_id: str) -> None:
        """Mark a candidate as viewed for a vacancy"""
        if self.redis_client:
            try:
                key = f"vacancy:{vacancy_id}:viewed_candidates"
                await self.redis_client.sadd(key, hh_id)
                # Set expiration (90 days)
                await self.redis_client.expire(key, 90 * 24 * 60 * 60)
            except Exception as e:
                logger.warning("Failed to mark candidate as viewed in Redis", error=str(e))
    
    async def get_vacancies_for_auto_matching(self) -> List[Vacancy]:
        """Get all vacancies that need auto-matching"""
        vacancies = await vacancy_service.get_active_vacancies_for_auto_matching()
        
        # Filter by should_run_auto_match
        matching_vacancies = []
        for vacancy in vacancies:
            if await self.should_run_auto_match(vacancy):
                matching_vacancies.append(vacancy)
        
        return matching_vacancies


# Global service instance
vacancy_matching_service = VacancyMatchingService()
