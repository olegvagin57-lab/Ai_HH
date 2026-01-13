"""HeadHunter Parser Client using kate-red/HH_parcer approach"""
import asyncio
import re
from typing import Optional, Dict, Any, List
from urllib.parse import urlencode, quote
import httpx
from bs4 import BeautifulSoup
from app.config import settings
from app.core.logging import get_logger
from app.core.exceptions import ExternalServiceException

logger = get_logger(__name__)


class HHKateParserClient:
    """
    Client for HeadHunter using direct HTML parsing approach
    Based on: https://github.com/kate-red/HH_parcer
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
            "москва": 1,
            "moscow": 1,
            "санкт-петербург": 2,
            "spb": 2,
            "saint-petersburg": 2,
            "питер": 2,
            "новосибирск": 4,
            "novosibirsk": 4,
            "екатеринбург": 3,
            "ekaterinburg": 3,
            "нижний новгород": 66,
            "казань": 88,
            "челябинск": 104,
            "омск": 68,
            "самара": 78,
            "ростов-на-дону": 76,
            "уфа": 99,
            "красноярск": 54,
            "воронеж": 26,
            "пермь": 72,
        }
    
    def _get_area_id(self, city: str) -> int:
        """Get area_id from city name"""
        city_lower = city.lower().strip()
        for city_key, area_id in self.city_to_area_id.items():
            if city_key in city_lower:
                return area_id
        # Default to Moscow
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
            "items_on_page": 20,
            "order_by": "relevance",
        }
        
        try:
            # Don't follow redirects automatically, handle them manually
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=False) as client:
                response = await client.get(url, params=params, headers=self.headers)
                
                # Handle redirects manually to preserve headers
                if response.status_code in (301, 302, 303, 307, 308):
                    redirect_url = response.headers.get("Location")
                    if redirect_url:
                        # Make sure it's absolute URL
                        if redirect_url.startswith("/"):
                            redirect_url = f"{self.base_url}{redirect_url}"
                        # Follow redirect with same headers
                        response = await client.get(redirect_url, headers=self.headers)
                
                response.raise_for_status()
                return response.text
        except Exception as e:
            logger.error(f"Failed to download search page: {str(e)}")
            raise ExternalServiceException("hh_kate_parser", f"Failed to download search page: {str(e)}")
    
    def _extract_resume_ids(self, html: str) -> List[str]:
        """Extract resume IDs from search results HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        resume_ids = []
        
        # Method 1: Find by data-resume-id attribute
        resume_blocks = soup.find_all(attrs={"data-resume-id": True})
        for block in resume_blocks:
            resume_id = block.get("data-resume-id")
            if resume_id:
                resume_ids.append(resume_id)
        
        # Method 2: Find by class resume-search-item
        if not resume_ids:
            resume_items = soup.find_all("div", class_=re.compile(r"resume-search-item"))
            for item in resume_items:
                # Try to find link to resume
                link = item.find("a", href=re.compile(r"/resume/"))
                if link:
                    href = link.get("href", "")
                    match = re.search(r"/resume/([a-f0-9]+)", href)
                    if match:
                        resume_ids.append(match.group(1))
        
        # Method 3: Find all links to /resume/
        if not resume_ids:
            links = soup.find_all("a", href=re.compile(r"/resume/[a-f0-9]+"))
            for link in links:
                href = link.get("href", "")
                match = re.search(r"/resume/([a-f0-9]+)", href)
                if match:
                    resume_id = match.group(1)
                    if resume_id not in resume_ids:
                        resume_ids.append(resume_id)
        
        # Remove duplicates
        return list(set(resume_ids))
    
    async def _download_resume_html(self, resume_id: str) -> Optional[str]:
        """Download HTML page of a specific resume"""
        url = f"{self.base_url}/resume/{resume_id}"
        
        try:
            # Use same headers but add Referer for resume pages
            resume_headers = self.headers.copy()
            resume_headers["Referer"] = f"{self.base_url}/search/resume"
            
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=False) as client:
                response = await client.get(url, headers=resume_headers)
                
                # Handle redirects manually
                if response.status_code in (301, 302, 303, 307, 308):
                    redirect_url = response.headers.get("Location")
                    if redirect_url:
                        if redirect_url.startswith("/"):
                            redirect_url = f"{self.base_url}{redirect_url}"
                        response = await client.get(redirect_url, headers=resume_headers)
                
                if response.status_code == 403:
                    logger.warning(f"Resume {resume_id} access forbidden (403) - may require authentication")
                    return None
                
                response.raise_for_status()
                return response.text
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning(f"Resume {resume_id} not found (404)")
                return None
            if e.response.status_code == 403:
                logger.warning(f"Resume {resume_id} access forbidden (403)")
                return None
            raise
        except Exception as e:
            logger.warning(f"Failed to download resume {resume_id}: {str(e)}")
            return None
    
    def _parse_resume_html(self, html: str, resume_id: str) -> Optional[Dict[str, Any]]:
        """Parse resume HTML to extract structured data"""
        soup = BeautifulSoup(html, 'html.parser')
        
        try:
            # Extract title
            title_elem = soup.find("h1", class_=re.compile(r"resume-block__title"))
            if not title_elem:
                title_elem = soup.find("span", class_=re.compile(r"resume-block__title-text"))
            title = title_elem.get_text(strip=True) if title_elem else ""
            
            # Extract city
            city = ""
            city_elem = soup.find("span", {"data-qa": "resume-personal-address"})
            if not city_elem:
                city_elem = soup.find("span", class_=re.compile(r"resume-block__title-subtitle"))
            if city_elem:
                city = city_elem.get_text(strip=True)
            
            # Extract age
            age = None
            age_elem = soup.find("span", {"data-qa": "resume-personal-age"})
            if age_elem:
                age_text = age_elem.get_text(strip=True)
                age_match = re.search(r"(\d+)", age_text)
                if age_match:
                    age = int(age_match.group(1))
            
            # Extract gender
            gender = None
            gender_elem = soup.find("span", {"data-qa": "resume-personal-gender"})
            if gender_elem:
                gender_text = gender_elem.get_text(strip=True).lower()
                if "муж" in gender_text or "male" in gender_text:
                    gender = "male"
                elif "жен" in gender_text or "female" in gender_text:
                    gender = "female"
            
            # Extract salary
            salary = None
            currency = None
            salary_elem = soup.find("span", {"data-qa": "resume-block-salary"})
            if not salary_elem:
                salary_elem = soup.find("span", class_=re.compile(r"resume-block__salary"))
            if salary_elem:
                salary_text = salary_elem.get_text(strip=True)
                # Extract number and currency
                salary_match = re.search(r"(\d+[\s\d]*)", salary_text.replace(" ", ""))
                if salary_match:
                    salary = int(salary_match.group(1).replace(" ", ""))
                    if "руб" in salary_text or "RUR" in salary_text:
                        currency = "RUR"
                    elif "USD" in salary_text or "$" in salary_text:
                        currency = "USD"
                    elif "EUR" in salary_text or "€" in salary_text:
                        currency = "EUR"
            
            # Extract skills
            skills = []
            skills_elem = soup.find("div", {"data-qa": "skills-element"})
            if not skills_elem:
                skills_elem = soup.find("div", class_=re.compile(r"resume-block__skills"))
            if skills_elem:
                skill_items = skills_elem.find_all("span", class_=re.compile(r"bloko-tag"))
                for item in skill_items:
                    skill_text = item.get_text(strip=True)
                    if skill_text:
                        skills.append({"name": skill_text})
            
            # Extract experience
            experience = []
            exp_section = soup.find("div", {"data-qa": "resume-block-experience"})
            if not exp_section:
                exp_section = soup.find("div", class_=re.compile(r"resume-block__experience"))
            
            if exp_section:
                exp_items = exp_section.find_all("div", class_=re.compile(r"resume-block__experience-item"))
                for item in exp_items:
                    position_elem = item.find("div", class_=re.compile(r"resume-block__experience-position"))
                    company_elem = item.find("div", class_=re.compile(r"resume-block__experience-company"))
                    desc_elem = item.find("div", class_=re.compile(r"resume-block__experience-description"))
                    
                    position = position_elem.get_text(strip=True) if position_elem else ""
                    company = company_elem.get_text(strip=True) if company_elem else ""
                    description = desc_elem.get_text(strip=True) if desc_elem else ""
                    
                    if position or company:
                        experience.append({
                            "position": position,
                            "company": company,
                            "description": description
                        })
            
            # Extract education
            education = []
            edu_section = soup.find("div", {"data-qa": "resume-block-education"})
            if not edu_section:
                edu_section = soup.find("div", class_=re.compile(r"resume-block__education"))
            
            if edu_section:
                edu_items = edu_section.find_all("div", class_=re.compile(r"resume-block__education-item"))
                for item in edu_items:
                    edu_text = item.get_text(strip=True)
                    if edu_text:
                        education.append({"name": edu_text})
            
            # Extract languages
            languages = []
            lang_section = soup.find("div", {"data-qa": "resume-block-languages"})
            if not lang_section:
                lang_section = soup.find("div", class_=re.compile(r"resume-block__languages"))
            
            if lang_section:
                lang_items = lang_section.find_all("div", class_=re.compile(r"resume-block__language"))
                for item in lang_items:
                    lang_text = item.get_text(strip=True)
                    if lang_text:
                        languages.append({"name": lang_text})
            
            # Build result
            result = {
                "id": resume_id,
                "title": title,
                "first_name": "",  # Not available in public resumes
                "last_name": "",   # Not available in public resumes
                "age": age,
                "area": {"name": city} if city else {},
                "salary": {"amount": salary, "currency": currency} if salary else {},
                "experience": experience,
                "skills": skills,
                "education": education,
                "languages": languages,
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to parse resume HTML {resume_id}: {str(e)}", exc_info=True)
            return None
    
    async def search_resumes(
        self,
        query: str,
        city: str,
        per_page: int = 20,
        page: int = 0
    ) -> Dict[str, Any]:
        """
        Search resumes using HTML parsing
        Returns: {
            "found": int,
            "pages": int,
            "items": List[Dict]
        }
        """
        try:
            area_id = self._get_area_id(city)
            
            logger.info(
                "Searching resumes with kate parser",
                query=query,
                city=city,
                area_id=area_id,
                per_page=per_page,
                page=page
            )
            
            # Download search page
            html = await self._download_search_page(query, area_id, page)
            
            # Extract resume IDs
            resume_ids = self._extract_resume_ids(html)
            logger.info(f"Found {len(resume_ids)} resume IDs on page {page}")
            
            if not resume_ids:
                return {
                    "found": 0,
                    "pages": 0,
                    "per_page": per_page,
                    "page": page,
                    "items": []
                }
            
            # Download and parse resumes (limit to per_page)
            items = []
            for resume_id in resume_ids[:per_page]:
                try:
                    # Download resume HTML
                    resume_html = await self._download_resume_html(resume_id)
                    if not resume_html:
                        continue
                    
                    # Parse resume
                    resume_data = self._parse_resume_html(resume_html, resume_id)
                    if resume_data:
                        items.append(resume_data)
                    
                    # Small delay to avoid rate limiting
                    await asyncio.sleep(0.5)
                    
                except Exception as e:
                    logger.warning(f"Error processing resume {resume_id}: {str(e)}")
                    continue
            
            # Estimate total found (based on page size)
            # This is approximate since we don't know total without parsing all pages
            estimated_total = len(resume_ids) * (page + 1) if page == 0 else len(resume_ids)
            
            return {
                "found": estimated_total,
                "pages": max(1, (estimated_total + per_page - 1) // per_page),
                "per_page": per_page,
                "page": page,
                "items": items
            }
            
        except Exception as e:
            logger.error("Error searching resumes with kate parser", error=str(e), exc_info=True)
            raise ExternalServiceException("hh_kate_parser", f"Parser error: {str(e)}")
    
    async def get_resume(self, resume_id: str) -> Dict[str, Any]:
        """Get resume details by ID"""
        try:
            resume_html = await self._download_resume_html(resume_id)
            if not resume_html:
                raise ExternalServiceException("hh_kate_parser", f"Resume {resume_id} not found")
            
            resume_data = self._parse_resume_html(resume_html, resume_id)
            if not resume_data:
                raise ExternalServiceException("hh_kate_parser", f"Failed to parse resume {resume_id}")
            
            return resume_data
            
        except ExternalServiceException:
            raise
        except Exception as e:
            logger.error("Error getting resume with kate parser", resume_id=resume_id, error=str(e), exc_info=True)
            raise ExternalServiceException("hh_kate_parser", f"Parser error: {str(e)}")


# Global parser client instance
hh_kate_parser_client = HHKateParserClient()
