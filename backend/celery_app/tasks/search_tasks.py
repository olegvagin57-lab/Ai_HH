"""Celery tasks for search processing"""
from typing import Dict, Any
from celery_app.celery import celery_app
from app.domain.entities.search import Search, Resume, Concept
from app.infrastructure.external.hh_client import hh_client
from app.application.services.search_service import search_service
from app.application.services.ai_service import ai_service
from app.core.logging import get_logger
from app.config import settings


logger = get_logger(__name__)


@celery_app.task(name="process_search")
def process_search_task(search_id: str) -> Dict[str, Any]:
    """Process search: fetch resumes from HH and perform preliminary scoring"""
    import asyncio
    
    async def _process():
        try:
            # Get search
            search = await Search.get(search_id)
            if not search:
                logger.error("Search not found", search_id=search_id)
                return {"status": "error", "message": "Search not found"}
            
            # Update status
            search.status = "processing"
            await search.save()
            
            logger.info("Processing search", search_id=search_id, query=search.query, city=search.city)
            
            # Extract concepts
            concepts_list = await ai_service.extract_concepts(search.query)
            
            # Save concepts
            concept = Concept(
                search_id=str(search.id),
                concepts=concepts_list
            )
            await concept.create()
            
            # Search resumes from HH
            all_resumes = []
            max_pages = (settings.max_resumes_from_search + 19) // 20  # Round up
            
            for page in range(max_pages):
                hh_response = await hh_client.search_resumes(
                    query=search.query,
                    city=search.city,
                    per_page=20,
                    page=page
                )
                
                items = hh_response.get("items", [])
                if not items:
                    break
                
                all_resumes.extend(items)
                
                if len(all_resumes) >= settings.max_resumes_from_search:
                    break
            
            # Limit to max_resumes_from_search
            all_resumes = all_resumes[:settings.max_resumes_from_search]
            
            # Process each resume
            for resume_data in all_resumes:
                await search_service.process_resume_from_hh(search, resume_data, concepts_list)
            
            # Update search status
            search.total_found = len(all_resumes)
            search.status = "completed"
            await search.save()
            
            logger.info(
                "Search processing completed",
                search_id=search_id,
                resumes_found=len(all_resumes)
            )
            
            # Trigger AI analysis for top resumes
            analyze_top_resumes_task.delay(search_id)
            
            return {
                "status": "completed",
                "resumes_found": len(all_resumes),
                "search_id": search_id
            }
            
        except Exception as e:
            logger.error("Search processing error", search_id=search_id, error=str(e), exc_info=True)
            
            # Update search status
            search = await Search.get(search_id)
            if search:
                search.status = "failed"
                search.error_message = str(e)
                await search.save()
            
            return {"status": "error", "message": str(e)}
    
    return asyncio.run(_process())


@celery_app.task(name="analyze_top_resumes")
def analyze_top_resumes_task(search_id: str) -> Dict[str, Any]:
    """Analyze top resumes with AI"""
    import asyncio
    
    async def _analyze():
        try:
            # Get search
            search = await Search.get(search_id)
            if not search:
                logger.error("Search not found", search_id=search_id)
                return {"status": "error", "message": "Search not found"}
            
            # Get concepts
            concept = await Concept.find_one({"search_id": str(search.id)})
            if not concept:
                logger.error("Concepts not found", search_id=search_id)
                return {"status": "error", "message": "Concepts not found"}
            
            # Get top resumes by preliminary score
            top_resumes = await Resume.find(
                {"search_id": str(search.id)}
            ).sort(-Resume.preliminary_score).limit(settings.max_resumes_for_deep_analysis).to_list()
            
            logger.info(
                "Analyzing top resumes",
                search_id=search_id,
                count=len(top_resumes)
            )
            
            # Analyze each resume
            analyzed_count = 0
            for resume in top_resumes:
                try:
                    await search_service.analyze_resume_with_ai(resume, concept.concepts)
                    analyzed_count += 1
                except Exception as e:
                    logger.error(
                        "Failed to analyze resume",
                        resume_id=str(resume.id),
                        error=str(e)
                    )
            
            # Update search
            search.analyzed_count = analyzed_count
            await search.save()
            
            logger.info(
                "AI analysis completed",
                search_id=search_id,
                analyzed_count=analyzed_count
            )
            
            return {
                "status": "completed",
                "analyzed_count": analyzed_count,
                "search_id": search_id
            }
            
        except Exception as e:
            logger.error("AI analysis error", search_id=search_id, error=str(e), exc_info=True)
            return {"status": "error", "message": str(e)}
    
    return asyncio.run(_analyze())
