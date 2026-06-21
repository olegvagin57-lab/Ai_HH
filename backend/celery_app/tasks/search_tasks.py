"""Celery tasks for search processing"""
import re
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


def _smart_preliminary_score(resume_data: dict, query: str, concepts: list) -> float:
    """
    Title-first preliminary scoring. Range 2.0–10.0.

    HH search cards only expose: title, age, salary, and a total-experience
    duration string like "17 лет 6 месяцев". There is no job history, no skills
    list, and no description in card data. So the title match is by far the
    most reliable signal — it gets the dominant weight. Experience years and
    profile completeness add secondary bonuses.
    """
    title = (resume_data.get("title") or "").lower().strip()

    # Parse total experience from summary string, e.g. "17 лет 6 месяцев"
    exp_desc = ""
    for exp in (resume_data.get("experience") or []):
        if isinstance(exp, dict):
            exp_desc += " " + (exp.get("description") or "")
    exp_desc = exp_desc.strip()

    years_m = re.search(r"(\d+)\s*(?:лет|год(?:а)?)", exp_desc)
    months_m = re.search(r"(\d+)\s*месяц", exp_desc)
    exp_years = int(years_m.group(1)) if years_m else 0
    exp_months = int(months_m.group(1)) if months_m else 0
    total_months = exp_years * 12 + exp_months

    # Build keyword set from query + concepts (no stop-words, len > 2)
    stop = {"и", "или", "в", "на", "с", "для", "от", "до", "по", "из", "к", "о", "а", "но", "не", "что"}
    query_words = [w for w in re.sub(r"[^\w\s]", " ", query.lower()).split()
                   if len(w) > 2 and w not in stop]
    concept_words = []
    for group in concepts:
        for term in group:
            concept_words.extend(w for w in term.lower().split() if len(w) > 2)
    all_keywords = list(set(query_words + concept_words))

    if not all_keywords:
        return 2.0

    # No title → can't determine profession → low score regardless of experience
    if not title:
        return 2.0

    # ── Title matching (primary signal) ────────────────────────────────
    title_hits = sum(1 for kw in all_keywords if kw in title)
    title_ratio = title_hits / len(all_keywords)

    if title_ratio >= 0.35:
        # Strong match: likely the right profession
        score = 7.5 + min(title_ratio, 1.0) * 2.0    # 7.5–9.5
    elif title_ratio >= 0.10:
        # Partial match: adjacent profession
        score = 5.0 + title_ratio * 12.5              # 5.0–8.75
    else:
        # Wrong/unrelated title — cap at 3.5 so they don't reach AI queue
        score = 2.0 + title_ratio * 15.0              # 2.0–3.5

    # ── Experience years bonus — only for title matches ─────────────────
    if title_ratio >= 0.10:
        if total_months >= 120:
            score = min(10.0, score + 0.8)
        elif total_months >= 60:
            score = min(10.0, score + 0.5)
        elif total_months >= 24:
            score = min(10.0, score + 0.2)

    # ── Profile completeness bonuses ───────────────────────────────────
    if resume_data.get("salary", {}).get("amount"):
        score = min(10.0, score + 0.15)

    age = resume_data.get("age")
    if age and 25 <= age <= 52:
        score = min(10.0, score + 0.15)

    return round(score, 2)


