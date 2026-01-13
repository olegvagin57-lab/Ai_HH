"""HeadHunter Parser Client using parse_hh_data library"""
import asyncio
from typing import Optional, Dict, Any, List
from app.config import settings
from app.core.logging import get_logger
from app.core.exceptions import ExternalServiceException

logger = get_logger(__name__)


class HHParserClient:
    """Client for HeadHunter using parse_hh_data library (no API keys required)"""
    
    def __init__(self):
        self.use_parser = True
        try:
            # Try to import parse_hh_data
            import parse_hh_data
            self.parser_available = True
            logger.info("parse_hh_data library available, using parser mode")
        except ImportError:
            self.parser_available = False
            logger.warning(
                "parse_hh_data library not available. "
                "Install with: pip install git+https://github.com/arinaaageeva/parse_hh_data.git"
            )
    
    async def search_resumes(
        self,
        query: str,
        city: str,
        per_page: int = 20,
        page: int = 0
    ) -> Dict[str, Any]:
        """
        Search resumes using parse_hh_data library
        Returns: {
            "found": int,
            "pages": int,
            "items": List[Dict]
        }
        """
        if not self.parser_available:
            raise ExternalServiceException(
                "hh_parser",
                "parse_hh_data library not installed. "
                "Install with: pip install git+https://github.com/arinaaageeva/parse_hh_data.git"
            )
        
        try:
            # Import parse_hh_data
            from parse_hh_data import download, parse
            
            # Map city name to area_id (common cities)
            # For full list, you would need to query HH API areas endpoint
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
            
            # Try to get area_id from city name
            area_id = None
            city_lower = city.lower().strip()
            for city_key, area in city_to_area_id.items():
                if city_key in city_lower:
                    area_id = area
                    break
            
            if not area_id:
                # Default to Moscow if city not found
                area_id = 1
                logger.warning(f"City '{city}' not found in mapping, using Moscow (area_id=1)")
            
            # Get resume IDs using parse_hh_data
            # Note: parse_hh_data.download.resume_ids may need area_ids and specialization_ids
            # For now, we'll use a simplified approach
            
            logger.info(
                "Searching resumes with parser",
                query=query,
                city=city,
                area_id=area_id,
                per_page=per_page,
                page=page
            )
            
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            
            # Get resume IDs (this is a synchronous operation)
            def get_resume_ids():
                try:
                    # parse_hh_data.download.resume_ids signature:
                    # resume_ids(area_id, specialization_id, search_period, num_pages)
                    # area_id: int - area ID (1 = Moscow, 2 = SPB, etc.)
                    # specialization_id: int - specialization ID (0 = all)
                    # search_period: int - days (0=all, 1=day, 3=3days, 7=week, 30=month, 365=year)
                    # num_pages: int - number of pages to fetch
                    
                    # Calculate num_pages based on per_page and max results needed
                    num_pages = max(1, (per_page * (page + 1) + 19) // 20)  # Round up to pages
                    
                    # Try with search_period=0 (all periods) first for better results
                    resume_ids = download.resume_ids(
                        area_id=area_id,
                        specialization_id=0,  # 0 = all specializations
                        search_period=0,  # 0 = all periods (better chance of finding resumes)
                        num_pages=num_pages
                    )
                    logger.info(f"Got {len(resume_ids)} resume IDs from parser")
                    return resume_ids
                except Exception as e:
                    logger.error(f"Error getting resume IDs: {str(e)}", exc_info=True)
                    return []
            
            resume_ids = await loop.run_in_executor(None, get_resume_ids)
            
            # Apply pagination
            start_idx = page * per_page
            end_idx = start_idx + per_page
            page_ids = resume_ids[start_idx:end_idx]
            
            # Download and parse resumes
            items = []
            for resume_id in page_ids:
                try:
                    # Download resume HTML
                    def download_resume(rid):
                        try:
                            return download.resume(rid)
                        except Exception as e:
                            logger.warning(f"Failed to download resume {rid}: {str(e)}")
                            return None
                    
                    resume_html = await loop.run_in_executor(None, download_resume, resume_id)
                    
                    if resume_html:
                        # Parse resume to JSON
                        def parse_resume(html):
                            try:
                                return parse.resume(html)
                            except Exception as e:
                                logger.warning(f"Failed to parse resume {resume_id}: {str(e)}")
                                return None
                        
                        resume_data = await loop.run_in_executor(None, parse_resume, resume_html)
                        
                        if resume_data:
                            # Convert parse_hh_data format to our format
                            item = self._convert_resume_format(resume_data, resume_id)
                            items.append(item)
                            
                            # Limit to per_page
                            if len(items) >= per_page:
                                break
                
                except Exception as e:
                    logger.warning(f"Error processing resume {resume_id}: {str(e)}")
                    continue
            
            # Filter by query if provided (simple text matching)
            if query:
                query_lower = query.lower()
                filtered_items = []
                for item in items:
                    # Check if query matches title, skills, or experience
                    title = item.get("title", "").lower()
                    skills = " ".join([s.get("name", "") for s in item.get("skills", [])]).lower()
                    if query_lower in title or query_lower in skills:
                        filtered_items.append(item)
                items = filtered_items
            
            return {
                "found": len(resume_ids),  # Total found (before filtering)
                "pages": (len(resume_ids) + per_page - 1) // per_page,
                "per_page": per_page,
                "page": page,
                "items": items
            }
            
        except Exception as e:
            logger.error("Error searching resumes with parser", error=str(e), exc_info=True)
            raise ExternalServiceException("hh_parser", f"Parser error: {str(e)}")
    
    def _convert_resume_format(self, resume_data: Dict[str, Any], resume_id: str) -> Dict[str, Any]:
        """Convert parse_hh_data format to our expected format"""
        # parse_hh_data format:
        # {
        #   "birth_date": str,
        #   "gender": str,
        #   "area": str,
        #   "title": str,
        #   "specialization": list,
        #   "salary": dict,
        #   "education_level": str,
        #   "education": list,
        #   "language": list,
        #   "experience": list,
        #   "skills": str,
        #   "skill_set": list
        # }
        
        # Our expected format (similar to HH API):
        item = {
            "id": resume_id,
            "title": resume_data.get("title", ""),
            "first_name": "",  # Not available in anonymized resumes
            "last_name": "",   # Not available in anonymized resumes
            "age": self._calculate_age(resume_data.get("birth_date")),
            "area": {"name": resume_data.get("area", "")},
            "salary": resume_data.get("salary", {}),
            "experience": self._convert_experience(resume_data.get("experience", [])),
            "skills": [{"name": skill} for skill in resume_data.get("skill_set", [])],
            "education": resume_data.get("education", []),
            "languages": resume_data.get("language", []),
            "specialization": resume_data.get("specialization", []),
            "education_level": resume_data.get("education_level", ""),
            "skills_text": resume_data.get("skills", ""),  # Full skills text
        }
        
        return item
    
    def _calculate_age(self, birth_date: Optional[str]) -> Optional[int]:
        """Calculate age from birth date"""
        if not birth_date:
            return None
        
        try:
            from datetime import datetime
            # Parse date (format may vary)
            # Assuming format like "1990-01-15" or "15.01.1990"
            if "-" in birth_date:
                birth = datetime.strptime(birth_date, "%Y-%m-%d")
            elif "." in birth_date:
                birth = datetime.strptime(birth_date, "%d.%m.%Y")
            else:
                return None
            
            today = datetime.now()
            age = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
            return age
        except Exception:
            return None
    
    def _convert_experience(self, experience_list: List[Dict]) -> List[Dict]:
        """Convert experience format"""
        converted = []
        for exp in experience_list:
            converted.append({
                "position": exp.get("position", ""),
                "company": "",  # Not available in anonymized resumes
                "description": exp.get("description", ""),
                "start": exp.get("start", ""),
                "end": exp.get("end", "")
            })
        return converted
    
    async def get_resume(self, resume_id: str) -> Dict[str, Any]:
        """Get resume details by ID using parser"""
        if not self.parser_available:
            raise ExternalServiceException(
                "hh_parser",
                "parse_hh_data library not installed"
            )
        
        try:
            from parse_hh_data import download, parse
            
            loop = asyncio.get_event_loop()
            
            # Download resume
            def download_resume(rid):
                try:
                    return download.resume(rid)
                except Exception as e:
                    logger.error(f"Failed to download resume {rid}: {str(e)}")
                    return None
            
            resume_html = await loop.run_in_executor(None, download_resume, resume_id)
            
            if not resume_html:
                raise ExternalServiceException("hh_parser", f"Resume {resume_id} not found")
            
            # Parse resume
            def parse_resume(html):
                try:
                    return parse.resume(html)
                except Exception as e:
                    logger.error(f"Failed to parse resume {resume_id}: {str(e)}")
                    return None
            
            resume_data = await loop.run_in_executor(None, parse_resume, resume_html)
            
            if not resume_data:
                raise ExternalServiceException("hh_parser", f"Failed to parse resume {resume_id}")
            
            # Convert format
            return self._convert_resume_format(resume_data, resume_id)
            
        except ExternalServiceException:
            raise
        except Exception as e:
            logger.error("Error getting resume with parser", resume_id=resume_id, error=str(e), exc_info=True)
            raise ExternalServiceException("hh_parser", f"Parser error: {str(e)}")


# Global parser client instance
hh_parser_client = HHParserClient()
