"""Celery tasks for search processing"""
from typing import Dict, Any
from datetime import datetime
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
    import nest_asyncio
    
    logger.info("process_search_task called", search_id=search_id)
    
    # Allow nested event loops (needed for Celery)
    nest_asyncio.apply()
    
    async def _process():
        search = None
        try:
            logger.info("Starting search processing", search_id=search_id)
            
            # Ensure MongoDB is initialized
            from app.infrastructure.database.mongodb import mongodb, connect_to_mongo
            if mongodb.client is None or mongodb.database is None:
                logger.debug("MongoDB not initialized, connecting...")
                await connect_to_mongo()
                logger.debug("MongoDB connected")
            
            # Get search with error handling for DB operations
            try:
                search = await Search.get(search_id)
            except Exception as db_error:
                logger.error("Database error getting search", search_id=search_id, error=str(db_error), exc_info=True)
                return {"status": "error", "message": f"Database error: {str(db_error)}"}
            
            if not search:
                logger.error("Search not found", search_id=search_id)
                return {"status": "error", "message": "Search not found"}
            
            # Update status with error handling
            try:
                logger.debug("Updating search status to processing", search_id=search_id)
                search.status = "processing"
                await search.save()
                logger.info("Search status updated to processing", search_id=search_id)
            except Exception as db_error:
                logger.error("Database error updating search status", search_id=search_id, error=str(db_error), exc_info=True)
                return {"status": "error", "message": f"Database error: {str(db_error)}"}
            
            logger.info("Processing search", search_id=search_id, query=search.query[:50], city=search.city)
            
            # Extract concepts
            logger.debug("Extracting concepts", search_id=search_id)
            concepts_list = await ai_service.extract_concepts(search.query)
            logger.info("Concepts extracted", search_id=search_id, count=len(concepts_list))
            
            # Save concepts
            concept = Concept(
                search_id=str(search.id),
                concepts=concepts_list
            )
            await concept.create()
            logger.debug("Concepts saved", search_id=search_id)
            
            # Search resumes from HH
            logger.debug("Starting HH resume search", search_id=search_id, max_resumes=settings.max_resumes_from_search)
            all_resumes = []
            max_pages = (settings.max_resumes_from_search + 19) // 20  # Round up
            logger.debug("Will search up to pages", max_pages=max_pages)
            
            for page in range(max_pages):
                logger.debug("Searching page", page=page + 1, total=max_pages)
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
            
            # Update progress: set total to process
            try:
                search.total_to_process = len(all_resumes)
                search.processed_count = 0
                await search.save()
            except Exception as db_error:
                logger.warning("Failed to update progress", error=str(db_error))
            
            # Process each resume with progress tracking
            for idx, resume_data in enumerate(all_resumes, 1):
                await search_service.process_resume_from_hh(search, resume_data, concepts_list)
                
                # Update progress after each resume
                try:
                    search.processed_count = idx
                    await search.save()
                    logger.debug("Progress updated", 
                               search_id=search_id,
                               processed=idx,
                               total=len(all_resumes))
                except Exception as db_error:
                    logger.warning("Failed to update progress", error=str(db_error))
            
            # Update search status
            try:
                search.total_found = len(all_resumes)
                search.status = "completed"
                search.completed_at = datetime.utcnow()
                await search.save()
            except Exception as db_error:
                logger.error("Database error finalizing search", search_id=search_id, error=str(db_error), exc_info=True)
                # Try to update status to failed
                try:
                    search.status = "failed"
                    search.error_message = f"Database error: {str(db_error)}"
                    await search.save()
                except:
                    pass
                return {"status": "error", "message": f"Database error: {str(db_error)}"}
            
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
            
            # Update search status with error handling
            try:
                if search is None:
                    search = await Search.get(search_id)
                if search:
                    search.status = "failed"
                    search.error_message = str(e)
                    await search.save()
            except Exception as db_error:
                logger.error("Database error updating failed status", search_id=search_id, db_error=str(db_error), exc_info=True)
            
            return {"status": "error", "message": str(e)}
    
    # Handle event loop properly for Celery
    # Use nest_asyncio to allow nested event loops
    import nest_asyncio
    nest_asyncio.apply()
    
    # Create new event loop for this task
    # This ensures the loop is not closed prematurely
    try:
        # Try to get existing loop
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            # If closed, create new one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
    except RuntimeError:
        # No event loop, create one
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    try:
        # Run the async function
        result = loop.run_until_complete(_process())
        return result
    finally:
        # Don't close the loop - let Celery handle it
        # Closing the loop here causes "Event loop is closed" errors
        pass


