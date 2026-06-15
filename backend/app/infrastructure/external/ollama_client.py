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
        self.timeout = 300.0  # 5 min — GPU model may queue multiple requests
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
            # Re-check availability in case it came up after startup
            self._check_availability()
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
        prompt = f"""Ты — помощник для HR-системы. Твоя задача: извлечь ключевые профессиональные понятия из поискового запроса и подобрать к ним ТОЛЬКО русскоязычные синонимы.

СТРОГИЕ ПРАВИЛА:
1. Только русские слова — никаких английских, китайских или других иностранных слов
2. Аббревиатуры только русские (НПС, КИПиА, ЧПУ и т.п.)
3. 3-6 групп понятий, в каждой 1-3 синонима
4. Верни ТОЛЬКО JSON, без пояснений

Пример для запроса "оператор котельной газ":
[["оператор","операторщик","машинист"],["котельная","котёл","теплоснабжение"],["газ","газоснабжение","природный газ"]]

Запрос: {query}

JSON:"""

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
        # Build search context string
        concepts_text = ", ".join([c[0] for c in concepts[:6]]) if concepts else ""
        vacancy_reqs = ""
        if vacancy_requirements:
            parts = []
            for key in ("technical_skills", "experience", "education", "soft_skills"):
                val = vacancy_requirements.get(key)
                if val:
                    parts.append(str(val))
            if parts:
                vacancy_reqs = "\nДоп. требования вакансии: " + "; ".join(parts)

        prompt = f"""Ты — senior HR-рекрутер с 10+ лет опыта подбора технических специалистов в промышленности.

ВАКАНСИЯ / ПОИСКОВЫЙ ЗАПРОС: {concepts_text}{vacancy_reqs}

РЕЗЮМЕ КАНДИДАТА:
{resume_text}

ВАЖНЫЕ ПРАВИЛА ОЦЕНКИ:
1. Если в резюме МАЛО ДАННЫХ (нет реальных должностей, нет компаний, нет описания опыта) — ставь score 2-3 и укажи "недостаточно данных для оценки"
2. Если должность кандидата явно из ДРУГОЙ ОТРАСЛИ (бухгалтер, повар, продавец, оператор 1С, etc.) — ставь score 1-3
3. Высокие оценки (7-10) ТОЛЬКО при явном наличии релевантного опыта в нефтегазе, трубопроводах или смежных технических областях
4. Не делай допущений: если нет прямых доказательств релевантности — оценка низкая

Шкала оценок:
- 9-10: явный опыт в нефтегазе/трубопроводах, идеальное совпадение
- 7-8: технический специалист со смежным опытом (электрик, механик, машинист)
- 5-6: технический специалист, но из другой отрасли
- 3-4: нет технического опыта или мало данных
- 1-2: явно не подходит (другая профессия/отрасль)

Верни JSON (только JSON, без markdown, без пояснений вне JSON):
{{
  "score": <целое 1-10>,
  "match_percentage": <целое 0-100>,
  "match_explanation": "<2-3 предложения: почему подходит или нет, со ссылкой на конкретные факты резюме>",
  "strengths": ["<факт из резюме>", "<факт из резюме>", "<факт из резюме>"],
  "weaknesses": ["<что отсутствует или вызывает сомнение>", "<второй минус>"],
  "red_flags": ["<красный флаг если есть, иначе пустой список>"],
  "recommendation": "<1-2 предложения: брать/не брать и почему>",
  "interview_focus": "<2-3 конкретных вопроса для проверки компетенций>",
  "career_trajectory": "<1 предложение: карьерный рост стабилен/нет>",
  "evaluation_details": {{
    "technical_skills": {{"score": <1-10>, "details": "<навыки относительно вакансии>"}},
    "experience": {{"score": <1-10>, "details": "<релевантность и стаж>"}},
    "education": {{"score": <1-10>, "details": "<образование>"}},
    "soft_skills": {{"score": <1-10>, "details": "<что видно из резюме>"}}
  }},
  "questions": ["<вопрос 1>", "<вопрос 2>", "<вопрос 3>"],
  "ai_generated_detected": false
}}"""

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