@celery_app.task(name="process_search", time_limit=3600, soft_time_limit=3300)
def process_search_task(search_id: str) -> Dict[str, Any]:
    """Fetch resumes from HH, run preliminary scoring, queue per-resume AI tasks."""
    import asyncio

    async def _process():
        search = None
        try:
            from app.infrastructure.database.mongodb import mongodb, connect_to_mongo
            try:
                if mongodb.client:
                    mongodb.client.close()
            except Exception:
                pass
            mongodb.client = None
            mongodb.database = None
            await connect_to_mongo()

            search = await Search.get(search_id)
            if not search:
                return {"status": "error", "message": "Search not found"}

            search.status = "processing"
            await search.save()

            logger.info("Processing search", search_id=search_id, query=search.query[:60])

            # Extract concepts via AI
            concepts_list = await ai_service.extract_concepts(search.query)
            logger.info("Concepts extracted", search_id=search_id, count=len(concepts_list))

            # Build profession profile — one LLM call per search, cached in Concept.
            # This gives the evaluation model a precise understanding of the profession
            # (synonymous titles, adjacent roles, competencies) so it doesn't have to
            # guess whether "инженер по пожарной безопасности" == "инженер пожарной охраны".
            profession_profile = None
            try:
                vacancy_title = ""
                vacancy_desc = ""
                vacancy_reqs = ""
                if search.vacancy_id:
                    from app.domain.entities.vacancy import Vacancy
                    vac = await Vacancy.get(search.vacancy_id)
                    if vac:
                        vacancy_title = vac.title or ""
                        vacancy_desc  = vac.description or ""
                        vacancy_reqs  = vac.requirements or ""
                if not vacancy_title:
                    vacancy_title = search.query
                profession_profile = await ai_service.extract_profession_profile(
                    vacancy_title, vacancy_desc, vacancy_reqs
                )
                logger.info("Profession profile built", search_id=search_id, title=vacancy_title)
            except Exception as e:
                logger.warning("Profession profile extraction failed (non-fatal)", error=str(e))

            concept = Concept(
                search_id=str(search.id),
                concepts=concepts_list,
                profession_profile=profession_profile,
            )
            await concept.create()

            # HH search-cards page always returns 20 resumes regardless of per_page.
            # Fetch up to max_resumes_from_search across multiple pages (10 pages × 20 = 200).
            all_resumes = []
            PAGE_SIZE = 20
            max_pages = (settings.max_resumes_from_search + PAGE_SIZE - 1) // PAGE_SIZE
            for page in range(max_pages):
                hh_response = await hh_client.search_resumes(
                    query=search.query,
                    city=search.city,
                    per_page=PAGE_SIZE,
                    page=page
                )
                items = hh_response.get("items", [])
                if not items:
                    break
                all_resumes.extend(items)
                if len(all_resumes) >= settings.max_resumes_from_search:
                    break

            all_resumes = all_resumes[:settings.max_resumes_from_search]

            search.total_to_process = len(all_resumes)
            search.processed_count = 0
            await search.save()

            # Save each resume with smart preliminary score
            saved_resumes = []
            for idx, resume_data in enumerate(all_resumes, 1):
                # Compute smart preliminary score before saving
                preliminary = _smart_preliminary_score(resume_data, search.query, concepts_list)
                # Temporarily inject so process_resume_from_hh doesn't overwrite it
                resume_data["_preliminary_score_override"] = preliminary

                try:
                    resume = await search_service.process_resume_from_hh(search, resume_data, concepts_list)
                    if resume and preliminary != resume.preliminary_score:
                        resume.preliminary_score = preliminary
                        await resume.save()
                    saved_resumes.append(resume)
                except Exception as e:
                    logger.warning("Failed to process resume", error=str(e))

                search.processed_count = idx
                await search.save()

            # Mark search completed (scraping phase done)
            search.total_found = len(saved_resumes)
            search.status = "completed"
            search.completed_at = datetime.utcnow()
            await search.save()

            logger.info("Search processing completed", search_id=search_id, resumes_found=len(saved_resumes))

            # Queue per-resume AI analysis tasks for top N by preliminary score
            top_resumes = await Resume.find(
                {"search_id": str(search.id), "analyzed": {"$ne": True}}
            ).sort(-Resume.preliminary_score).limit(settings.max_resumes_for_deep_analysis).to_list()

            logger.info("Queuing AI analysis", search_id=search_id, count=len(top_resumes))

            for resume in top_resumes:
                analyze_single_resume_task.delay(str(resume.id), search_id)

            # If search is linked to a vacancy, auto-add top candidates to it
            if search.vacancy_id:
                try:
                    from app.domain.entities.vacancy import Vacancy
                    vacancy = await Vacancy.get(search.vacancy_id)
                    if vacancy:
                        for resume in top_resumes:
                            vacancy.add_candidate(str(resume.id))
                        await vacancy.save()
                        logger.info("Auto-linked candidates to vacancy",
                                    vacancy_id=search.vacancy_id, count=len(top_resumes))
                except Exception as e:
                    logger.warning("Failed to auto-link candidates to vacancy", error=str(e))

            return {
                "status": "completed",
                "resumes_found": len(saved_resumes),
                "queued_for_analysis": len(top_resumes),
                "search_id": search_id
            }

        except Exception as e:
            logger.error("Search processing error", search_id=search_id, error=str(e), exc_info=True)
            try:
                if search is None:
                    search = await Search.get(search_id)
                if search:
                    search.status = "failed"
                    search.error_message = str(e)
                    await search.save()
            except Exception:
                pass
            return {"status": "error", "message": str(e)}

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(_process())
    finally:
        loop.close()


