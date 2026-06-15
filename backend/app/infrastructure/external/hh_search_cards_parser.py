"""HeadHunter Parser - Extract data from search results cards (without downloading full resume pages)"""
import asyncio
import re
from typing import Optional, Dict, Any, List
from urllib.parse import urlencode
import httpx
from bs4 import BeautifulSoup
from app.config import settings
from app.core.logging import get_logger
from app.core.exceptions import ExternalServiceException

logger = get_logger(__name__)


class HHSearchCardsParser:
    """
    Парсер резюме из карточек на странице поиска
    Не требует скачивания отдельных страниц резюме - использует данные из поисковой выдачи
    """
    
    def __init__(self):
        self.base_url = "https://hh.ru"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0",
            "Referer": "https://hh.ru/",
        }
        self.city_to_area_id = {
            "москва": 1, "moscow": 1,
            "санкт-петербург": 2, "spb": 2, "saint-petersburg": 2, "питер": 2,
            "новосибирск": 4, "novosibirsk": 4,
            "екатеринбург": 3, "ekaterinburg": 3,
            "нижний новгород": 66, "казань": 88,
            "челябинск": 104, "омск": 68, "самара": 78,
            "ростов-на-дону": 76, "уфа": 99, "красноярск": 54,
            "воронеж": 26, "пермь": 72,
        }
    
    def _get_area_id(self, city: str) -> int:
        """Get area_id from city name"""
        city_lower = city.lower().strip()
        for city_key, area_id in self.city_to_area_id.items():
            if city_key in city_lower:
                return area_id
        logger.warning(f"City '{city}' not found in mapping, using Moscow (area_id=1)")
        return 1
    
    async def _download_search_page(
        self,
        query: str,
        area_id: int,
        page: int = 0
    ) -> str:
        """Download HTML page with search results"""
        url = f"{self.base_url}/search/resume"
        params = {
            "text": query,
            "area": area_id,
            "page": page,
            "items_on_page": 100,  # Максимум на странице для получения больше данных
            "order_by": "relevance",
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=False) as client:
                response = await client.get(url, params=params, headers=self.headers)
                
                # Handle redirects
                if response.status_code in (301, 302, 303, 307, 308):
                    redirect_url = response.headers.get("Location")
                    if redirect_url:
                        if redirect_url.startswith("/"):
                            redirect_url = f"{self.base_url}{redirect_url}"
                        response = await client.get(redirect_url, headers=self.headers)
                
                response.raise_for_status()
                return response.text
        except Exception as e:
            logger.error(f"Failed to download search page: {str(e)}")
            raise ExternalServiceException("hh_search_cards", f"Failed to download search page: {str(e)}")
    
    def _parse_resume_card(self, card_html) -> Optional[Dict[str, Any]]:
        """Parse resume data from search result card"""
        try:
            soup = BeautifulSoup(str(card_html), 'html.parser')

            # Extract resume ID
            # Method 1: data-resume-hash attribute on the card element (current HH structure)
            resume_id = card_html.get("data-resume-hash") if hasattr(card_html, 'get') else None

            # Method 2: extract from title link href (require 20+ chars to avoid short hex like "ad")
            if not resume_id:
                link = soup.find("a", attrs={"data-qa": "serp-item__title"})
                if link:
                    href = link.get("href", "")
                    match = re.search(r"/resume/([a-f0-9]{20,})", href)
                    if match:
                        resume_id = match.group(1)

            if not resume_id:
                return None

            # Extract title (должность)
            title = ""
            title_elem = soup.find("span", {"data-qa": "serp-item__title-text"})
            if not title_elem:
                title_elem = soup.find("a", {"data-qa": "serp-item__title"})
            if title_elem:
                title = title_elem.get_text(strip=True)

            # City is not exposed in anonymized HH search results
            city = ""

            # Extract age
            age = None
            age_elem = soup.find("span", {"data-qa": "resume-serp__resume-age"})
            if age_elem:
                age_match = re.search(r"(\d+)", age_elem.get_text(strip=True))
                if age_match:
                    age = int(age_match.group(1))

            # Extract salary from card text (uses thin spaces and nbsp as separators)
            salary = None
            currency = None
            card_text = card_html.get_text() if hasattr(card_html, 'get_text') else soup.get_text()
            salary_match = re.search(r"([\d \xa0]+)\s*([₽$€]|руб)", card_text)
            if salary_match:
                digits = re.sub(r"[\s \xa0]", "", salary_match.group(1))
                if digits:
                    salary = int(digits)
                    sym = salary_match.group(2)
                    currency = "RUR" if sym in ("₽", "руб") else ("USD" if sym == "$" else "EUR")

            # Extract experience summary
            experience_summary = ""
            exp_elem = soup.find(attrs={"data-qa": "resume-serp_resume-item-total-experience-content"})
            if exp_elem:
                experience_summary = exp_elem.get_text(strip=True)

            return {
                "id": resume_id,
                "title": title,
                "first_name": "",
                "last_name": "",
                "age": age,
                "area": {"name": city} if city else {},
                "salary": {"amount": salary, "currency": currency} if salary else {},
                "experience": [{"description": experience_summary}] if experience_summary else [],
                "skills": [],
                "education": [],
                "languages": [],
                "description": "",
            }

        except Exception as e:
            logger.warning(f"Failed to parse resume card: {str(e)}")
            return None
    
    async def search_resumes(
        self,
        query: str,
        city: str,
        per_page: int = 20,
        page: int = 0
    ) -> Dict[str, Any]:
        """
        Search resumes and extract data from search result cards
        Returns: {
            "found": int,
            "pages": int,
            "items": List[Dict]
        }
        """
        try:
            area_id = self._get_area_id(city)
            
            logger.info(
                "Searching resumes from search cards (no download needed)",
                query=query,
                city=city,
                area_id=area_id,
                per_page=per_page,
                page=page
            )
            
            # Download search page
            html = await self._download_search_page(query, area_id, page)
            
            # Parse HTML
            soup = BeautifulSoup(html, 'html.parser')
            
            # Find all resume cards using current HH structure
            resume_cards = []

            # Method 1: data-qa="resume-serp__resume" (current HH Magritte design)
            resume_cards = soup.find_all(attrs={"data-qa": "resume-serp__resume"})

            # Method 2: data-resume-hash attribute (also current HH)
            if not resume_cards:
                resume_cards = soup.find_all(attrs={"data-resume-hash": True})

            # Method 3: links with long resume IDs (20+ chars to avoid short hex like "ad")
            if not resume_cards:
                seen_parents = []
                for link in soup.find_all("a", href=re.compile(r"/resume/[a-f0-9]{20,}")):
                    parent = link.find_parent("div")
                    if parent and parent not in seen_parents:
                        seen_parents.append(parent)
                resume_cards = seen_parents
            
            logger.info(f"Found {len(resume_cards)} resume cards on page {page}")
            
            # Parse each card
            items = []
            for card in resume_cards[:per_page]:
                try:
                    resume_data = self._parse_resume_card(card)
                    if resume_data:
                        items.append(resume_data)
                except Exception as e:
                    logger.warning(f"Error parsing resume card: {str(e)}")
                    continue
            
            logger.info(f"Successfully parsed {len(items)} resumes from cards")
            
            # Estimate total (можем попытаться найти информацию о количестве в HTML)
            estimated_total = len(resume_cards)
            
            return {
                "found": estimated_total,
                "pages": max(1, (estimated_total + per_page - 1) // per_page),
                "per_page": per_page,
                "page": page,
                "items": items
            }
            
        except Exception as e:
            logger.error("Error searching resumes from cards", error=str(e), exc_info=True)
            raise ExternalServiceException("hh_search_cards", f"Parser error: {str(e)}")
    
    async def get_resume(self, resume_id: str) -> Dict[str, Any]:
        """Get resume - not supported, returns basic info"""
        # Для полных данных нужно скачать страницу, но мы можем вернуть минимум
        logger.warning(f"get_resume not fully supported in search cards parser for {resume_id}")
        return {
            "id": resume_id,
            "title": "",
            "area": {},
            "salary": {},
            "experience": [],
            "skills": [],
            "education": [],
            "languages": [],
        }


# Global parser instance
hh_search_cards_parser = HHSearchCardsParser()
