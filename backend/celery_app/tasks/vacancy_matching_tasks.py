"""Celery tasks for automatic vacancy matching"""
from celery_app.celery import celery_app
from app.application.services.vacancy_matching_service import vacancy_matching_service
from app.core.logging import get_logger
from typing import Dict, Any


logger = get_logger(__name__)


@celery_app.task(name="auto_match_vacancies")
def auto_match_vacancies_task() -> Dict[str, Any]:
    """Run auto-matching for all eligible vacancies"""
    import asyncio
    
    async def _match():
        try:
            # Ensure MongoDB is initialized
            from app.infrastructure.database.mongodb import mongodb, connect_to_mongo
            if mongodb.client is None or mongodb.database is None:
                await connect_to_mongo()
            
            # Get vacancies that need matching
            vacancies = await vacancy_matching_service.get_vacancies_for_auto_matching()
            
            logger.info("Starting auto-matching for vacancies", count=len(vacancies))
            
            results = []
            for vacancy in vacancies:
                try:
                    result = await vacancy_matching_service.run_auto_match_for_vacancy(str(vacancy.id))
                    results.append({
                        "vacancy_id": str(vacancy.id),
                        "status": result.get("status"),
                        "new_candidates": result.get("new_candidates", 0)
                    })
                except Exception as e:
                    logger.error(
                        "Failed to run auto-matching for vacancy",
                        vacancy_id=str(vacancy.id),
                        error=str(e),
                        exc_info=True
                    )
                    results.append({
                        "vacancy_id": str(vacancy.id),
                        "status": "error",
                        "error": str(e)
                    })
            
            logger.info("Auto-matching completed", processed=len(results))
            
            return {
                "status": "completed",
                "processed": len(results),
                "results": results
            }
            
        except Exception as e:
            logger.error("Auto-matching task failed", error=str(e), exc_info=True)
            return {"status": "error", "message": str(e)}
    
    # Handle both sync (Celery) and async (test) contexts
    try:
        # Check if there's a running event loop
        loop = asyncio.get_running_loop()
        # If loop is running, we need to run in a new thread with new event loop
        import concurrent.futures
        def run_in_thread():
            new_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(new_loop)
            try:
                return new_loop.run_until_complete(_match())
            finally:
                new_loop.close()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(run_in_thread)
            return future.result()
    except RuntimeError:
        # No running loop, safe to use asyncio.run()
        return asyncio.run(_match())


@celery_app.task(name="auto_match_single_vacancy")
def auto_match_single_vacancy_task(vacancy_id: str) -> Dict[str, Any]:
    """Run auto-matching for a single vacancy"""
    import asyncio
    
    async def _match():
        try:
            # Ensure MongoDB is initialized
            from app.infrastructure.database.mongodb import mongodb, connect_to_mongo
            if mongodb.client is None or mongodb.database is None:
                await connect_to_mongo()
            
            result = await vacancy_matching_service.run_auto_match_for_vacancy(vacancy_id)
            return result
            
        except Exception as e:
            logger.error(
                "Auto-matching task failed for vacancy",
                vacancy_id=vacancy_id,
                error=str(e),
                exc_info=True
            )
            return {"status": "error", "message": str(e)}
    
    # Handle both sync (Celery) and async (test) contexts
    try:
        # Check if there's a running event loop
        loop = asyncio.get_running_loop()
        # If loop is running, we need to run in a new thread with new event loop
        import concurrent.futures
        def run_in_thread():
            new_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(new_loop)
            try:
                return new_loop.run_until_complete(_match())
            finally:
                new_loop.close()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(run_in_thread)
            return future.result()
    except RuntimeError:
        # No running loop, safe to use asyncio.run()
        return asyncio.run(_match())
