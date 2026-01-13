"""AI service for resume analysis"""
from typing import List, Dict, Any, Optional
import random
from app.infrastructure.external.cloudflare_client import cloudflare_client
from app.core.logging import get_logger
from app.core.exceptions import ExternalServiceException
from app.core.metrics import track_resume_analyzed


logger = get_logger(__name__)


class AIService:
    """Service for AI-powered resume analysis"""
    
    async def extract_concepts(self, query: str) -> List[List[str]]:
        """
        Extract concepts from search query
        Returns: List of concept arrays, e.g. [["concept1", "synonym1"], ["concept2", "synonym2"]]
        """
        try:
            concepts = await cloudflare_client.extract_concepts(query)
            logger.info("Concepts extracted via Cloudflare Worker", query=query, count=len(concepts))
            return concepts
            
        except ExternalServiceException as e:
            logger.warning("Cloudflare Worker unavailable, using fallback", error=str(e))
            return self._fallback_extract_concepts(query)
        except Exception as e:
            logger.error("Unexpected error extracting concepts", error=str(e), exc_info=True)
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
        concepts: List[List[str]]
    ) -> Dict[str, Any]:
        """
        Analyze resume using AI
        Returns: {
            "score": int (1-10),
            "summary": str,
            "questions": List[str],
            "ai_generated_detected": bool
        }
        """
        try:
            result = await cloudflare_client.analyze_resume(resume_text, concepts)
            track_resume_analyzed("ai")
            logger.info("Resume analyzed via Cloudflare Worker", score=result.get("score"))
            return result
            
        except ExternalServiceException as e:
            logger.warning("Cloudflare Worker unavailable, using fallback", error=str(e))
            result = self._fallback_analyze_resume(resume_text, concepts)
            track_resume_analyzed("fallback")
            return result
        except Exception as e:
            logger.error("Unexpected error analyzing resume", error=str(e), exc_info=True)
            result = self._fallback_analyze_resume(resume_text, concepts)
            track_resume_analyzed("fallback")
            return result
    
    def _fallback_analyze_resume(
        self,
        resume_text: str,
        concepts: List[List[str]]
    ) -> Dict[str, Any]:
        """Fallback resume analysis (rule-based scoring)"""
        text_lower = resume_text.lower()
        
        # Simple scoring based on concept matches
        score = 5  # Base score
        concept_keywords = []
        for concept_group in concepts:
            concept_keywords.extend([c.lower() for c in concept_group])
        
        # Count concept matches
        matches = sum(1 for keyword in concept_keywords if keyword in text_lower)
        if matches > 0:
            score = min(10, 5 + (matches * 2))
        
        # Check for common skills/experience indicators
        if any(word in text_lower for word in ["опыт", "experience", "стаж"]):
            score = min(10, score + 1)
        
        if any(word in text_lower for word in ["образование", "education", "университет"]):
            score = min(10, score + 1)
        
        # Generate summary
        summary = f"Резюме содержит {matches} совпадений с ключевыми концепциями. "
        if score >= 8:
            summary += "Высокий уровень соответствия требованиям."
        elif score >= 6:
            summary += "Средний уровень соответствия требованиям."
        else:
            summary += "Низкий уровень соответствия требованиям."
        
        # Generate questions
        questions = [
            "Какой опыт работы у кандидата?",
            "Какие технологии использует кандидат?",
            "Готов ли кандидат к переезду?"
        ]
        
        # Simple AI-generated detection (very basic)
        ai_generated_detected = len(resume_text) > 5000 and "chatgpt" in text_lower
        
        result = {
            "score": max(1, min(10, score)),
            "summary": summary,
            "questions": questions,
            "ai_generated_detected": ai_generated_detected
        }
        
        logger.info("Using fallback resume analysis", score=result["score"])
        return result


# Global service instance
ai_service = AIService()
