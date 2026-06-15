"""AI service for resume analysis.

This project is configured to use ONLY local AI models (via Ollama).
If a local model is not available, the service falls back to a simple heuristic analysis
so the product remains functional without external AI dependencies.
"""
from typing import List, Dict, Any, Optional
import random

from app.infrastructure.external.ollama_client import ollama_client
from app.core.logging import get_logger
from app.core.exceptions import ExternalServiceException
from app.core.metrics import track_resume_analyzed


logger = get_logger(__name__)


class AIService:
    """Service for AI-powered resume analysis"""
    
    async def extract_concepts(self, query: str) -> List[List[str]]:
        """
        Extract concepts from search query
        Priority: Ollama (local) -> Fallback
        Returns: List of concept arrays, e.g. [["concept1", "synonym1"], ["concept2", "synonym2"]]
        """
        # Priority 1: Try Ollama (local) - PRIMARY
        if ollama_client.available:
            try:
                concepts = await ollama_client.extract_concepts(query)
                logger.info("Concepts extracted via Ollama", query=query, count=len(concepts))
                return concepts
            except ExternalServiceException as e:
                logger.warning("Ollama unavailable, using fallback", error=str(e))
            except Exception as e:
                logger.error("Unexpected error with Ollama", error=str(e), exc_info=True)
        else:
            logger.debug("Ollama not available, skipping")
        
        # Fallback (simple keyword extraction)
        logger.info("Using fallback concept extraction", query=query)
        return self._fallback_extract_concepts(query)
    
    def _fallback_extract_concepts(self, query: str) -> List[List[str]]:
        """Fallback concept extraction (simple keyword-based)"""
        # Simple keyword extraction
        words = query.lower().split()
        # Filter common stop words
        stop_words = {"и", "или", "в", "на", "с", "для", "от", "до", "по", "из", "к", "о", "а", "но"}
        keywords = [w for w in words if len(w) > 2 and w not in stop_words]
        
        # Create simple concept pairs
        concepts = [[word, word] for word in keywords[:10]]  # Limit to 10 concepts
        
        logger.info("Using fallback concept extraction", query=query, concepts=len(concepts))
        return concepts
    
    async def analyze_resume(
        self,
        resume_text: str,
        concepts: List[List[str]],
        vacancy_requirements: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze resume using AI with detailed evaluation
        Returns: {
            "score": int (1-10),
            "summary": str,
            "questions": List[str],
            "ai_generated_detected": bool,
            "evaluation_details": Optional[Dict],
            "match_percentage": Optional[float],
            "red_flags": List[str]
        }
        """
        # Priority 1: Try Ollama (local) - PRIMARY
        if ollama_client.available:
            try:
                result = await ollama_client.analyze_resume(
                    resume_text,
                    concepts,
                    vacancy_requirements
                )
                track_resume_analyzed("ollama")
                logger.info("Resume analyzed via Ollama", score=result.get("score"))
                return result
            except ExternalServiceException as e:
                logger.warning("Ollama unavailable, using fallback", error=str(e))
            except (SystemExit, KeyboardInterrupt):
                raise  # Never swallow process-level signals
            except Exception as e:
                # Check if this is a Celery soft-limit signal — don't swallow it
                if "SoftTimeLimitExceeded" in type(e).__name__:
                    raise
                logger.error("Unexpected error with Ollama", error=str(e), exc_info=True)
        else:
            logger.debug("Ollama not available, using fallback")

        # Fallback — Ollama unavailable/failed. Return a conservative placeholder.
        logger.warning("All AI providers unavailable, using fallback analysis")
        result = self._fallback_analyze_resume(resume_text, concepts, vacancy_requirements)
        track_resume_analyzed("fallback")
        return result
    
    def _fallback_analyze_resume(
        self,
        resume_text: str,
        concepts: List[List[str]],
        vacancy_requirements: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Conservative fallback when Ollama is unavailable.
        Returns a low-confidence placeholder — never gives high scores
        so HR managers are not misled by keyword noise.
        Resumes analyzed here are marked for re-analysis once Ollama is back.
        """
        text_lower = resume_text.lower()

        concept_keywords = []
        for group in concepts:
            concept_keywords.extend([c.lower() for c in group])

        matches = sum(1 for kw in concept_keywords if kw in text_lower)
        # Cap at 4 — only Ollama can score higher
        score = min(4, 2 + matches)

        evaluation_details = {
            "technical_skills": {"score": score, "details": "Требуется анализ ИИ"},
            "experience": {"score": score, "details": "Требуется анализ ИИ"},
            "education": {"score": score, "details": "Требуется анализ ИИ"},
            "soft_skills": {"score": score, "details": "Требуется анализ ИИ"},
        }

        result = {
            "score": score,
            "summary": "⚠️ ИИ-анализ недоступен. Оценка предварительная, требует повторного анализа.",
            "match_explanation": (
                f"Автоматический анализ выполнен без ИИ (Ollama недоступна). "
                f"Найдено {matches} поверхностных совпадений по ключевым словам. "
                "Это НЕ является полноценной оценкой соответствия."
            ),
            "strengths": [],
            "weaknesses": ["Анализ выполнен без ИИ — оценка ненадёжна"],
            "questions": ["Требуется повторный анализ с Ollama"],
            "ai_generated_detected": False,
            "evaluation_details": evaluation_details,
            "match_percentage": score * 10.0,
            "red_flags": ["requires_reanalysis"],
            "recommendation": (
                "Анализ выполнен без ИИ и не является достоверным. "
                "Ожидайте повторного анализа или оцените резюме вручную."
            ),
            "interview_focus": "Требуется повторный ИИ-анализ",
            "career_trajectory": "Требуется повторный ИИ-анализ",
        }

        logger.warning("Fallback resume analysis used — score capped at 4", score=score, matches=matches)
        return result


# Global service instance
ai_service = AIService()
