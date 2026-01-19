"""HeadHunter Parser Client using DarkDarW/hh.ru_pars approach"""
import asyncio
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List
import httpx
import requests
from bs4 import BeautifulSoup
import time
import random
from app.config import settings
from app.core.logging import get_logger
from app.core.exceptions import ExternalServiceException

logger = get_logger(__name__)


class HHDarkDarWParserClient:
    """Client for HeadHunter using DarkDarW/hh.ru_pars parser approach"""
    
    def __init__(self):
        # Parser is always available as it uses only requests and BeautifulSoup
        # No need to check for external files
        try:
            # Verify dependencies are available
            import requests
            from bs4 import BeautifulSoup
            self.parser_available = True
            logger.info("DarkDarW parser available (using requests + BeautifulSoup)")
        except ImportError as e:
            self.parser_available = False
            logger.warning(f"DarkDarW parser dependencies not available: {str(e)}")
    
    def _get_links(self, text: str, area_id: int = 1, max_pages: int = 10) -> List[str]:
        """Get resume links from hh.ru search (based on DarkDarW parser)"""
        links = []
        
        for page in range(1, max_pages + 1):
            try:
                url = f"https://hh.ru/search/resume?text={text}&area={area_id}&isDefaultArea=true&exp_period=all_time&logic=normal&pos=full_text&page={page}"
                response = requests.get(
                    url=url,
                    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
                    timeout=10
                )
                
                if response.status_code != 200:
                    logger.warning(f"Failed to fetch page {page}: status {response.status_code}")
                    break
                
                # Try lxml first, fallback to html.parser
                try:
                    soup = BeautifulSoup(response.content, "lxml")
                except:
                    soup = BeautifulSoup(response.content, "html.parser")
                
                page_links = []
                
                for a in soup.find_all("a", attrs={"data-qa": "serp-item__title"}):
                    href = a.attrs.get('href', '')
                    if href:
                        # Extract resume ID from href
                        full_link = f"https://hh.ru{href.split('?')[0]}"
                        page_links.append(full_link)
                
                if not page_links:
                    # No more results
                    break
                
                links.extend(page_links)
                logger.debug(f"Found {len(page_links)} resumes on page {page}")
                
                # Small delay to avoid rate limiting
                time.sleep(0.5)
                
            except Exception as e:
                logger.warning(f"Error fetching page {page}: {str(e)}")
                break
        
        return links
    
    def _get_resume_data(self, link: str) -> Optional[Dict[str, Any]]:
        """Get resume data from link (based on DarkDarW parser)"""
        try:
            response = requests.get(
                url=link,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
                timeout=10
            )
            
            if response.status_code != 200:
                return None
            
            # Try lxml first, fallback to html.parser
            try:
                soup = BeautifulSoup(response.content, "lxml")
            except:
                soup = BeautifulSoup(response.content, "html.parser")
            
            # Extract resume ID from link
            resume_id = link.split('/')[-1].split('?')[0]
            
            # Extract name
            name = ""
            try:
                name_elem = soup.find(attrs={"class": "resume-block__title-text"})
                if name_elem:
                    name = name_elem.text.strip()
            except:
                pass
            
            # Extract age
            age = None
            try:
                age_elem = soup.find(attrs={"data-qa": "resume-personal-age"})
                if age_elem:
                    age_text = age_elem.text.replace("\xa0", "").strip()
                    # Extract number from age text (e.g., "25 лет" -> 25)
                    import re
                    age_match = re.search(r'(\d+)', age_text)
                    if age_match:
                        age = int(age_match.group(1))
            except:
                pass
            
            # Extract salary
            salary = None
            try:
                salary_elem = soup.find(attrs={"class": "resume-block__salary"})
                if salary_elem:
                    salary_text = salary_elem.text.replace("\u2009", "").replace("\xa0", "").strip()
                    salary = {"currency": "RUR", "amount": None}
                    # Try to extract amount (simplified)
                    import re
                    amount_match = re.search(r'(\d+)', salary_text.replace(' ', ''))
                    if amount_match:
                        salary["amount"] = int(amount_match.group(1))
            except:
                pass
            
            # Extract tags/skills
            tags = []
            try:
                tag_list = soup.find(attrs={"class": "bloko-tag-list"})
                if tag_list:
                    tags = [tag.text.strip() for tag in tag_list.find_all(attrs={"class": "bloko-tag__section_text"})]
            except:
                pass
            
            # Extract title/position
            title = ""
            try:
                title_elem = soup.find(attrs={"data-qa": "resume-block-title-position"})
                if not title_elem:
                    title_elem = soup.find("h1")
                if title_elem:
                    title = title_elem.text.strip()
            except:
                pass
            
            # Extract area
            area = ""
            try:
                area_elem = soup.find(attrs={"data-qa": "resume-personal-address"})
                if area_elem:
                    area = area_elem.text.strip()
            except:
                pass
            
            return {
                "id": resume_id,
                "name": name,
                "title": title or name,
                "age": age,
                "salary": salary,
                "tags": tags,
                "link": link,
                "area": area
            }
            
        except Exception as e:
            logger.warning(f"Error parsing resume {link}: {str(e)}")
            return None
    
    async def search_resumes(
        self,
        query: str,
        city: str,
        per_page: int = 20,
        page: int = 0
    ) -> Dict[str, Any]:
        """
        Search resumes using DarkDarW parser
        Returns: {
            "found": int,
            "pages": int,
            "items": List[Dict]
        }
        """
        if not self.parser_available:
            raise ExternalServiceException(
                "hh_darkdarw_parser",
                "DarkDarW parser not available. "
                "Clone repository: git clone https://github.com/DarkDarW/hh.ru_pars.git"
            )
        
        try:
            logger.info(
                "Searching resumes with DarkDarW parser",
                query=query,
                city=city,
                per_page=per_page,
                page=page
            )
            
            # Map city to area_id
            city_to_area_id = {
                "москва": 1,
                "moscow": 1,
                "санкт-петербург": 2,
                "spb": 2,
                "saint-petersburg": 2,
                "новосибирск": 4,
                "novosibirsk": 4,
                "екатеринбург": 3,
                "ekaterinburg": 3,
            }
            
            area_id = None
            city_lower = city.lower().strip()
            for city_key, area in city_to_area_id.items():
                if city_key in city_lower:
                    area_id = area
                    break
            
            if not area_id:
                area_id = 1  # Default to Moscow
                logger.warning(f"City '{city}' not found, using Moscow (area_id=1)")
            
            # Calculate how many pages we need
            max_pages = max(1, (per_page * (page + 1) + 19) // 20)
            
            # Run parser in thread pool
            loop = asyncio.get_event_loop()
            
            def search_resumes_sync():
                # Get links
                links = self._get_links(query, area_id, max_pages)
                
                # Apply pagination
                start_idx = page * per_page
                end_idx = start_idx + per_page
                page_links = links[start_idx:end_idx]
                
                # Parse resumes
                items = []
                for link in page_links:
                    resume_data = self._get_resume_data(link)
                    if resume_data:
                        # Convert to our format
                        item = self._convert_resume_format(resume_data)
                        items.append(item)
                    
                    # Small delay to avoid rate limiting
                    time.sleep(0.3)
                    
                    if len(items) >= per_page:
                        break
                
                return {
                    "found": len(links),
                    "pages": (len(links) + per_page - 1) // per_page,
                    "items": items
                }
            
            result = await loop.run_in_executor(None, search_resumes_sync)
            
            return {
                "found": result.get("found", 0),
                "pages": result.get("pages", 0),
                "per_page": per_page,
                "page": page,
                "items": result.get("items", [])
            }
            
        except Exception as e:
            logger.error("Error searching resumes with DarkDarW parser", error=str(e), exc_info=True)
            raise ExternalServiceException("hh_darkdarw_parser", f"Parser error: {str(e)}")
    
    async def get_resume(self, resume_id: str) -> Dict[str, Any]:
        """Get resume details by ID using DarkDarW parser"""
        if not self.parser_available:
            raise ExternalServiceException(
                "hh_darkdarw_parser",
                "DarkDarW parser not available"
            )
        
        try:
            # Construct resume link
            link = f"https://hh.ru/resume/{resume_id}"
            
            loop = asyncio.get_event_loop()
            
            def get_resume_sync(link):
                return self._get_resume_data(link)
            
            resume_data = await loop.run_in_executor(None, get_resume_sync, link)
            
            if not resume_data:
                raise ExternalServiceException("hh_darkdarw_parser", f"Resume {resume_id} not found")
            
            # Convert format
            return self._convert_resume_format(resume_data)
            
        except ExternalServiceException:
            raise
        except Exception as e:
            logger.error("Error getting resume with DarkDarW parser", resume_id=resume_id, error=str(e), exc_info=True)
            raise ExternalServiceException("hh_darkdarw_parser", f"Parser error: {str(e)}")
    
    def _convert_resume_format(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert DarkDarW parser format to our expected format"""
        # Split name into first_name and last_name
        name = resume_data.get("name", "")
        name_parts = name.split(maxsplit=1)
        first_name = name_parts[0] if len(name_parts) > 0 else ""
        last_name = name_parts[1] if len(name_parts) > 1 else ""
        
        # Convert tags to skills format
        tags = resume_data.get("tags", [])
        skills = [{"name": tag} for tag in tags]
        
        return {
            "id": resume_data.get("id", ""),
            "title": resume_data.get("title", ""),
            "first_name": first_name,
            "last_name": last_name,
            "age": resume_data.get("age"),
            "area": {"name": resume_data.get("area", "")},
            "salary": resume_data.get("salary", {}),
            "experience": [],  # Not extracted in basic parser
            "skills": skills,
            "education": [],  # Not extracted in basic parser
        }


# Global parser client instance
hh_darkdarw_parser_client = HHDarkDarWParserClient()
