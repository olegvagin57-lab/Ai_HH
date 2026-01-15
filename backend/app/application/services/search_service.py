"""Search service for resume search and analysis"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.domain.entities.search import Search, Resume, Concept
from app.domain.entities.user import User
from app.infrastructure.external.hh_client import hh_client
from app.application.services.ai_service import ai_service
from app.application.services.evaluation_service import evaluation_service
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
        # Validate search_id format (ObjectId)
        from bson import ObjectId
        try:
            ObjectId(search_id)
        except Exception:
            raise ValidationException(f"Invalid search ID format: {search_id}")
        
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
    
    async def analyze_resume_with_ai(
        self, 
        resume: Resume, 
        concepts: List[List[str]],
        criteria: Optional[Any] = None
    ) -> None:
        """Analyze resume with AI and detailed evaluation"""
        # Use evaluation service for detailed analysis
        evaluation_result = await evaluation_service.evaluate_resume(
            resume=resume,
            concepts=concepts,
            criteria=criteria
        )
        
        # Update resume with AI results
        resume.ai_score = evaluation_result["score"]
        resume.ai_summary = evaluation_result["summary"]
        resume.ai_questions = evaluation_result["questions"]
        resume.ai_generated_detected = evaluation_result["ai_generated_detected"]
        resume.analyzed = True
        
        # Store detailed evaluation with semantic explanations
        resume.evaluation_details = evaluation_result.get("evaluation_details")
        resume.match_percentage = evaluation_result.get("match_percentage")
        resume.match_explanation = evaluation_result.get("match_explanation")
        resume.strengths = evaluation_result.get("strengths", [])
        resume.weaknesses = evaluation_result.get("weaknesses", [])
        resume.recommendation = evaluation_result.get("recommendation")
        resume.red_flags = evaluation_result.get("red_flags", [])
        
        await resume.save()
        
        logger.info(
            "Resume analyzed with AI and detailed evaluation",
            resume_id=str(resume.id),
            score=resume.ai_score,
            match_percentage=resume.match_percentage
        )
    
    async def get_search_resumes(
        self,
        search_id: str,
        user: User,
        page: int = 1,
        page_size: int = 20,
        sort_by: str = "ai_score",
        sort_order: str = "desc",
        # Filter parameters
        min_salary: Optional[int] = None,
        max_salary: Optional[int] = None,
        min_age: Optional[int] = None,
        max_age: Optional[int] = None,
        min_experience_years: Optional[int] = None,
        skills: Optional[List[str]] = None,
        education: Optional[str] = None,
        relocation_ready: Optional[bool] = None,
        min_ai_score: Optional[int] = None,
        max_ai_score: Optional[int] = None,
        min_match_percentage: Optional[float] = None,
        max_match_percentage: Optional[float] = None,
        candidate_status: Optional[str] = None,
        has_red_flags: Optional[bool] = None
    ) -> Dict[str, Any]:
        """Get resumes for a search with pagination, sorting, and filtering"""
        search = await self.get_search(search_id, user)
        
        skip = (page - 1) * page_size
        
        # Build query with filters
        query_dict = {"search_id": str(search.id)}
        
        # Salary filter
        if min_salary is not None or max_salary is not None:
            salary_filter = {}
            if min_salary is not None:
                salary_filter["$gte"] = min_salary
            if max_salary is not None:
                salary_filter["$lte"] = max_salary
            if salary_filter:
                query_dict["salary"] = salary_filter
        
        # Age filter
        if min_age is not None or max_age is not None:
            age_filter = {}
            if min_age is not None:
                age_filter["$gte"] = min_age
            if max_age is not None:
                age_filter["$lte"] = max_age
            if age_filter:
                query_dict["age"] = age_filter
        
        # AI Score filter
        if min_ai_score is not None or max_ai_score is not None:
            ai_score_filter = {}
            if min_ai_score is not None:
                ai_score_filter["$gte"] = min_ai_score
            if max_ai_score is not None:
                ai_score_filter["$lte"] = max_ai_score
            if ai_score_filter:
                query_dict["ai_score"] = ai_score_filter
        
        # Match percentage filter
        if min_match_percentage is not None or max_match_percentage is not None:
            match_filter = {}
            if min_match_percentage is not None:
                match_filter["$gte"] = min_match_percentage
            if max_match_percentage is not None:
                match_filter["$lte"] = max_match_percentage
            if match_filter:
                query_dict["match_percentage"] = match_filter
        
        # Red flags filter
        if has_red_flags is not None:
            if has_red_flags:
                query_dict["red_flags"] = {"$ne": []}  # Has red flags
            else:
                query_dict["$or"] = [
                    {"red_flags": {"$exists": False}},
                    {"red_flags": []}
                ]  # No red flags
        
        # Build base query
        query = Resume.find(query_dict)
        
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
        elif sort_by == "match_percentage":
            if sort_order == "desc":
                resumes = await query.sort(-Resume.match_percentage).skip(skip).limit(page_size).to_list()
            else:
                resumes = await query.sort(Resume.match_percentage).skip(skip).limit(page_size).to_list()
        elif sort_by == "created_at":
            if sort_order == "desc":
                resumes = await query.sort(-Resume.created_at).skip(skip).limit(page_size).to_list()
            else:
                resumes = await query.sort(Resume.created_at).skip(skip).limit(page_size).to_list()
        else:
            resumes = await query.skip(skip).limit(page_size).to_list()
        
        # Apply filters that require raw_data inspection (post-filtering)
        filtered_resumes = []
        for resume in resumes:
            # Skills filter
            if skills:
                resume_skills = self._extract_skills(resume)
                if not any(skill.lower() in [s.lower() for s in resume_skills] for skill in skills):
                    continue
            
            # Experience years filter
            if min_experience_years is not None:
                experience_years = self._calculate_experience_years(resume)
                if experience_years < min_experience_years:
                    continue
            
            # Education filter
            if education:
                resume_education = self._extract_education(resume)
                if education.lower() not in resume_education.lower():
                    continue
            
            # Relocation ready filter
            if relocation_ready is not None:
                is_relocation_ready = self._check_relocation_ready(resume)
                if is_relocation_ready != relocation_ready:
                    continue
            
            filtered_resumes.append(resume)
        
        # Re-count total with filters (approximate, for better performance use aggregation)
        total_query = Resume.find(query_dict)
        total = await total_query.count()
        
        return {
            "resumes": filtered_resumes,
            "total": total,
            "page": page,
            "page_size": page_size
        }
    
    def _extract_skills(self, resume: Resume) -> List[str]:
        """Extract skills from resume"""
        skills = []
        raw_data = resume.raw_data or {}
        
        if "skills" in raw_data:
            if isinstance(raw_data["skills"], list):
                for skill in raw_data["skills"]:
                    if isinstance(skill, dict):
                        skills.append(skill.get("name", ""))
                    elif isinstance(skill, str):
                        skills.append(skill)
            elif isinstance(raw_data["skills"], str):
                skills.append(raw_data["skills"])
        
        return skills
    
    def _calculate_experience_years(self, resume: Resume) -> int:
        """Calculate total years of experience from resume"""
        raw_data = resume.raw_data or {}
        total_years = 0
        
        if "experience" in raw_data:
            if isinstance(raw_data["experience"], list):
                for exp in raw_data["experience"]:
                    if isinstance(exp, dict):
                        # Try to extract years from dates
                        start_date = exp.get("start", "")
                        end_date = exp.get("end", "") or "present"
                        # Simple calculation (can be improved)
                        if start_date:
                            total_years += 1  # Approximate
            elif isinstance(raw_data["experience"], str):
                # Try to parse years from string
                import re
                years_match = re.search(r'(\d+)\s*(?:лет|год|years?)', raw_data["experience"], re.IGNORECASE)
                if years_match:
                    total_years = int(years_match.group(1))
        
        return total_years
    
    def _extract_education(self, resume: Resume) -> str:
        """Extract education information from resume"""
        education_parts = []
        raw_data = resume.raw_data or {}
        
        if "education" in raw_data:
            if isinstance(raw_data["education"], list):
                for edu in raw_data["education"]:
                    if isinstance(edu, dict):
                        education_parts.append(edu.get("institution", ""))
                        education_parts.append(edu.get("degree", ""))
            elif isinstance(raw_data["education"], str):
                education_parts.append(raw_data["education"])
        
        return " ".join(education_parts)
    
    def _check_relocation_ready(self, resume: Resume) -> bool:
        """Check if candidate is ready for relocation"""
        raw_data = resume.raw_data or {}
        
        # Check in various fields
        relocation_keywords = ["готов к переезду", "relocation", "готов переехать", "готовность к переезду"]
        
        for field in ["relocation", "additional_info", "about", "description"]:
            if field in raw_data:
                field_value = str(raw_data[field]).lower()
                if any(keyword in field_value for keyword in relocation_keywords):
                    return True
        
        return False


# Global service instance
search_service = SearchService()
