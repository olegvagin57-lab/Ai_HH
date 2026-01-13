"""Search service for resume search and analysis"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.domain.entities.search import Search, Resume, Concept
from app.domain.entities.user import User
from app.infrastructure.external.hh_client import hh_client
from app.application.services.ai_service import ai_service
from app.core.logging import get_logger
from app.core.exceptions import NotFoundException, ValidationException
from app.core.metrics import track_search_created
from app.config import settings


logger = get_logger(__name__)


class SearchService:
    """Service for search operations"""
    
    async def create_search(
        self,
        user: User,
        query: str,
        city: str
    ) -> Search:
        """Create a new search"""
        logger.info("create_search service called", 
                   user_id=str(user.id),
                   query=query[:50] if query else None,
                   city=city)
        
        try:
            # Validate user can create searches
            logger.debug("Checking user permissions", user_id=str(user.id))
            if not user.can_create_searches():
                logger.warning("User does not have permission to create searches", 
                             user_id=str(user.id),
                             roles=user.role_names)
                raise ValidationException("User does not have permission to create searches")
            
            logger.debug("User has permission, creating search record")
            # Create search record
            search = Search(
                user_id=str(user.id),
                query=query,
                city=city,
                status="pending"
            )
            logger.debug("Saving search to database")
            await search.create()
            
            logger.info("Search created successfully", 
                       search_id=str(search.id), 
                       user_id=str(user.id),
                       status=search.status)
            track_search_created("created")
            
            return search
        except Exception as e:
            logger.error("Error in create_search service", 
                        error=str(e),
                        error_type=type(e).__name__,
                        exc_info=True)
            raise
    
    async def get_search(self, search_id: str, user: User) -> Search:
        """Get search by ID"""
        search = await Search.get(search_id)
        if not search:
            raise NotFoundException("Search not found")
        
        # Check permissions
        if str(search.user_id) != str(user.id) and not user.can_view_all_searches():
            raise ValidationException("Access denied")
        
        return search
    
    async def extract_concepts_from_query(self, query: str) -> Concept:
        """Extract concepts from search query"""
        concepts_list = await ai_service.extract_concepts(query)
        
        # Create or update concept record
        concept = Concept(
            search_id="",  # Will be updated after search creation
            concepts=concepts_list
        )
        
        return concept
    
    async def preliminary_scoring(
        self,
        resume_data: Dict[str, Any],
        concepts: List[List[str]]
    ) -> float:
        """Calculate preliminary score for a resume"""
        score = 5.0  # Base score
        
        # Extract resume text
        resume_text = ""
        if "title" in resume_data:
            resume_text += str(resume_data["title"]) + " "
        if "experience" in resume_data:
            for exp in resume_data["experience"]:
                if isinstance(exp, dict):
                    resume_text += str(exp.get("position", "")) + " "
                    resume_text += str(exp.get("description", "")) + " "
        if "skills" in resume_data:
            for skill in resume_data["skills"]:
                if isinstance(skill, dict):
                    resume_text += str(skill.get("name", "")) + " "
        
        resume_text = resume_text.lower()
        
        # Count concept matches
        concept_keywords = []
        for concept_group in concepts:
            concept_keywords.extend([c.lower() for c in concept_group])
        
        matches = sum(1 for keyword in concept_keywords if keyword in resume_text)
        if matches > 0:
            score = min(10.0, 5.0 + (matches * 0.5))
        
        # Bonus for experience
        if "experience" in resume_data and len(resume_data["experience"]) > 0:
            score = min(10.0, score + 1.0)
        
        # Bonus for skills
        if "skills" in resume_data and len(resume_data["skills"]) > 3:
            score = min(10.0, score + 0.5)
        
        return round(score, 2)
    
    async def process_resume_from_hh(
        self,
        search: Search,
        resume_data: Dict[str, Any],
        concepts: List[List[str]]
    ) -> Resume:
        """Process a single resume from HeadHunter"""
        # Calculate preliminary score
        preliminary_score = await self.preliminary_scoring(resume_data, concepts)
        
        # Create resume record
        resume = Resume(
            search_id=str(search.id),
            hh_id=str(resume_data.get("id", "")),
            name=f"{resume_data.get('first_name', '')} {resume_data.get('last_name', '')}".strip(),
            age=resume_data.get("age"),
            city=resume_data.get("area", {}).get("name") if isinstance(resume_data.get("area"), dict) else None,
            title=resume_data.get("title"),
            salary=resume_data.get("salary", {}).get("amount") if isinstance(resume_data.get("salary"), dict) else None,
            currency=resume_data.get("salary", {}).get("currency") if isinstance(resume_data.get("salary"), dict) else None,
            raw_data=resume_data,
            preliminary_score=preliminary_score,
            analyzed=False
        )
        
        await resume.create()
        
        return resume
    
    async def analyze_resume_with_ai(self, resume: Resume, concepts: List[List[str]]) -> None:
        """Analyze resume with AI"""
        # Build resume text from raw data
        resume_text_parts = []
        
        if resume.title:
            resume_text_parts.append(f"Должность: {resume.title}")
        
        if resume.raw_data.get("experience"):
            resume_text_parts.append("Опыт работы:")
            for exp in resume.raw_data["experience"]:
                if isinstance(exp, dict):
                    position = exp.get("position", "")
                    company = exp.get("company", "")
                    description = exp.get("description", "")
                    resume_text_parts.append(f"- {position} в {company}: {description}")
        
        if resume.raw_data.get("skills"):
            skills = [s.get("name", "") if isinstance(s, dict) else str(s) for s in resume.raw_data["skills"]]
            resume_text_parts.append(f"Навыки: {', '.join(skills)}")
        
        resume_text = "\n".join(resume_text_parts)
        
        # Analyze with AI
        ai_result = await ai_service.analyze_resume(resume_text, concepts)
        
        # Update resume with AI results
        resume.ai_score = ai_result["score"]
        resume.ai_summary = ai_result["summary"]
        resume.ai_questions = ai_result["questions"]
        resume.ai_generated_detected = ai_result["ai_generated_detected"]
        resume.analyzed = True
        
        await resume.save()
        
        logger.info("Resume analyzed with AI", resume_id=str(resume.id), score=resume.ai_score)
    
    async def get_search_resumes(
        self,
        search_id: str,
        user: User,
        page: int = 1,
        page_size: int = 20,
        sort_by: str = "ai_score",
        sort_order: str = "desc"
    ) -> Dict[str, Any]:
        """Get resumes for a search with pagination and sorting"""
        search = await self.get_search(search_id, user)
        
        skip = (page - 1) * page_size
        
        # Build sort criteria
        sort_field = sort_by
        if sort_order == "desc":
            sort_field = f"-{sort_field}"
        
        # Query resumes
        query = Resume.find({"search_id": str(search.id)})
        
        # Apply sorting
        if sort_by == "ai_score":
            if sort_order == "desc":
                resumes = await query.sort(-Resume.ai_score).skip(skip).limit(page_size).to_list()
            else:
                resumes = await query.sort(Resume.ai_score).skip(skip).limit(page_size).to_list()
        elif sort_by == "preliminary_score":
            if sort_order == "desc":
                resumes = await query.sort(-Resume.preliminary_score).skip(skip).limit(page_size).to_list()
            else:
                resumes = await query.sort(Resume.preliminary_score).skip(skip).limit(page_size).to_list()
        else:
            resumes = await query.skip(skip).limit(page_size).to_list()
        
        total = await Resume.find({"search_id": str(search.id)}).count()
        
        return {
            "resumes": resumes,
            "total": total,
            "page": page,
            "page_size": page_size
        }


# Global service instance
search_service = SearchService()
