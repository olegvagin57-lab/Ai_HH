"""Evaluation service for detailed resume analysis"""
from typing import Dict, Any, Optional, List
from app.application.services.ai_service import ai_service
from app.domain.entities.search import Resume
from app.domain.entities.evaluation_criteria import EvaluationCriteria
from app.core.logging import get_logger


logger = get_logger(__name__)


class EvaluationService:
    """Service for evaluating resumes with detailed criteria"""
    
    async def evaluate_resume(
        self,
        resume: Resume,
        concepts: List[List[str]],
        criteria: Optional[EvaluationCriteria] = None
    ) -> Dict[str, Any]:
        """
        Evaluate resume with detailed analysis
        
        Returns:
            {
                "score": int (1-10),
                "summary": str,
                "questions": List[str],
                "ai_generated_detected": bool,
                "evaluation_details": {
                    "technical_skills": {"score": float, "details": str},
                    "experience": {"score": float, "details": str},
                    "education": {"score": float, "details": str},
                    "soft_skills": {"score": float, "details": str}
                },
                "match_percentage": float (0-100),
                "red_flags": List[str]
            }
        """
        # Prepare vacancy requirements if criteria provided
        vacancy_requirements = None
        if criteria:
            vacancy_requirements = {
                "weights": criteria.weights,
                "technical_skills": criteria.technical_skills,
                "experience": criteria.experience,
                "education": criteria.education,
                "soft_skills": criteria.soft_skills,
                "red_flags": criteria.red_flags
            }
        
        # Get resume text from raw_data
        resume_text = self._extract_resume_text(resume)
        
        # Analyze with AI
        analysis_result = await ai_service.analyze_resume(
            resume_text=resume_text,
            concepts=concepts,
            vacancy_requirements=vacancy_requirements
        )
        
        # Calculate match percentage if evaluation_details available
        match_percentage = None
        if analysis_result.get("evaluation_details") and criteria:
            match_percentage = self._calculate_match_percentage(
                analysis_result["evaluation_details"],
                criteria.weights
            )
            analysis_result["match_percentage"] = match_percentage
        
        # Enhance summary with semantic explanation if not provided
        if not analysis_result.get("match_explanation") and analysis_result.get("summary"):
            analysis_result["match_explanation"] = analysis_result["summary"]
        
        # Ensure recommendation is present
        if not analysis_result.get("recommendation"):
            score = analysis_result.get("score", 5)
            if score >= 8:
                analysis_result["recommendation"] = "Отличный кандидат с высоким соответствием требованиям. Рекомендуется для собеседования."
            elif score >= 6:
                analysis_result["recommendation"] = "Хороший кандидат с приемлемым уровнем соответствия. Стоит рассмотреть."
            else:
                analysis_result["recommendation"] = "Кандидат требует дополнительной оценки. Соответствие требованиям ниже среднего."
        
        logger.info(
            "Resume evaluated with semantic analysis",
            resume_id=str(resume.id),
            score=analysis_result.get("score"),
            match_percentage=match_percentage,
            has_explanation=bool(analysis_result.get("match_explanation"))
        )
        
        return analysis_result
    
    def _extract_resume_text(self, resume: Resume) -> str:
        """Extract text from resume raw_data"""
        text_parts = []
        
        if resume.name:
            text_parts.append(f"Имя: {resume.name}")
        if resume.title:
            text_parts.append(f"Должность: {resume.title}")
        if resume.city:
            text_parts.append(f"Город: {resume.city}")
        if resume.age:
            text_parts.append(f"Возраст: {resume.age}")
        
        # Extract from raw_data
        raw = resume.raw_data or {}
        
        # Add experience
        if "experience" in raw:
            if isinstance(raw["experience"], list):
                for exp in raw["experience"]:
                    if isinstance(exp, dict):
                        text_parts.append(f"Опыт: {exp.get('position', '')} - {exp.get('description', '')}")
            elif isinstance(raw["experience"], str):
                text_parts.append(f"Опыт: {raw['experience']}")
        
        # Add skills
        if "skills" in raw:
            if isinstance(raw["skills"], list):
                text_parts.append(f"Навыки: {', '.join(raw['skills'])}")
            elif isinstance(raw["skills"], str):
                text_parts.append(f"Навыки: {raw['skills']}")
        
        # Add education
        if "education" in raw:
            if isinstance(raw["education"], list):
                for edu in raw["education"]:
                    if isinstance(edu, dict):
                        text_parts.append(f"Образование: {edu.get('institution', '')} - {edu.get('degree', '')}")
            elif isinstance(raw["education"], str):
                text_parts.append(f"Образование: {raw['education']}")
        
        # Add any text fields
        for key in ["description", "about", "summary", "additional_info"]:
            if key in raw and raw[key]:
                text_parts.append(str(raw[key]))
        
        return "\n".join(text_parts)
    
    def _calculate_match_percentage(
        self,
        evaluation_details: Dict[str, Any],
        weights: Dict[str, float]
    ) -> float:
        """Calculate overall match percentage from category scores and weights"""
        if not evaluation_details:
            return 0.0
        
        total_score = 0.0
        total_weight = 0.0
        
        categories = ["technical_skills", "experience", "education", "soft_skills"]
        
        for category in categories:
            if category in evaluation_details:
                category_data = evaluation_details[category]
                if isinstance(category_data, dict) and "score" in category_data:
                    score = float(category_data["score"])
                    weight = weights.get(category, 0.0)
                    total_score += score * weight
                    total_weight += weight
        
        if total_weight == 0:
            return 0.0
        
        # Normalize to 0-100
        match_percentage = (total_score / total_weight) * 10.0  # Convert from 0-10 to 0-100
        return min(100.0, max(0.0, match_percentage))
    
    async def get_default_criteria(self) -> EvaluationCriteria:
        """Get default evaluation criteria"""
        criteria = await EvaluationCriteria.find_one({"vacancy_id": None})
        if not criteria:
            # Create default criteria
            criteria = EvaluationCriteria(
                vacancy_id=None,
                name="Default Criteria",
                weights={
                    "technical_skills": 0.4,
                    "experience": 0.3,
                    "education": 0.2,
                    "soft_skills": 0.1
                }
            )
            await criteria.insert()
        
        return criteria


# Global service instance
evaluation_service = EvaluationService()
