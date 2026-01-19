"""Hugging Face Inference API client for AI analysis"""
import asyncio
from typing import Optional, Dict, Any, List
import httpx
import json
import re
from app.config import settings
from app.core.logging import get_logger
from app.core.exceptions import ExternalServiceException


logger = get_logger(__name__)


class HuggingFaceClient:
    """Client for Hugging Face Inference API"""
    
    def __init__(self):
        # Try to get token from settings
        self.api_token = getattr(settings, 'huggingface_api_token', '') or ''
        # Also try environment variable directly
        import os
        if not self.api_token:
            self.api_token = os.getenv('HUGGING_FACE_API_TOKEN', '')
        
        # Hugging Face Inference API (use direct inference endpoint)
        self.base_url = "https://api-inference.huggingface.co"
        # Используем Mistral 7B Instruct - отличная модель для анализа
        self.model = getattr(settings, 'huggingface_model', 'mistralai/Mistral-7B-Instruct-v0.2')
        self.timeout = 30.0
        self.available = bool(self.api_token)
        
        if not self.available:
            logger.debug("Hugging Face API token not configured")
        else:
            logger.info("Hugging Face client initialized", model=self.model, token_length=len(self.api_token))
    
    async def _call_model(self, prompt: str) -> str:
        """Call Hugging Face Inference API using Python SDK"""
        if not self.available:
            raise ExternalServiceException(
                "huggingface",
                "Hugging Face API token not configured. Set HUGGING_FACE_API_TOKEN in .env"
            )
        
        try:
            # Use Hugging Face InferenceClient (recommended way)
            from huggingface_hub import InferenceClient
            import asyncio
            
            # InferenceClient is synchronous, run in thread pool
            def sync_call():
                client = InferenceClient(token=self.api_token)
                try:
                    # Try text_generation first
                    return client.text_generation(
                        prompt=prompt,
                        model=self.model,
                        max_new_tokens=1000,
                        temperature=0.7,
                        top_p=0.9,
                        return_full_text=False
                    )
                except Exception:
                    # If text_generation fails, try conversational API
                    try:
                        result = client.chat_completion(
                            model=self.model,
                            messages=[{"role": "user", "content": prompt}],
                            max_tokens=1000,
                            temperature=0.7,
                            top_p=0.9
                        )
                        # Extract text from conversational response
                        if isinstance(result, dict) and "choices" in result:
                            return result["choices"][0]["message"]["content"]
                        elif isinstance(result, dict) and "generated_text" in result:
                            return result["generated_text"]
                        else:
                            return str(result)
                    except Exception:
                        # Last resort: use post method directly
                        result = client.post(
                            json={"inputs": prompt},
                            model=self.model
                        )
                        if isinstance(result, list) and len(result) > 0:
                            return result[0].get("generated_text", str(result[0]))
                        return str(result)
            
            # Run in executor to avoid blocking
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, sync_call)
            
            return response
                    
        except ImportError:
            # Fallback to HTTP API if huggingface_hub not installed
            logger.warning("huggingface_hub not installed, using HTTP API")
            return await self._call_model_http(prompt)
        except Exception as e:
            logger.warning(f"Hugging Face SDK failed, trying HTTP API: {str(e)}")
            return await self._call_model_http(prompt)
    
    async def _call_model_http(self, prompt: str) -> str:
        """Fallback HTTP API call"""
        # Try using Inference Endpoints API format
        url = f"https://api-inference.huggingface.co/models/{self.model}"
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        
        data = {
            "inputs": prompt,
            "parameters": {
                "temperature": 0.7,
                "top_p": 0.9,
                "max_new_tokens": 1000,
                "return_full_text": False
            }
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=data, headers=headers)
                
                if response.status_code == 410:
                    # Old API deprecated, but try anyway
                    raise ExternalServiceException(
                        "huggingface",
                        "Hugging Face Inference API deprecated. Please install huggingface_hub: pip install huggingface_hub"
                    )
                
                # Handle rate limiting
                if response.status_code == 503:
                    error_text = response.text
                    if "loading" in error_text.lower():
                        wait_time = 20
                        logger.info(f"Model is loading, waiting {wait_time}s...")
                        await asyncio.sleep(wait_time)
                        response = await client.post(url, json=data, headers=headers)
                
                response.raise_for_status()
                result = response.json()
                
                # Parse response
                if isinstance(result, list) and len(result) > 0:
                    if "generated_text" in result[0]:
                        return result[0]["generated_text"]
                    elif "text" in result[0]:
                        return result[0]["text"]
                    else:
                        return str(result[0])
                elif isinstance(result, dict):
                    if "generated_text" in result:
                        return result["generated_text"]
                    elif "text" in result:
                        return result["text"]
                    else:
                        return str(result)
                else:
                    return str(result)
                    
        except httpx.TimeoutException:
            raise ExternalServiceException(
                "huggingface",
                f"Hugging Face request timeout after {self.timeout}s"
            )
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                raise ExternalServiceException(
                    "huggingface",
                    "Hugging Face rate limit exceeded. Free tier: 30,000 requests/month"
                )
            raise ExternalServiceException(
                "huggingface",
                f"Hugging Face HTTP error: {e.response.status_code} - {e.response.text}"
            )
        except Exception as e:
            raise ExternalServiceException(
                "huggingface",
                f"Hugging Face request failed: {str(e)}"
            )
    
    async def extract_concepts(self, query: str) -> List[List[str]]:
        """
        Extract concepts from search query using Hugging Face
        Returns: List of concept arrays, e.g. [["concept1", "synonym1"], ["concept2", "synonym2"]]
        """
        prompt = f"""<s>[INST] Извлеки ключевые концепты и их синонимы из следующего запроса на русском языке.
Верни результат ТОЛЬКО в формате JSON массива массивов, где каждый внутренний массив содержит концепт и его синонимы.
Пример: [["python", "питон"], ["разработчик", "developer", "программист"]]

Запрос: {query}

Верни только JSON, без дополнительного текста: [/INST]"""

        try:
            response_text = await self._call_model(prompt)
            
            # Parse JSON from response
            concepts = []
            try:
                # Try to extract JSON from response
                json_match = re.search(r'\[\[.*?\]\]', response_text, re.DOTALL)
                if json_match:
                    concepts = json.loads(json_match.group(0))
                else:
                    # Try to parse entire response
                    concepts = json.loads(response_text.strip())
            except json.JSONDecodeError:
                # Fallback: simple keyword extraction
                logger.warning("Failed to parse Hugging Face JSON response, using fallback")
                words = query.lower().split()
                stop_words = {"и", "или", "в", "на", "с", "для", "от", "до", "по", "из", "к", "о", "а", "но"}
                keywords = [w for w in words if len(w) > 2 and w not in stop_words]
                concepts = [[word, word] for word in keywords[:10]]
            
            if not isinstance(concepts, list):
                concepts = []
            
            logger.info("Concepts extracted via Hugging Face", query=query, count=len(concepts))
            return concepts
            
        except ExternalServiceException:
            raise
        except Exception as e:
            logger.error("Failed to extract concepts via Hugging Face", error=str(e), exc_info=True)
            raise ExternalServiceException(
                "huggingface",
                f"Failed to extract concepts: {str(e)}"
            )
    
    async def analyze_resume(
        self,
        resume_text: str,
        concepts: List[List[str]],
        vacancy_requirements: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze resume using Hugging Face with detailed evaluation
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
        
        prompt = f"""<s>[INST] Ты - опытный HR-аналитик и рекрутер. Проведи ГЛУБОКИЙ анализ резюме кандидата и дай детальную оценку его соответствия требованиям.

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
  "ai_generated_detected": true/false (определи, написано ли резюме с помощью AI),
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

Верни только JSON, без дополнительного текста: [/INST]"""

        try:
            response_text = await self._call_model(prompt)
            
            # Parse JSON from response
            result = {}
            try:
                # Try to extract JSON from response
                json_match = re.search(r'\{[\s\S]*\}', response_text, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group(0))
                else:
                    result = json.loads(response_text.strip())
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse Hugging Face JSON response", error=str(e))
                # Return basic structure with fallback values
                result = {
                    "score": 5,
                    "summary": "Анализ выполнен через Hugging Face, но не удалось распарсить ответ",
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
                result["summary"] = "Анализ выполнен через Hugging Face"
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
            if "interview_focus" not in result:
                result["interview_focus"] = "Требуется дополнительная оценка на собеседовании"
            if "career_trajectory" not in result:
                result["career_trajectory"] = "Требуется анализ карьерной траектории"
            
            logger.info("Resume analyzed via Hugging Face", score=result.get("score"))
            return result
            
        except ExternalServiceException:
            raise
        except Exception as e:
            logger.error("Failed to analyze resume via Hugging Face", error=str(e), exc_info=True)
            raise ExternalServiceException(
                "huggingface",
                f"Failed to analyze resume: {str(e)}"
            )


# Global client instance
huggingface_client = HuggingFaceClient()