@celery_app.task(name="analyze_top_resumes")
def analyze_top_resumes_task(search_id: str) -> Dict[str, Any]:
    """Analyze top resumes with AI"""
    import asyncio
    import nest_asyncio
    
    # Allow nested event loops (needed for Celery)
    nest_asyncio.apply()
    
    async def _analyze():
        search = None
        try:
            # Ensure MongoDB is initialized
            from app.infrastructure.database.mongodb import mongodb, connect_to_mongo
            if mongodb.client is None or mongodb.database is None:
                await connect_to_mongo()
            
            # Get search with error handling for DB operations
            try:
                search = await Search.get(search_id)
            except Exception as db_error:
                logger.error("Database error getting search", search_id=search_id, error=str(db_error), exc_info=True)
                return {"status": "error", "message": f"Database error: {str(db_error)}"}
            
            if not search:
                logger.error("Search not found", search_id=search_id)
                return {"status": "error", "message": "Search not found"}
            
            # Get concepts with error handling
            try:
                concept = await Concept.find_one({"search_id": str(search.id)})
            except Exception as db_error:
                logger.error("Database error getting concepts", search_id=search_id, error=str(db_error), exc_info=True)
                return {"status": "error", "message": f"Database error: {str(db_error)}"}
            
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
            
            # Get default criteria (can be extended to use vacancy-specific criteria)
            from app.application.services.evaluation_service import evaluation_service
            criteria = await evaluation_service.get_default_criteria()
            
            # Update progress for AI analysis
            try:
                search.total_to_process = len(top_resumes)
                search.processed_count = 0
                await search.save()
            except Exception as db_error:
                logger.warning("Failed to update AI analysis progress", error=str(db_error))
            
            # Analyze each resume with detailed evaluation and progress tracking
            analyzed_count = 0
            for idx, resume in enumerate(top_resumes, 1):
                try:
                    await search_service.analyze_resume_with_ai(resume, concept.concepts, criteria)
                    analyzed_count += 1
                    
                    # Update progress after each analysis
                    try:
                        search.processed_count = idx
                        search.analyzed_count = analyzed_count
                        await search.save()
                        logger.debug("AI analysis progress updated", 
                                   search_id=search_id,
                                   analyzed=idx,
                                   total=len(top_resumes))
                    except Exception as db_error:
                        logger.warning("Failed to update AI analysis progress", error=str(db_error))
                except Exception as e:
                    logger.error(
                        "Failed to analyze resume",
                        resume_id=str(resume.id),
                        error=str(e)
                    )
            
            # Update search with completed_at
            try:
                search.analyzed_count = analyzed_count
                search.completed_at = datetime.utcnow()
                await search.save()
            except Exception as db_error:
                logger.error("Database error updating search after analysis", search_id=search_id, error=str(db_error), exc_info=True)
                return {"status": "error", "message": f"Database error: {str(db_error)}"}
            
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
            
            # Try to update search status to failed
            try:
                if search is None:
                    search = await Search.get(search_id)
                if search:
                    search.status = "failed"
                    search.error_message = str(e)
                    await search.save()
            except Exception as db_error:
                logger.error("Database error updating failed status", search_id=search_id, db_error=str(db_error), exc_info=True)
            
            return {"status": "error", "message": str(e)}
    
    # Handle event loop properly for Celery
    # Use nest_asyncio to allow nested event loops
    import nest_asyncio
    nest_asyncio.apply()
    
    # Create new event loop for this task
    try:
        # Try to get existing loop
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            # If closed, create new one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
    except RuntimeError:
        # No event loop, create one
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    try:
        # Run the async function
        result = loop.run_until_complete(_analyze())
        return result
    finally:
        # Don't close the loop - let Celery handle it
        pass
