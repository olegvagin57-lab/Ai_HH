"""Ollama client for local AI analysis"""
import asyncio
import re
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
    
    async def extract_profession_profile(
        self,
        vacancy_title: str,
        vacancy_description: str = "",
        vacancy_requirements: str = "",
    ) -> Dict[str, Any]:
        """
        Generate a professional profile for the vacancy once per search.
        The profile captures: what the role really is, all synonymous titles,
        adjacent roles, key competencies, and profession-specific red flags.
        This is cached in the Concept document and passed to every resume evaluation,
        so the model doesn't have to re-derive profession semantics from scratch each time.
        """
        context_parts = [f"Название должности: {vacancy_title}"]
        if vacancy_description:
            context_parts.append(f"Описание: {str(vacancy_description)[:400]}")
        if vacancy_requirements:
            context_parts.append(f"Требования: {str(vacancy_requirements)[:400]}")
        context = "\n".join(context_parts)

        prompt = f"""ИНСТРУКЦИЯ: отвечай ТОЛЬКО на русском языке. Никаких иностранных слов, кроме общепринятых аббревиатур.

Ты — HR-эксперт. Опиши профессию для российского рынка труда.

Вакансия: {vacancy_title}
{f"Описание: {str(vacancy_description)[:250]}" if vacancy_description else ""}
{f"Требования: {str(vacancy_requirements)[:250]}" if vacancy_requirements else ""}

Верни ТОЛЬКО JSON на русском языке:
{{
  "core_role": "суть работы на этой должности (1 предложение по-русски)",
  "synonymous_titles": ["русское синонимичное название 1", "русское синонимичное название 2", "русское синонимичное название 3"],
  "adjacent_roles": ["смежная профессия 1 по-русски", "смежная профессия 2 по-русски"],
  "clearly_different_roles": ["другая профессия 1 по-русски", "другая профессия 2 по-русски"],
  "key_competencies": ["компетенция 1", "компетенция 2", "компетенция 3", "компетенция 4"],
  "experience_levels": {{
    "junior": "до 2 лет — что умеет",
    "middle": "2-5 лет — что умеет",
    "senior": "5 лет и более — что умеет"
  }},
  "profession_red_flags": ["красный флаг 1 по-русски", "красный флаг 2 по-русски"]
}}"""

        def _has_cyrillic(text: str) -> bool:
            return bool(re.search(r'[а-яёА-ЯЁ]', text))

        def _parse_profile(response_text: str) -> Dict[str, Any]:
            match = re.search(r'\{[\s\S]*\}', response_text, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            return json.loads(response_text.strip())

        try:
            profile: Dict[str, Any] = {}
            for attempt in range(2):
                response_text = await self._call_model(prompt)
                try:
                    parsed = _parse_profile(response_text)
                    # Reject if synonymous_titles contain no Cyrillic (e.g. model answered in Chinese)
                    synonyms_text = " ".join(parsed.get("synonymous_titles", []))
                    if synonyms_text and not _has_cyrillic(synonyms_text):
                        logger.warning(
                            f"Profession profile attempt {attempt+1} returned non-Russian text, retrying"
                        )
                        if attempt == 0:
                            continue
                    profile = parsed
                    break
                except json.JSONDecodeError:
                    if attempt == 0:
                        continue
                    logger.warning("Failed to parse profession profile JSON, using minimal fallback")

            if not profile:
                profile = {
                    "core_role": vacancy_title,
                    "synonymous_titles": [vacancy_title],
                    "adjacent_roles": [],
                    "clearly_different_roles": [],
                    "key_competencies": [],
                    "experience_levels": {},
                    "profession_red_flags": [],
                }

            logger.info("Profession profile extracted", title=vacancy_title)
            return profile

        except ExternalServiceException:
            raise
        except Exception as e:
            logger.error("Failed to extract profession profile", error=str(e), exc_info=True)
            return {
                "core_role": vacancy_title,
                "synonymous_titles": [vacancy_title],
                "adjacent_roles": [],
                "clearly_different_roles": [],
                "key_competencies": [],
                "experience_levels": {},
                "profession_red_flags": [],
            }

    async def analyze_resume(
        self,
        resume_text: str,
        concepts: List[List[str]],
        vacancy_requirements: Optional[Dict[str, Any]] = None,
        profession_profile: Optional[Dict[str, Any]] = None,
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
        # ── Vacancy section ────────────────────────────────────────────────────
        vreq = vacancy_requirements or {}
        vacancy_title  = vreq.get("vacancy_title", "")
        vacancy_desc   = vreq.get("vacancy_description", "")
        vacancy_reqs   = vreq.get("vacancy_requirements_text", "")

        salary_min = vreq.get("vacancy_salary_min")
        salary_max = vreq.get("vacancy_salary_max")
        currency   = vreq.get("vacancy_currency", "RUR")
        salary_parts = []
        if salary_min:
            salary_parts.append(f"от {salary_min:,}".replace(",", " "))
        if salary_max:
            salary_parts.append(f"до {salary_max:,}".replace(",", " "))
        salary_str = (" ".join(salary_parts) + f" {currency}") if salary_parts else None

        vacancy_lines = []
        if vacancy_title:
            vacancy_lines.append(f"Должность: {vacancy_title}")
        if vacancy_desc:
            vacancy_lines.append(f"Описание: {str(vacancy_desc)[:350]}")
        if vacancy_reqs:
            vacancy_lines.append(f"Требования: {str(vacancy_reqs)[:350]}")
        if salary_str:
            vacancy_lines.append(f"Зарплата: {salary_str}")
        if not vacancy_lines:
            concepts_text = ", ".join(c[0] for c in concepts[:6]) if concepts else ""
            vacancy_lines.append(f"Поисковый запрос: {concepts_text}")
        vacancy_section = "\n".join(vacancy_lines)

        # ── Profession profile section ─────────────────────────────────────────
        # Built once per search by extract_profession_profile(); tells the model
        # exactly what this profession is and which titles are equivalent.
        if profession_profile:
            synonyms  = ", ".join(profession_profile.get("synonymous_titles", [])[:8])
            adjacent  = ", ".join(profession_profile.get("adjacent_roles", [])[:5])
            different = ", ".join(profession_profile.get("clearly_different_roles", [])[:4])
            competencies = "; ".join(profession_profile.get("key_competencies", [])[:6])
            prof_flags   = "; ".join(profession_profile.get("profession_red_flags", [])[:4])
            exp_levels   = profession_profile.get("experience_levels", {})
            exp_junior   = exp_levels.get("junior", "")
            exp_middle   = exp_levels.get("middle", "")
            exp_senior   = exp_levels.get("senior", "")

            profession_section = f"""ПРОФЕССИОНАЛЬНЫЙ ПРОФИЛЬ ВАКАНСИИ (используй как эталон при оценке):
Суть роли: {profession_profile.get("core_role", vacancy_title)}
Синонимичные названия этой должности: {synonyms or "—"}
Смежные профессии (частичное пересечение): {adjacent or "—"}
Явно другие профессии (для этой вакансии): {different or "—"}
Ключевые компетенции: {competencies or "—"}
Уровни опыта: junior — {exp_junior}; middle — {exp_middle}; senior — {exp_senior}
Специфические красные флаги профессии: {prof_flags or "—"}"""
        else:
            profession_section = ""

        prompt = f"""Ты — senior HR-рекрутер с 10+ лет опыта. Оцени соответствие резюме кандидата вакансии.

ВАКАНСИЯ:
{vacancy_section}

{profession_section}

РЕЗЮМЕ КАНДИДАТА:
{resume_text}

ВАЖНО О ДАННЫХ: резюме из карточки поиска — доступны только должность, возраст, суммарный стаж. Полной истории и навыков нет. Оценивай честно по тому, что есть.

ПРАВИЛА ОЦЕНКИ:

1. ПРОФЕССИЯ — используй профессиональный профиль выше:
   - Если должность кандидата входит в "Синонимичные названия" → это ТА ЖЕ профессия → score 6-8+
   - Если должность близка к "Смежные профессии" → score 4-6
   - Если должность в "Явно другие" или не имеет отношения → score 1-2
   - Если профиля нет — опирайся на суть профессии из описания вакансии

2. СТАЖ — оценивай соответствие уровню, не объём:
   - Используй уровни опыта из профиля (junior/middle/senior)
   - Кандидат уровня senior на позицию junior → overqualification → score -1, добавь в red_flags
   - Кандидат уровня junior на позицию senior → underqualification → score -1

3. ЗАРПЛАТА — только факты:
   - Ищи в резюме строку "Желаемая зарплата: ЧИСЛО"
   - Нет этой строки → ЗАПРЕЩЕНО писать что-либо про зарплату в ответе
   - Есть число, превышает вакансию в 1.5× → score -1, в red_flags
   - Есть число, превышает вакансию в 2× → score -2, в red_flags

4. ОГРАНИЧЕННЫЕ ДАННЫЕ:
   - Та же профессия + подходящий уровень стаж → 7-8 (не занижай из-за отсутствия деталей)
   - Та же профессия + стаж неизвестен → 6-7

Шкала: 8-10 (точное совпадение, всё ок) | 6-7 (совпадает, но мало деталей или 1 минус) | 4-5 (смежная или 1 стоп-фактор) | 2-3 (слабое совпадение) | 1 (другая отрасль)

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
