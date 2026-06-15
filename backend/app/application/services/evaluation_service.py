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
        """
        Build a concise resume summary from available data.
        The HH search-card parser only gives us title, age, and a total-experience string —
        so we make the most of what we have and structure it clearly for the LLM.
        """
        lines = []
        raw = resume.raw_data or {}

        # ── Basic info ─────────────────────────────────────────────────────────
        if resume.title:
            lines.append(f"Должность: {resume.title}")
        if resume.age:
            lines.append(f"Возраст: {resume.age} лет")
        if resume.city:
            lines.append(f"Город: {resume.city}")

        # ── Salary expectation ─────────────────────────────────────────────────
        salary = resume.salary or raw.get("salary", {})
        if isinstance(salary, dict) and salary.get("amount"):
            cur = salary.get("currency", "₽")
            lines.append(f"Желаемая зарплата: {salary['amount']:,} {cur}".replace(",", " "))
        elif isinstance(salary, (int, float)) and salary:
            cur = resume.currency or raw.get("salary", {}).get("currency", "₽")
            lines.append(f"Желаемая зарплата: {int(salary):,} {cur}".replace(",", " "))

        # ── Experience ─────────────────────────────────────────────────────────
        exp_raw = raw.get("experience", [])
        if isinstance(exp_raw, list) and exp_raw:
            exp_texts = []
            for exp in exp_raw:
                if isinstance(exp, dict):
                    parts = []
                    for field in ("position", "employer", "description"):
                        val = exp.get(field, "")
                        if val and str(val).strip():
                            parts.append(str(val).strip())
                    if parts:
                        exp_texts.append(" | ".join(parts))
            if exp_texts:
                lines.append("Опыт работы:")
                for t in exp_texts[:5]:
                    lines.append(f"  - {t}")
        elif isinstance(exp_raw, str) and exp_raw:
            lines.append(f"Общий стаж: {exp_raw}")

        # ── Skills ────────────────────────────────────────────────────────────
        skills_raw = raw.get("skills", [])
        if isinstance(skills_raw, list) and skills_raw:
            names = [s.get("name", "") if isinstance(s, dict) else str(s) for s in skills_raw]
            names = [n for n in names if n]
            if names:
                lines.append(f"Ключевые навыки: {', '.join(names[:20])}")
        elif isinstance(skills_raw, str) and skills_raw:
            lines.append(f"Ключевые навыки: {skills_raw}")

        # ── Education ─────────────────────────────────────────────────────────
        edu_raw = raw.get("education", [])
        if isinstance(edu_raw, list) and edu_raw:
            edu_texts = []
            for edu in edu_raw:
                if isinstance(edu, dict):
                    inst = edu.get("institution") or edu.get("name", "")
                    deg = edu.get("degree") or edu.get("specialization", "")
                    year = edu.get("year", "")
                    text = " — ".join(filter(None, [inst, deg, str(year) if year else ""]))
                    if text.strip():
                        edu_texts.append(text)
            if edu_texts:
                lines.append(f"Образование: {'; '.join(edu_texts[:3])}")
        elif isinstance(edu_raw, str) and edu_raw:
            lines.append(f"Образование: {edu_raw}")

        # ── Free-text description ─────────────────────────────────────────────
        for key in ("description", "about", "summary", "additional_info"):
            val = raw.get(key)
            if val and str(val).strip():
                snippet = str(val).strip()[:400]
                lines.append(f"О себе: {snippet}")
                break

        if not lines:
            lines.append("Резюме не содержит текстовых данных (только заголовок)")

        return "\n".join(lines)
    
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