@celery_app.task(name="analyze_single_resume", time_limit=150, soft_time_limit=120)
def analyze_single_resume_task(resume_id: str, search_id: str) -> Dict[str, Any]:
    """Analyze a single resume with Ollama. One Celery task per resume — no timeout cascade."""
    import asyncio

    async def _analyze():
        try:
            from app.infrastructure.database.mongodb import mongodb, connect_to_mongo
            try:
                if mongodb.client:
                    mongodb.client.close()
            except Exception:
                pass
            mongodb.client = None
            mongodb.database = None
            await connect_to_mongo()

            resume = await Resume.get(resume_id)
            if not resume:
                return {"status": "error", "message": "Resume not found"}

            # Already analyzed — skip
            if resume.analyzed:
                return {"status": "skipped", "resume_id": resume_id}

            concept = await Concept.find_one({"search_id": search_id})
            search = await Search.get(search_id)
            query = search.query if search else ""

            # If concept record is missing, extract concepts on the fly
            if not concept and query:
                logger.info("Concepts not found, extracting on-the-fly", search_id=search_id)
                try:
                    concepts_list = await ai_service.extract_concepts(query)
                    concept = Concept(search_id=search_id, concepts=concepts_list)
                    await concept.create()
                except Exception as e:
                    logger.warning("Failed to extract concepts on-the-fly", error=str(e))
                    from app.domain.entities.search import Concept as ConceptModel
                    concept = ConceptModel(search_id=search_id, concepts=[])

            if not concept:
                return {"status": "error", "message": "Concepts not found and search has no query"}

            from app.application.services.evaluation_service import evaluation_service
            criteria = await evaluation_service.get_default_criteria()

            # Load vacancy context if this search was triggered by a vacancy
            vacancy_context = None
            if search and search.vacancy_id:
                try:
                    from app.domain.entities.vacancy import Vacancy
                    vacancy = await Vacancy.get(search.vacancy_id)
                    if vacancy:
                        vacancy_context = {
                            "title": vacancy.title,
                            "description": vacancy.description,
                            "requirements": vacancy.requirements,
                            "salary_max": vacancy.salary_max,
                            "salary_min": vacancy.salary_min,
                            "currency": vacancy.currency,
                        }
                except Exception as e:
                    logger.warning("Failed to load vacancy context", error=str(e))

            await search_service.analyze_resume_with_ai(
                resume, concept.concepts, criteria,
                vacancy_context=vacancy_context,
                profession_profile=concept.profession_profile,
            )

            # Auto-create Candidate record if not exists
            try:
                from app.domain.entities.candidate import Candidate
                existing = await Candidate.find_one({"resume_id": resume_id})
                if not existing:
                    await Candidate(resume_id=resume_id, status="new").create()
                    logger.info("Auto-created candidate", resume_id=resume_id)
            except Exception as e:
                logger.warning("Failed to auto-create candidate", error=str(e))

            # Update search analyzed count
            try:
                if search:
                    analyzed = await Resume.find(
                        {"search_id": search_id, "analyzed": True}
                    ).count()
                    search.analyzed_count = analyzed
                    await search.save()
            except Exception:
                pass

            logger.info("Resume analyzed successfully", resume_id=resume_id, search_id=search_id)
            return {"status": "completed", "resume_id": resume_id}

        except Exception as e:
            logger.error("Resume analysis failed", resume_id=resume_id, error=str(e), exc_info=True)
            return {"status": "error", "resume_id": resume_id, "message": str(e)}

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(_analyze())
    finally:
        loop.close()


@celery_app.task(name="analyze_top_resumes", time_limit=3600, soft_time_limit=3300)
def analyze_top_resumes_task(search_id: str) -> Dict[str, Any]:
    """
    Legacy task kept for backwards-compat.
    Now delegates to per-resume tasks.
    """
    import asyncio

    async def _delegate():
        try:
            from app.infrastructure.database.mongodb import mongodb, connect_to_mongo
            try:
                if mongodb.client:
                    mongodb.client.close()
            except Exception:
                pass
            mongodb.client = None
            mongodb.database = None
            await connect_to_mongo()

            top_resumes = await Resume.find(
                {"search_id": search_id, "analyzed": {"$ne": True}}
            ).sort(-Resume.preliminary_score).limit(settings.max_resumes_for_deep_analysis).to_list()

            logger.info("Delegating to per-resume tasks", search_id=search_id, count=len(top_resumes))
            for resume in top_resumes:
                analyze_single_resume_task.delay(str(resume.id), search_id)

            return {"status": "queued", "count": len(top_resumes)}
        except Exception as e:
            logger.error("Delegation error", error=str(e))
            return {"status": "error", "message": str(e)}

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(_delegate())
    finally:
        loop.close()
