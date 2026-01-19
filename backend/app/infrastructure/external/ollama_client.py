"""Ollama client for local AI analysis"""
import asyncio
from typing import Optional, Dict, Any, List
import httpx
import json
from app.config import settings
from app.core.logging import get_logger
from app.core.exceptions import ExternalServiceException


logger = get_logger(__name__)


class OllamaClient:
    """Client for Ollama local AI models"""
    
    def __init__(self):
        # Use settings from config (supports OLLAMA_BASE_URL and OLLAMA_URL)
        self.base_url = getattr(settings, 'ollama_base_url', None) or getattr(settings, 'ollama_url', 'http://localhost:11434')
        self.model = getattr(settings, 'ollama_model', 'mistral')
        self.timeout = 60.0  # Longer timeout for local models
        self.available = False
        self._check_availability()
    
    def _check_availability(self):
        """Check if Ollama is available (synchronous check on init)"""
        try:
            # Try to ping Ollama synchronously (only on init)
            import httpx
            response = httpx.get(f"{self.base_url}/api/tags", timeout=2.0)
            if response.status_code == 200:
                self.available = True
                logger.info("Ollama is available", url=self.base_url, model=self.model)
            else:
                logger.debug("Ollama not available", status=response.status_code)
                self.available = False
        except Exception as e:
            logger.debug("Ollama not available", error=str(e))
            self.available = False
    
    async def _call_model(self, prompt: str) -> str:
        """Call Ollama model with prompt"""
        if not self.available:
            raise ExternalServiceException(
                "ollama",
                "Ollama is not available. Make sure Ollama is running and model is installed."
            )
        
        url = f"{self.base_url}/api/generate"
        data = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
            }
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=data)
                response.raise_for_status()
                result = response.json()
                return result.get("response", "")
        except httpx.TimeoutException:
            raise ExternalServiceException(
                "ollama",
                f"Ollama request timeout after {self.timeout}s"
            )
        except httpx.HTTPStatusError as e:
            raise ExternalServiceException(
                "ollama",
                f"Ollama HTTP error: {e.response.status_code} - {e.response.text}"
            )
        except Exception as e:
            raise ExternalServiceException(
                "ollama",
                f"Ollama request failed: {str(e)}"
            )
    
    async def extract_concepts(self, query: str) -> List[List[str]]:
        """
        Extract concepts from search query using Ollama
        Returns: List of concept arrays, e.g. [["concept1", "synonym1"], ["concept2", "synonym2"]]
        """
        prompt = f"""Извлеки ключевые концепты и их синонимы из следующего запроса на русском языке.
Верни результат ТОЛЬКО в формате JSON массива массивов, где каждый внутренний массив содержит концепт и его синонимы.
Пример: [["python", "питон"], ["разработчик", "developer", "программист"]]

Запрос: {query}

Верни только JSON, без дополнительного текста:"""

        try:
            response_text = await self._call_model(prompt)
            
            # Parse JSON from response
            concepts = []
            try:
                # Try to extract JSON from response
                json_match = None
                # Look for JSON array pattern
                import re
                json_pattern = r'\[\[.*?\]\]'
                match = re.search(json_pattern, response_text, re.DOTALL)
                if match:
                    concepts = json.loads(match.group(0))
                else:
                    # Try to parse entire response
                    concepts = json.loads(response_text.strip())
            except json.JSONDecodeError:
                # Fallback: simple keyword extraction
                logger.warning("Failed to parse Ollama JSON response, using fallback")
                words = query.lower().split()
                stop_words = {"и", "или", "в", "на", "с", "для", "от", "до", "по", "из", "к", "о", "а", "но"}
                keywords = [w for w in words if len(w) > 2 and w not in stop_words]
                concepts = [[word, word] for word in keywords[:10]]
            
            if not isinstance(concepts, list):
                concepts = []
            
            logger.info("Concepts extracted via Ollama", query=query, count=len(concepts))
            return concepts
            
        except ExternalServiceException:
            raise
        except Exception as e:
            logger.error("Failed to extract concepts via Ollama", error=str(e), exc_info=True)
            raise ExternalServiceException(
                "ollama",
                f"Failed to extract concepts: {str(e)}"
            )
    
    async def analyze_resume(
        self,
        resume_text: str,
        concepts: List[List[str]],
        vacancy_requirements: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze resume using Ollama with detailed evaluation
        Returns: {
            "score": int (1-10),
            "summary": str,
            "match_explanation": str,
            "strengths": List[str],
            "weaknesses": List[str],
            "questions": List[str],
            "ai_generated_detected": bool,
            "evaluation_details": {
                "technical_skills": {"score": float, "details": str, "explanation": str},
                "experience": {"score": float, "details": str, "explanation": str},
                "education": {"score": float, "details": str, "explanation": str},
                "soft_skills": {"score": float, "details": str, "explanation": str}
            },
            "match_percentage": float (0-100),
            "red_flags": List[str],
            "recommendation": str
        }
        """
        concepts_text = concepts[0][0] if concepts else ""
        if len(concepts) > 1:
            concepts_text = ", ".join([c[0] for c in concepts[:5]])
        
        # Build vacancy requirements text if available
        vacancy_text = ""
        if vacancy_requirements:
            vacancy_text = "\n\nТребования к вакансии:\n"
            if vacancy_requirements.get("technical_skills"):
                vacancy_text += f"Технические навыки: {vacancy_requirements.get('technical_skills')}\n"
            if vacancy_requirements.get("experience"):
                vacancy_text += f"Опыт работы: {vacancy_requirements.get('experience')}\n"
            if vacancy_requirements.get("education"):
                vacancy_text += f"Образование: {vacancy_requirements.get('education')}\n"
        
        prompt = f"""Ты - опытный HR-аналитик и рекрутер. Проведи ГЛУБОКИЙ анализ резюме кандидата и дай детальную оценку его соответствия требованиям.

Резюме кандидата:
{resume_text}

Ключевые требования для поиска: {concepts_text}{vacancy_text}

Проведи детальный анализ по следующим аспектам:

1. **ОПЫТ РАБОТЫ**: 
   - Оцени релевантность опыта работы требованиям
   - Проанализируй карьерный рост и стабильность
   - Оцени длительность работы в каждой компании
   - Выяви пробелы в опыте или частые смены работы

2. **ТЕХНИЧЕСКИЕ НАВЫКИ**:
   - Оцени соответствие технических навыков требованиям
   - Определи уровень владения каждым навыком
   - Выяви недостающие критичные навыки
   - Оцени актуальность технологий

3. **ОБРАЗОВАНИЕ**:
   - Оцени релевантность образования
   - Учти дополнительное образование и сертификаты
   - Оцени престижность учебных заведений

4. **СОФТ-СКИЛЛЫ**:
   - Оцени коммуникативные навыки
   - Оцени способность к работе в команде
   - Оцени лидерские качества (если релевантно)

5. **ПОДХОДИТ ЛИ КАНДИДАТ**:
   - Детально объясни, ПОЧЕМУ кандидат подходит или не подходит
   - Укажи конкретные факты из резюме
   - Оцени потенциал роста

6. **НА ЧТО ОБРАТИТЬ ВНИМАНИЕ**:
   - Выяви подозрительные моменты
   - Укажи на несоответствия
   - Отметь красные флаги

7. **ЧТО СПРОСИТЬ НА СОБЕСЕДОВАНИИ**:
   - Подготовь конкретные вопросы для проверки опыта
   - Вопросы для уточнения пробелов
   - Вопросы для оценки мотивации

Верни результат ТОЛЬКО в формате JSON со следующими полями:
{{
  "score": число от 1 до 10 (общая оценка соответствия),
  "summary": "краткое резюме анализа на русском языке (2-3 предложения)",
  "match_explanation": "ПОДРОБНОЕ объяснение на русском языке (5-7 предложений): почему кандидат подходит или не подходит, какие конкретные факты из резюме это подтверждают, какие есть сильные и слабые стороны",
  "strengths": ["конкретная сильная сторона 1 с фактами", "конкретная сильная сторона 2 с фактами", "конкретная сильная сторона 3"],
  "weaknesses": ["конкретная слабая сторона 1 с фактами", "конкретная слабая сторона 2 с фактами"],
  "questions": ["конкретный вопрос для собеседования 1 (для проверки опыта/навыков)", "конкретный вопрос 2 (для уточнения пробелов)", "конкретный вопрос 3 (для оценки мотивации)", "конкретный вопрос 4", "конкретный вопрос 5"],
  "ai_generated_detected": true или false (определи, написано ли резюме с помощью AI),
  "evaluation_details": {{
    "technical_skills": {{
      "score": число от 1 до 10,
      "details": "детальный анализ технических навыков: какие навыки есть, каких не хватает, уровень владения",
      "explanation": "объяснение оценки: почему именно такая оценка, на основе каких фактов"
    }},
    "experience": {{
      "score": число от 1 до 10,
      "details": "детальный анализ опыта работы: релевантность опыта, карьерный рост, стабильность, длительность работы",
      "explanation": "объяснение оценки: почему именно такая оценка, какие проекты/компании наиболее релевантны"
    }},
    "education": {{
      "score": число от 1 до 10,
      "details": "детальный анализ образования: релевантность, престижность, дополнительное образование",
      "explanation": "объяснение оценки: почему именно такая оценка"
    }},
    "soft_skills": {{
      "score": число от 1 до 10,
      "details": "детальный анализ софт-скиллов: что видно из резюме, что можно предположить",
      "explanation": "объяснение оценки: почему именно такая оценка"
    }}
  }},
  "match_percentage": число от 0 до 100 (процент соответствия требованиям),
  "red_flags": ["конкретный красный флаг 1 с объяснением", "конкретный красный флаг 2 с объяснением"],
  "recommendation": "ДЕТАЛЬНАЯ рекомендация на русском языке (3-5 предложений): стоит ли приглашать на собеседование, почему, на что обратить внимание при собеседовании, какие вопросы задать, какой потенциал у кандидата",
  "interview_focus": "На чем сосредоточиться на собеседовании: конкретные темы и вопросы для обсуждения",
  "career_trajectory": "Анализ карьерной траектории: рост, стабильность, логичность переходов"
}}

ВАЖНО:
- Будь конкретным и ссылайся на факты из резюме
- Давай развернутые объяснения, а не краткие ответы
- Вопросы должны быть конкретными и релевантными
- Рекомендация должна быть детальной и обоснованной

Верни только JSON, без дополнительного текста:"""

        try:
            response_text = await self._call_model(prompt)
            
            # Parse JSON from response
            result = {}
            try:
                # Try to extract JSON from response
                import re
                json_pattern = r'\{[\s\S]*\}'
                match = re.search(json_pattern, response_text, re.DOTALL)
                if match:
                    result = json.loads(match.group(0))
                else:
                    result = json.loads(response_text.strip())
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse Ollama JSON response", error=str(e))
                # Return basic structure with fallback values
                result = {
                    "score": 5,
                    "summary": "Анализ выполнен через Ollama, но не удалось распарсить ответ",
                    "match_explanation": response_text[:200] if response_text else "Ошибка парсинга",
                    "strengths": [],
                    "weaknesses": [],
                    "questions": ["Требуется дополнительная оценка"],
                    "ai_generated_detected": False,
                    "evaluation_details": None,
                    "match_percentage": 50.0,
                    "red_flags": [],
                    "recommendation": "Требуется ручная оценка"
                }
            
            # Ensure all required fields are present
            if "score" not in result:
                result["score"] = 5
            if "summary" not in result:
                result["summary"] = "Анализ выполнен через Ollama"
            if "questions" not in result:
                result["questions"] = []
            if "ai_generated_detected" not in result:
                result["ai_generated_detected"] = False
            if "red_flags" not in result:
                result["red_flags"] = []
            if "strengths" not in result:
                result["strengths"] = []
            if "weaknesses" not in result:
                result["weaknesses"] = []
            if "match_explanation" not in result:
                result["match_explanation"] = result.get("summary", "")
            if "recommendation" not in result:
                result["recommendation"] = result.get("summary", "")
            if "match_percentage" not in result:
                result["match_percentage"] = result.get("score", 5) * 10.0
            if "evaluation_details" not in result:
                result["evaluation_details"] = None
            
            logger.info("Resume analyzed via Ollama", score=result.get("score"))
            return result
            
        except ExternalServiceException:
            raise
        except Exception as e:
            logger.error("Failed to analyze resume via Ollama", error=str(e), exc_info=True)
            raise ExternalServiceException(
                "ollama",
                f"Failed to analyze resume: {str(e)}"
            )


# Global client instance
ollama_client = OllamaClient()
