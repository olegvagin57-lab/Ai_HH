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
            resume_id = None
            
            # Method 1: data-resume-id attribute
            resume_id_attr = card_html.get("data-resume-id") if hasattr(card_html, 'get') else None
            if resume_id_attr:
                resume_id = resume_id_attr
            
            # Method 2: Find link to resume
            if not resume_id:
                link = soup.find("a", href=re.compile(r"/resume/[a-f0-9]+"))
                if link:
                    href = link.get("href", "")
                    match = re.search(r"/resume/([a-f0-9]+)", href)
                    if match:
                        resume_id = match.group(1)
            
            if not resume_id:
                return None
            
            # Extract title (должность) - пробуем разные селекторы
            title = ""
            title_selectors = [
                ("a", {"data-qa": "resume-serp__resume-title"}),
                ("a", {"class": re.compile(r"resume-search-item__name")}),
                ("a", {"class": re.compile(r"serp-item__title")}),
                ("span", {"class": re.compile(r"resume-search-item__title")}),
                ("h3", {}),
                ("h2", {}),
            ]
            for tag, attrs in title_selectors:
                title_elem = soup.find(tag, attrs) if attrs else soup.find(tag)
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    if title:
                        break
            
            # Extract city
            city = ""
            city_elem = soup.find("span", {"data-qa": "resume-serp__resume-address"})
            if not city_elem:
                city_elem = soup.find("span", class_=re.compile(r"resume-search-item__location"))
            if city_elem:
                city = city_elem.get_text(strip=True)
            
            # Extract age
            age = None
            age_text = ""
            age_elem = soup.find("span", {"data-qa": "resume-serp__resume-age"})
            if not age_elem:
                age_elem = soup.find("span", class_=re.compile(r"resume-search-item__age"))
            if age_elem:
                age_text = age_elem.get_text(strip=True)
                age_match = re.search(r"(\d+)", age_text)
                if age_match:
                    age = int(age_match.group(1))
            
            # Extract salary
            salary = None
            currency = None
            salary_elem = soup.find("span", {"data-qa": "resume-serp__resume-compensation"})
            if not salary_elem:
                salary_elem = soup.find("div", class_=re.compile(r"resume-search-item__compensation"))
            if salary_elem:
                salary_text = salary_elem.get_text(strip=True)
                # Extract number and currency
                salary_match = re.search(r"(\d+[\s\d]*)", salary_text.replace(" ", "").replace("\xa0", ""))
                if salary_match:
                    salary = int(salary_match.group(1).replace(" ", "").replace("\xa0", ""))
                    if "руб" in salary_text.lower() or "rur" in salary_text.lower():
                        currency = "RUR"
                    elif "usd" in salary_text.lower() or "$" in salary_text:
                        currency = "USD"
                    elif "eur" in salary_text.lower() or "€" in salary_text:
                        currency = "EUR"
            
            # Extract experience summary (краткое описание опыта)
            experience_summary = ""
            exp_elem = soup.find("div", {"data-qa": "resume-serp__resume-experience"})
            if not exp_elem:
                exp_elem = soup.find("div", class_=re.compile(r"resume-search-item__experience"))
            if exp_elem:
                experience_summary = exp_elem.get_text(strip=True)
            
            # Extract skills from tags
            skills = []
            skills_container = soup.find("div", {"data-qa": "resume-serp__resume-skills"})
            if not skills_container:
                skills_container = soup.find("div", class_=re.compile(r"resume-search-item__skills"))
            
            if skills_container:
                skill_tags = skills_container.find_all("span", class_=re.compile(r"bloko-tag"))
                for tag in skill_tags:
                    skill_text = tag.get_text(strip=True)
                    if skill_text:
                        skills.append({"name": skill_text})
            
            # Extract full description/preview text
            description = ""
            desc_elem = soup.find("div", {"data-qa": "resume-serp__resume-snippet"})
            if not desc_elem:
                desc_elem = soup.find("div", class_=re.compile(r"resume-search-item__snippet"))
            if desc_elem:
                description = desc_elem.get_text(strip=True)
            
            # Build result - используем данные из карточки
            result = {
                "id": resume_id,
                "title": title,
                "first_name": "",  # Не доступно в карточке
                "last_name": "",   # Не доступно в карточке
                "age": age,
                "area": {"name": city} if city else {},
                "salary": {"amount": salary, "currency": currency} if salary else {},
                "experience": [{"description": experience_summary}] if experience_summary else [],
                "skills": skills,
                "education": [],  # Обычно не показывается в карточке
                "languages": [],  # Обычно не показывается в карточке
                "description": description,  # Дополнительное поле с описанием
            }
            
            return result
            
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
            
            # Find all resume cards
            # Различные варианты селекторов для карточек резюме
            resume_cards = []
            
            # Method 1: data-resume-id attribute
            cards_with_attr = soup.find_all(attrs={"data-resume-id": True})
            resume_cards.extend(cards_with_attr)
            
            # Method 2: По классу карточки
            if not resume_cards:
                card_classes = [
                    "resume-search-item",
                    "serp-item",
                    "resume-search-item__resume",
                    "resume-item",
                ]
                for class_name in card_classes:
                    cards = soup.find_all("div", class_=re.compile(class_name))
                    if cards:
                        resume_cards.extend(cards)
                        break
            
            # Method 3: По структуре - найти блоки со ссылками на резюме
            if not resume_cards:
                links = soup.find_all("a", href=re.compile(r"/resume/[a-f0-9]+"))
                for link in links:
                    parent = link.find_parent("div")
                    if parent and parent not in resume_cards:
                        resume_cards.append(parent)
            
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
