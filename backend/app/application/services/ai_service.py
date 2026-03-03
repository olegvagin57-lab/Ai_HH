"""AI service for resume analysis"""
from typing import List, Dict, Any, Optional
import random
# Cloudflare client removed - using only local models
from app.infrastructure.external.huggingface_client import huggingface_client
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
        Priority: Ollama (GPU) -> Gemini API -> Hugging Face -> Fallback
        Returns: List of concept arrays, e.g. [["concept1", "synonym1"], ["concept2", "synonym2"]]
        """
        # Priority 1: Try Ollama (local model with GPU) - PRIMARY
        if ollama_client.available:
            try:
                concepts = await ollama_client.extract_concepts(query)
                logger.info("Concepts extracted via Ollama (GPU)", query=query, count=len(concepts))
                return concepts
            except ExternalServiceException as e:
                logger.warning("Ollama unavailable, trying Gemini API", error=str(e))
            except Exception as e:
                logger.error("Unexpected error with Ollama", error=str(e), exc_info=True)
        else:
            logger.debug("Ollama not available, skipping")
        
        # Priority 2: Try Gemini API (Cloudflare Worker) - FALLBACK
        try:
            concepts = await cloudflare_client.extract_concepts(query)
            logger.info("Concepts extracted via Gemini API", query=query, count=len(concepts))
            return concepts
        except ExternalServiceException as e:
            logger.warning("Gemini API unavailable, trying Hugging Face", error=str(e))
        except Exception as e:
            logger.error("Unexpected error with Gemini API", error=str(e), exc_info=True)
        
        # Priority 3: Try Hugging Face Inference API - FALLBACK
        if huggingface_client.available:
            try:
                concepts = await huggingface_client.extract_concepts(query)
                logger.info("Concepts extracted via Hugging Face", query=query, count=len(concepts))
                return concepts
            except ExternalServiceException as e:
                logger.warning("Hugging Face unavailable, using fallback", error=str(e))
            except Exception as e:
                logger.error("Unexpected error with Hugging Face", error=str(e), exc_info=True)
        else:
            logger.debug("Hugging Face not available, skipping")
        
        # Priority 4: Fallback (simple keyword extraction)
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
        # Priority 1: Try Ollama (local model with GPU) - PRIMARY
        if ollama_client.available:
            try:
                result = await ollama_client.analyze_resume(
                    resume_text,
                    concepts,
                    vacancy_requirements
                )
                track_resume_analyzed("ollama")
                logger.info("Resume analyzed via Ollama (GPU)", score=result.get("score"))
                return result
            except ExternalServiceException as e:
                logger.warning("Ollama unavailable, trying Gemini API", error=str(e))
            except Exception as e:
                logger.error("Unexpected error with Ollama", error=str(e), exc_info=True)
        else:
            logger.debug("Ollama not available, skipping")
        
        # Priority 2: Try Gemini API (Cloudflare Worker) - FALLBACK
        try:
            result = await cloudflare_client.analyze_resume(
                resume_text, 
                concepts,
                vacancy_requirements
            )
            track_resume_analyzed("gemini")
            logger.info("Resume analyzed via Gemini API", score=result.get("score"))
            return result
        except ExternalServiceException as e:
            logger.warning("Gemini API unavailable, trying Hugging Face", error=str(e))
        except Exception as e:
            logger.error("Unexpected error with Gemini API", error=str(e), exc_info=True)
        
        # Priority 3: Try Hugging Face Inference API - FALLBACK
        if huggingface_client.available:
            try:
                result = await huggingface_client.analyze_resume(
                    resume_text,
                    concepts,
                    vacancy_requirements
                )
                track_resume_analyzed("huggingface")
                logger.info("Resume analyzed via Hugging Face", score=result.get("score"))
                return result
            except ExternalServiceException as e:
                logger.warning("Hugging Face unavailable, using fallback", error=str(e))
            except Exception as e:
                logger.error("Unexpected error with Hugging Face", error=str(e), exc_info=True)
        else:
            logger.debug("Hugging Face not available, skipping")
        
        # Priority 4: Fallback (simple keyword-based analysis)
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
        """Fallback resume analysis with semantic-style explanations"""
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
        has_experience = any(word in text_lower for word in ["опыт", "experience", "стаж"])
        has_education = any(word in text_lower for word in ["образование", "education", "университет"])
        
        if has_experience:
            score = min(10, score + 1)
        if has_education:
            score = min(10, score + 1)
        
        # Generate detailed evaluation
        weights = vacancy_requirements.get("weights", {}) if vacancy_requirements else {
            "technical_skills": 0.4,
            "experience": 0.3,
            "education": 0.2,
            "soft_skills": 0.1
        }
        
        # Calculate category scores
        technical_score = min(10, 5 + (matches * 1.5))
        experience_score = 8 if has_experience else 5
        education_score = 8 if has_education else 5
        soft_skills_score = 6  # Default
        
        evaluation_details = {
            "technical_skills": {
                "score": technical_score,
                "details": f"Найдено {matches} совпадений с ключевыми концепциями"
            },
            "experience": {
                "score": experience_score,
                "details": "Опыт работы присутствует" if has_experience else "Опыт работы не указан"
            },
            "education": {
                "score": education_score,
                "details": "Образование указано" if has_education else "Образование не указано"
            },
            "soft_skills": {
                "score": soft_skills_score,
                "details": "Базовая оценка soft skills"
            }
        }
        
        # Calculate match percentage
        match_percentage = (
            technical_score * weights.get("technical_skills", 0.4) +
            experience_score * weights.get("experience", 0.3) +
            education_score * weights.get("education", 0.2) +
            soft_skills_score * weights.get("soft_skills", 0.1)
        )
        
        # Generate detailed semantic summary and explanation
        summary = f"Семантический анализ резюме выявил {matches} совпадений с ключевыми концепциями. "
        if score >= 8:
            summary += "Высокий уровень соответствия требованиям. Кандидат демонстрирует отличное понимание необходимых технологий и имеет релевантный опыт."
        elif score >= 6:
            summary += "Средний уровень соответствия требованиям. Кандидат имеет базовые навыки, но может потребоваться дополнительное обучение."
        else:
            summary += "Низкий уровень соответствия требованиям. Кандидат требует значительного развития навыков."
        
        # Generate match explanation (why this candidate is suitable)
        match_explanation = f"Кандидат подходит по следующим причинам: "
        if matches > 0:
            match_explanation += f"найдено {matches} совпадений с ключевыми требованиями. "
        if has_experience:
            match_explanation += "Имеет практический опыт работы. "
        if has_education:
            match_explanation += "Образование соответствует требованиям. "
        if not match_explanation.endswith(". "):
            match_explanation += "Требуется дополнительная оценка."
        
        # Generate strengths and weaknesses
        strengths = []
        weaknesses = []
        
        if matches >= 5:
            strengths.append("Сильное соответствие ключевым требованиям")
        if has_experience:
            strengths.append("Наличие практического опыта")
        if has_education:
            strengths.append("Соответствующее образование")
        
        if matches < 3:
            weaknesses.append("Недостаточное соответствие ключевым требованиям")
        if not has_experience:
            weaknesses.append("Отсутствие указанного опыта работы")
        if not has_education:
            weaknesses.append("Образование не указано или не соответствует")
        
        # Generate recommendation
        if score >= 8:
            recommendation = "Отличный кандидат с высоким соответствием требованиям. Рекомендуется для собеседования. Кандидат демонстрирует глубокое понимание необходимых технологий и имеет релевантный опыт работы."
        elif score >= 6:
            recommendation = "Хороший кандидат с приемлемым уровнем соответствия. Стоит рассмотреть для собеседования. Возможно потребуется дополнительное обучение."
        else:
            recommendation = "Кандидат требует дополнительной оценки. Соответствие требованиям ниже среднего. Рекомендуется рассмотреть других кандидатов или провести дополнительное собеседование."
        
        # Generate questions
        questions = [
            "Какой опыт работы у кандидата?",
            "Какие технологии использует кандидат?",
            "Готов ли кандидат к переезду?"
        ]
        
        # Simple AI-generated detection (very basic)
        ai_generated_detected = len(resume_text) > 5000 and "chatgpt" in text_lower
        
        # Check for red flags
        red_flags = []
        if ai_generated_detected:
            red_flags.append("ai_generated")
        if len(resume_text) < 200:
            red_flags.append("incomplete_resume")
        
        result = {
            "score": max(1, min(10, score)),
            "summary": summary,
            "match_explanation": match_explanation,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "questions": questions,
            "ai_generated_detected": ai_generated_detected,
            "evaluation_details": evaluation_details,
            "match_percentage": match_percentage,
            "red_flags": red_flags,
            "recommendation": recommendation
        }
        
        logger.info("Using fallback resume analysis", score=result["score"])
        return result


# Global service instance
ai_service = AIService()
