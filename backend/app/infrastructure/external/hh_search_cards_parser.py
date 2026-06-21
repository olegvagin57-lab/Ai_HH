"""HeadHunter Parser - Extract data from search results cards (without downloading full resume pages)"""
import asyncio
import re
from typing import Optional, Dict, Any, List
from bs4 import BeautifulSoup
from app.config import settings
from app.core.logging import get_logger
from app.core.exceptions import ExternalServiceException

logger = get_logger(__name__)


class HHSearchCardsParser:
    """
    Парсер резюме из карточек на странице поиска.
    Использует curl_cffi для имитации TLS-fingerprint Chrome,
    что обходит bot-detection HH на уровне TLS handshake.
    """

    def __init__(self):
        self.base_url = "https://hh.ru"
        # Chrome-like headers — curl_cffi handles TLS/JA3 spoofing separately
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0",
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
        city_lower = city.lower().strip()
        for city_key, area_id in self.city_to_area_id.items():
            if city_key in city_lower:
                return area_id
        logger.warning(f"City '{city}' not found in mapping, using Moscow (area_id=1)")
        return 1

    async def _warm_session(self, session) -> None:
        """Visit the HH main page first to get a real session cookie."""
        try:
            r = await session.get(
                self.base_url,
                headers=self.headers,
                impersonate="chrome131",
                timeout=15,
            )
            logger.debug(f"Session warm-up: {r.status_code}")
            await asyncio.sleep(2)
        except Exception as e:
            logger.debug(f"Session warm-up failed (non-fatal): {e}")

    async def _download_search_page(
        self,
        session,
        query: str,
        area_id: int,
        page: int = 0,
    ) -> str:
        """Download one search-result page using the already-warmed session."""
        params = {
            "text": query,
            "area": area_id,
            "page": page,
            "items_on_page": 20,
            "order_by": "relevance",
            "logic": "normal",
            "pos": "full_text",
            "exp_period": "all_time",
        }
        url = self.base_url + "/search/resume"
        headers = {
            **self.headers,
            "Referer": self.base_url + "/",
            "Sec-Fetch-Site": "same-origin",
        }

        response = await session.get(
            url,
            params=params,
            headers=headers,
            impersonate="chrome131",
            timeout=30,
        )
        response.raise_for_status()
        return response.text

    def _parse_resume_card(self, card_html) -> Optional[Dict[str, Any]]:
        try:
            soup = BeautifulSoup(str(card_html), "html.parser")

            # Extract resume ID — prefer data-resume-hash on the card element
            resume_id = card_html.get("data-resume-hash") if hasattr(card_html, "get") else None
            if not resume_id:
                link = soup.find("a", attrs={"data-qa": "serp-item__title"})
                if link:
                    href = link.get("href", "")
                    match = re.search(r"/resume/([a-f0-9]{20,})", href)
                    if match:
                        resume_id = match.group(1)
            if not resume_id:
                return None

            # Title (должность)
            title = ""
            title_elem = soup.find("span", {"data-qa": "serp-item__title-text"})
            if not title_elem:
                title_elem = soup.find("a", {"data-qa": "serp-item__title"})
            if title_elem:
                title = title_elem.get_text(strip=True)

            # Age
            age = None
            age_elem = soup.find("span", {"data-qa": "resume-serp__resume-age"})
            if age_elem:
                age_match = re.search(r"(\d+)", age_elem.get_text(strip=True))
                if age_match:
                    age = int(age_match.group(1))

            # Salary
            salary = None
            currency = None
            card_text = card_html.get_text() if hasattr(card_html, "get_text") else soup.get_text()
            salary_match = re.search(r"([\d \xa0]+)\s*([₽$€]|руб)", card_text)
            if salary_match:
                digits = re.sub(r"[\s \xa0]", "", salary_match.group(1))
                if digits:
                    salary = int(digits)
                    sym = salary_match.group(2)
                    currency = "RUR" if sym in ("₽", "руб") else ("USD" if sym == "$" else "EUR")

            # Experience summary
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
                "area": {},
                "salary": {"amount": salary, "currency": currency} if salary else {},
                "experience": [{"description": experience_summary}] if experience_summary else [],
                "skills": [],
                "education": [],
                "languages": [],
                "description": "",
            }
        except Exception as e:
            logger.warning(f"Failed to parse resume card: {e}")
            return None

    async def search_resumes(
        self,
        query: str,
        city: str,
        per_page: int = 20,
        page: int = 0,
    ) -> Dict[str, Any]:
        """
        Search resumes and extract data from search result cards.
        Uses curl_cffi to spoof Chrome TLS fingerprint so HH doesn't
        classify the request as a bot and return default unrelated results.
        """
        try:
            from curl_cffi.requests import AsyncSession
        except ImportError:
            raise ExternalServiceException(
                "hh_search_cards",
                "curl-cffi not installed. Run: pip install curl-cffi",
            )

        area_id = self._get_area_id(city)
        logger.info(
            "Searching resumes (curl_cffi Chrome TLS)",
            query=query,
            city=city,
            area_id=area_id,
            page=page,
        )

        # Add delay before subsequent pages to look like a human browsing
        if page > 0:
            delay = 4 + page * 0.5  # 4.5s, 5s, 5.5s … — stays under rate limits
            logger.debug(f"Waiting {delay}s before page {page}")
            await asyncio.sleep(delay)

        try:
            async with AsyncSession() as session:
                # Always warm up with a main-page hit to get real session cookies
                await self._warm_session(session)
                html = await self._download_search_page(session, query, area_id, page)

            soup = BeautifulSoup(html, "html.parser")

            # Find resume cards (current HH Magritte design)
            resume_cards = soup.find_all(attrs={"data-qa": "resume-serp__resume"})
            if not resume_cards:
                resume_cards = soup.find_all(attrs={"data-resume-hash": True})
            if not resume_cards:
                seen_parents: List = []
                for link in soup.find_all("a", href=re.compile(r"/resume/[a-f0-9]{20,}")):
                    parent = link.find_parent("div")
                    if parent and parent not in seen_parents:
                        seen_parents.append(parent)
                resume_cards = seen_parents

            logger.info(f"Found {len(resume_cards)} resume cards on page {page}")

            items = []
            for card in resume_cards[:per_page]:
                resume_data = self._parse_resume_card(card)
                if resume_data:
                    items.append(resume_data)

            return {
                "found": len(resume_cards),
                "pages": max(1, (len(resume_cards) + per_page - 1) // per_page),
                "per_page": per_page,
                "page": page,
                "items": items,
            }

        except ExternalServiceException:
            raise
        except Exception as e:
            logger.error("Error searching resumes from cards", error=str(e), exc_info=True)
            raise ExternalServiceException("hh_search_cards", f"Parser error: {str(e)}")

    async def get_resume(self, resume_id: str) -> Dict[str, Any]:
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
