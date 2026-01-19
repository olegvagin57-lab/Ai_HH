"""HeadHunter API client"""
import asyncio
from typing import Optional, Dict, Any, List
import httpx
from app.config import settings
from app.core.logging import get_logger
from app.core.exceptions import ExternalServiceException
from app.core.metrics import track_external_service_request


logger = get_logger(__name__)


class HHClient:
    """Client for HeadHunter API"""
    
    def __init__(self):
        self.client_id = settings.hh_client_id
        self.client_secret = settings.hh_client_secret
        self.redirect_uri = settings.hh_redirect_uri
        self.base_url = "https://api.hh.ru"
        self.access_token: Optional[str] = None
        self.token_expires_at: Optional[float] = None
        self.use_mock = not (self.client_id and self.client_secret)
        self.use_parser = settings.use_hh_parser if hasattr(settings, 'use_hh_parser') else False
        self.parser_type = None  # "kate" or "parse_hh_data"
        
        # Try to use parser if available and no API credentials
        if self.use_mock:
            # Priority 1: Try DarkDarW parser (main parser)
            try:
                from app.infrastructure.external.hh_darkdarw_parser_client import hh_darkdarw_parser_client
                if hh_darkdarw_parser_client.parser_available:
                    self.use_parser = True
                    self.parser_type = "darkdarw"
                    logger.info("HH API credentials not provided, using DarkDarW parser (main parser)")
                else:
                    raise ImportError("DarkDarW parser not available")
            except ImportError:
                # Priority 2: Try search cards parser (no download needed, works reliably)
                try:
                    from app.infrastructure.external.hh_search_cards_parser import hh_search_cards_parser
                    self.use_parser = True
                    self.parser_type = "search_cards"
                    logger.info("HH API credentials not provided, using search cards parser (no download needed, reliable)")
                except ImportError:
                    # Priority 3: Try full page parser (most complete data, but may be blocked)
                    try:
                        from app.infrastructure.external.hh_full_page_parser import hh_full_page_parser
                        self.use_parser = True
                        self.parser_type = "full_page"
                        logger.info("HH API credentials not provided, using full page parser (with delays)")
                    except ImportError:
                        # Priority 4: Try kate-red parser
                        try:
                            from app.infrastructure.external.hh_kate_parser_client import hh_kate_parser_client
                            self.use_parser = True
                            self.parser_type = "kate"
                            logger.info("HH API credentials not provided, using kate-red HTML parser")
                        except ImportError:
                            # Priority 5: Try parse_hh_data parser
                            try:
                                from app.infrastructure.external.hh_parser_client import hh_parser_client
                                if hh_parser_client.parser_available:
                                    self.use_parser = True
                                    self.parser_type = "parse_hh_data"
                                    logger.info("HH API credentials not provided, using parse_hh_data parser")
                                else:
                                    logger.warning("HH API credentials not provided, using mock data")
                                    self.parser_type = None
                            except ImportError:
                                logger.warning("HH API credentials not provided, using mock data")
                                self.parser_type = None
    
    async def _get_access_token(self) -> str:
        """Get OAuth 2.0 access token"""
        if self.use_mock:
            return "mock_token"
        
        # Check if token is still valid
        if self.access_token and self.token_expires_at:
            import time
            if time.time() < self.token_expires_at - 60:  # Refresh 60s before expiry
                return self.access_token
        
        # Request new token
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/oauth/token",
                    data={
                        "grant_type": "client_credentials",
                        "client_id": self.client_id,
                        "client_secret": self.client_secret
                    },
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )
                response.raise_for_status()
                data = response.json()
                
                self.access_token = data["access_token"]
                expires_in = data.get("expires_in", 3600)
                import time
                self.token_expires_at = time.time() + expires_in
                
                logger.info("HH API access token obtained")
                return self.access_token
                
        except Exception as e:
            logger.error("Failed to get HH API access token", error=str(e), exc_info=True)
            raise ExternalServiceException("hh_api", f"Failed to get access token: {str(e)}")
    
    async def _make_request(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make authenticated request to HH API"""
        if self.use_mock:
            return self._mock_request(endpoint, params)
        
        token = await self._get_access_token()
        url = f"{self.base_url}/{endpoint}"
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    url,
                    params=params,
                    headers={"Authorization": f"Bearer {token}"}
                )
                response.raise_for_status()
                track_external_service_request("hh_api", "success")
                return response.json()
                
        except httpx.HTTPStatusError as e:
            track_external_service_request("hh_api", "error")
            raise ExternalServiceException(
                "hh_api",
                f"HTTP error: {e.response.status_code} - {e.response.text}"
            )
        except Exception as e:
            track_external_service_request("hh_api", "error")
            raise ExternalServiceException("hh_api", f"Request failed: {str(e)}")
    
    def _mock_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Mock HH API response for development"""
        logger.info("Using mock HH API response", endpoint=endpoint)
        
        if "resumes" in endpoint:
            # Mock resume search response
            return {
                "found": 1,
                "pages": 1,
                "per_page": 20,
                "page": 0,
                "items": [
                    {
                        "id": "mock_resume_1",
                        "title": "Senior Python Developer",
                        "first_name": "Иван",
                        "last_name": "Иванов",
                        "age": 30,
                        "area": {"name": "Москва"},
                        "salary": {"amount": 200000, "currency": "RUR"},
                        "experience": [
                            {
                                "position": "Senior Python Developer",
                                "company": "Tech Company",
                                "description": "Разработка backend на Python"
                            }
                        ],
                        "skills": [{"name": "Python"}, {"name": "FastAPI"}, {"name": "MongoDB"}]
                    }
                ]
            }
        else:
            return {}
    
    async def search_resumes(
        self,
        query: str,
        city: str,
        per_page: int = 20,
        page: int = 0
    ) -> Dict[str, Any]:
        """
        Search resumes on HeadHunter
        Returns: {
            "found": int,
            "pages": int,
            "items": List[Dict]
        }
        """
        # Use parser if available and no API credentials
        if self.use_parser:
            try:
                if self.parser_type == "darkdarw":
                    from app.infrastructure.external.hh_darkdarw_parser_client import hh_darkdarw_parser_client
                    return await hh_darkdarw_parser_client.search_resumes(query, city, per_page, page)
                elif self.parser_type == "search_cards":
                    from app.infrastructure.external.hh_search_cards_parser import hh_search_cards_parser
                    return await hh_search_cards_parser.search_resumes(query, city, per_page, page)
                elif self.parser_type == "full_page":
                    from app.infrastructure.external.hh_full_page_parser import hh_full_page_parser
                    return await hh_full_page_parser.search_resumes(query, city, per_page, page)
                elif self.parser_type == "kate":
                    from app.infrastructure.external.hh_kate_parser_client import hh_kate_parser_client
                    return await hh_kate_parser_client.search_resumes(query, city, per_page, page)
                elif self.parser_type == "parse_hh_data":
                    from app.infrastructure.external.hh_parser_client import hh_parser_client
                    return await hh_parser_client.search_resumes(query, city, per_page, page)
            except Exception as e:
                logger.warning(f"Parser failed, falling back to mock: {str(e)}")
                # Fall through to mock
        
        params = {
            "text": query,
            "area": city,  # This should be area ID, but for mock we use city name
            "per_page": min(per_page, 100),
            "page": page
        }
        
        response = await self._make_request("resumes", params)
        
        logger.info(
            "Resumes searched",
            query=query,
            city=city,
            found=response.get("found", 0),
            page=page
        )
        
        return response
    
    async def get_resume(self, resume_id: str) -> Dict[str, Any]:
        """Get resume details by ID"""
        # Use parser if available and no API credentials
        if self.use_parser:
            try:
                if self.parser_type == "darkdarw":
                    from app.infrastructure.external.hh_darkdarw_parser_client import hh_darkdarw_parser_client
                    return await hh_darkdarw_parser_client.get_resume(resume_id)
                elif self.parser_type == "search_cards":
                    from app.infrastructure.external.hh_search_cards_parser import hh_search_cards_parser
                    return await hh_search_cards_parser.get_resume(resume_id)
                elif self.parser_type == "full_page":
                    from app.infrastructure.external.hh_full_page_parser import hh_full_page_parser
                    return await hh_full_page_parser.get_resume(resume_id)
                elif self.parser_type == "kate":
                    from app.infrastructure.external.hh_kate_parser_client import hh_kate_parser_client
                    return await hh_kate_parser_client.get_resume(resume_id)
                elif self.parser_type == "parse_hh_data":
                    from app.infrastructure.external.hh_parser_client import hh_parser_client
                    return await hh_parser_client.get_resume(resume_id)
            except Exception as e:
                logger.warning(f"Parser failed, falling back to mock: {str(e)}")
                # Fall through to mock
        
        response = await self._make_request(f"resumes/{resume_id}")
        return response


# Global client instance
hh_client = HHClient()
