"""Analytics service for metrics and reporting"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from app.domain.entities.vacancy import Vacancy
from app.domain.entities.search import Search
from app.domain.entities.candidate import Candidate
from app.domain.entities.search import Resume
from app.domain.entities.user import User
from app.core.logging import get_logger
from app.core.exceptions import NotFoundException, ValidationException


logger = get_logger(__name__)


class AnalyticsService:
    """Service for analytics and metrics"""
    
    async def get_dashboard_metrics(
        self,
        user: Optional[User] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get dashboard metrics"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Build query filters
        search_query = {}
        vacancy_query = {}
        candidate_query = {}
        
        if user and not user.can_view_all_searches():
            search_query["user_id"] = str(user.id)
            vacancy_query["user_id"] = str(user.id)
        
        # Total searches
        total_searches = await Search.find(search_query).count()
        recent_searches = await Search.find({
            **search_query,
            "created_at": {"$gte": start_date}
        }).count()
        
        # Total vacancies
        total_vacancies = await Vacancy.find(vacancy_query).count()
        active_vacancies = await Vacancy.find({
            **vacancy_query,
            "status": "active"
        }).count()
        
        # Total candidates
        total_candidates = await Candidate.find(candidate_query).count()
        
        # Candidates by status
        candidates_by_status = {}
        statuses = ["new", "reviewed", "shortlisted", "interview_scheduled", "interviewed", "offer_sent", "hired", "rejected"]
        for status in statuses:
            count_query = {"status": status}
            if candidate_query:
                count_query.update(candidate_query)
            candidates_by_status[status] = await Candidate.find(count_query).count()
        
        # Hired candidates
        hired_count = candidates_by_status.get("hired", 0)
        
        # Average time to hire
        avg_time_to_hire = await self._calculate_avg_time_to_hire(user, days)
        
        # Average AI score of hired candidates
        avg_ai_score_hired = await self._calculate_avg_ai_score_hired(user)
        
        # Top skills
        top_skills = await self._get_top_skills(days)
        
        # Distribution by city
        city_distribution = await self._get_city_distribution(user)
        
        # Auto-matching statistics
        auto_match_stats = await self._get_auto_matching_stats(user, days)
        
        return {
            "searches": {
                "total": total_searches,
                "recent": recent_searches
            },
            "vacancies": {
                "total": total_vacancies,
                "active": active_vacancies
            },
            "candidates": {
                "total": total_candidates,
                "by_status": candidates_by_status,
                "hired": hired_count
            },
            "metrics": {
                "avg_time_to_hire_days": avg_time_to_hire,
                "avg_ai_score_hired": avg_ai_score_hired,
                "hiring_rate": (hired_count / total_candidates * 100) if total_candidates > 0 else 0
            },
            "top_skills": top_skills,
            "city_distribution": city_distribution,
            "auto_matching": auto_match_stats,
            "period_days": days
        }
    
    async def get_vacancy_analytics(
        self,
        vacancy_id: str,
        user: User
    ) -> Dict[str, Any]:
        """Get analytics for a specific vacancy"""
        vacancy = await Vacancy.get(vacancy_id)
        if not vacancy:
            raise NotFoundException("Vacancy not found")
        
        # Check permissions
        if str(vacancy.user_id) != str(user.id) and not user.can_view_all_searches():
            raise ValidationException("Access denied")
        
        # Time to hire
        time_to_hire = None
        if vacancy.status == "filled" and vacancy.closed_at and vacancy.created_at:
            time_to_hire = (vacancy.closed_at - vacancy.created_at).days
        
        # Candidates statistics
        total_candidates = len(vacancy.candidate_ids)
        candidates_by_status = {}
        
        for resume_id in vacancy.candidate_ids:
            candidate = await Candidate.find_one({"resume_id": resume_id})
            if candidate:
                status = candidate.status
                candidates_by_status[status] = candidates_by_status.get(status, 0) + 1
        
        # Average AI score
        ai_scores = []
        for resume_id in vacancy.candidate_ids:
            resume = await Resume.get(resume_id)
            if resume and resume.ai_score:
                ai_scores.append(resume.ai_score)
        
        avg_ai_score = sum(ai_scores) / len(ai_scores) if ai_scores else None
        
        # Search history
        searches_count = len(vacancy.search_ids)
        
        # Auto-matching statistics
        auto_match_count = vacancy.auto_match_count
        last_auto_match = vacancy.last_auto_match_at.isoformat() if vacancy.last_auto_match_at else None
        
        return {
            "vacancy_id": vacancy_id,
            "title": vacancy.title,
            "status": vacancy.status,
            "time_to_hire_days": time_to_hire,
            "candidates": {
                "total": total_candidates,
                "by_status": candidates_by_status,
                "avg_ai_score": avg_ai_score
            },
            "searches": {
                "total": searches_count,
                "search_ids": vacancy.search_ids
            },
            "auto_matching": {
                "enabled": vacancy.auto_matching_enabled,
                "candidates_found": auto_match_count,
                "last_run": last_auto_match
            }
        }
    
    async def get_hiring_funnel(
        self,
        user: Optional[User] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get hiring funnel metrics"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        query = {}
        if user and not user.can_view_all_searches():
            # Get candidates from user's vacancies
            vacancies = await Vacancy.find({"user_id": str(user.id)}).to_list()
            vacancy_ids = [str(v.id) for v in vacancies]
            query = {"vacancy_ids": {"$in": vacancy_ids}}
        
        # Count by status
        funnel = {
            "new": await Candidate.find({**query, "status": "new"}).count(),
            "reviewed": await Candidate.find({**query, "status": "reviewed"}).count(),
            "shortlisted": await Candidate.find({**query, "status": "shortlisted"}).count(),
            "interview_scheduled": await Candidate.find({**query, "status": "interview_scheduled"}).count(),
            "interviewed": await Candidate.find({**query, "status": "interviewed"}).count(),
            "offer_sent": await Candidate.find({**query, "status": "offer_sent"}).count(),
            "hired": await Candidate.find({**query, "status": "hired"}).count(),
            "rejected": await Candidate.find({**query, "status": "rejected"}).count()
        }
        
        # Calculate conversion rates
        total = sum(funnel.values())
        conversions = {}
        if total > 0:
            conversions = {
                "reviewed": (funnel["reviewed"] / total * 100) if total > 0 else 0,
                "shortlisted": (funnel["shortlisted"] / total * 100) if total > 0 else 0,
                "interviewed": (funnel["interviewed"] / total * 100) if total > 0 else 0,
                "hired": (funnel["hired"] / total * 100) if total > 0 else 0
            }
        
        return {
            "funnel": funnel,
            "conversions": conversions,
            "total": total,
            "period_days": days
        }
    
    async def _calculate_avg_time_to_hire(
        self,
        user: Optional[User],
        days: int
    ) -> Optional[float]:
        """Calculate average time to hire"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        query = {"status": "filled", "closed_at": {"$gte": start_date}}
        if user and not user.can_view_all_searches():
            query["user_id"] = str(user.id)
        
        filled_vacancies = await Vacancy.find(query).to_list()
        
        if not filled_vacancies:
            return None
        
        total_days = 0
        count = 0
        
        for vacancy in filled_vacancies:
            if vacancy.closed_at and vacancy.created_at:
                days_diff = (vacancy.closed_at - vacancy.created_at).days
                total_days += days_diff
                count += 1
        
        return total_days / count if count > 0 else None
    
    async def _calculate_avg_ai_score_hired(
        self,
        user: Optional[User]
    ) -> Optional[float]:
        """Calculate average AI score of hired candidates"""
        query = {"status": "hired"}
        
        # Filter by user's vacancies if needed
        if user and not user.can_view_all_searches():
            vacancies = await Vacancy.find({"user_id": str(user.id)}).to_list()
            vacancy_ids = [str(v.id) for v in vacancies]
            query = {"status": "hired", "vacancy_ids": {"$in": vacancy_ids}}
        
        hired_candidates = await Candidate.find(query).to_list()
        
        ai_scores = []
        for candidate in hired_candidates:
            resume = await Resume.get(candidate.resume_id)
            if resume and resume.ai_score:
                ai_scores.append(resume.ai_score)
        
        return sum(ai_scores) / len(ai_scores) if ai_scores else None
    
    async def _get_top_skills(self, days: int) -> List[Dict[str, Any]]:
        """Get top skills from resumes"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get recent resumes
        resumes = await Resume.find({
            "created_at": {"$gte": start_date},
            "analyzed": True
        }).limit(1000).to_list()
        
        # Extract skills
        skills_count = {}
        for resume in resumes:
            if resume.raw_data and "skills" in resume.raw_data:
                skills = resume.raw_data["skills"]
                if isinstance(skills, list):
                    for skill in skills:
                        skill_name = skill.get("name", "") if isinstance(skill, dict) else str(skill)
                        if skill_name:
                            skills_count[skill_name] = skills_count.get(skill_name, 0) + 1
        
        # Sort and return top 10
        top_skills = sorted(skills_count.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return [{"skill": skill, "count": count} for skill, count in top_skills]
    
    async def _get_city_distribution(
        self,
        user: Optional[User]
    ) -> Dict[str, int]:
        """Get candidate distribution by city"""
        query = {}
        if user and not user.can_view_all_searches():
            # Filter by user's searches
            searches = await Search.find({"user_id": str(user.id)}).to_list()
            search_ids = [str(s.id) for s in searches]
            query = {"search_id": {"$in": search_ids}}
        
        resumes = await Resume.find(query).limit(1000).to_list()
        
        city_count = {}
        for resume in resumes:
            if resume.city:
                city_count[resume.city] = city_count.get(resume.city, 0) + 1
        
        return city_count
    
    async def _get_auto_matching_stats(
        self,
        user: Optional[User],
        days: int
    ) -> Dict[str, Any]:
        """Get auto-matching statistics"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        query = {
            "auto_matching_enabled": True,
            "last_auto_match_at": {"$gte": start_date}
        }
        
        if user and not user.can_view_all_searches():
            query["user_id"] = str(user.id)
        
        vacancies = await Vacancy.find(query).to_list()
        
        total_candidates = sum(v.auto_match_count for v in vacancies)
        
        return {
            "active_vacancies": len(vacancies),
            "total_candidates_found": total_candidates,
            "avg_candidates_per_vacancy": total_candidates / len(vacancies) if vacancies else 0
        }


# Global service instance
analytics_service = AnalyticsService()
