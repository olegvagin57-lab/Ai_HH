"""Link existing resumes to matching vacancies for Транснефть demo"""
import asyncio
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from app.domain.entities.vacancy import Vacancy
from app.domain.entities.search import Search, Resume

MONGO_URL = "mongodb://mongodb:27017"
DB_NAME = "hh_analyzer"

# Map search query keywords → vacancy title keywords
SEARCH_TO_VACANCY = [
    ("оператор нпс", "Оператор нефтеперекачивающей станции"),
    ("оператор нефтеперекач", "Оператор нефтеперекачивающей станции"),
    ("слесарь ремонт насос", "Слесарь"),
    ("электромонтёр высоковольт", "Электромонтёр"),
    ("сварщик накс", "Сварщик"),
    ("инженер асутп", "Инженер АСУТП"),
    ("инженер трубопровод", "Инженер по эксплуатации"),
    ("диспетчер нефтепровод", "Диспетчер"),
    ("инженер охрана труда", "Инженер по охране труда"),
    ("начальник нефтеперекач", "Начальник нефтеперекачивающей"),
    ("главный инженер", "Главный инженер"),
]

# Oil extraction vacancies to delete (wrong for Транснефть pipeline transport)
EXTRACTION_KEYWORDS = ["буровой", "добыч", "геолог", "нгду", "месторождени", "скважин"]


async def main():
    client = AsyncIOMotorClient(MONGO_URL)
    await init_beanie(database=client[DB_NAME], document_models=[Search, Resume, Vacancy])

    all_vacancies = await Vacancy.find_all().to_list()
    all_searches = await Search.find_all().to_list()

    # 1. Delete oil extraction vacancies
    deleted = 0
    pipeline_vacancies = []
    for v in all_vacancies:
        q = (v.search_query or "").lower()
        if any(kw in q for kw in EXTRACTION_KEYWORDS):
            print(f"Deleting extraction vacancy: {v.title}")
            await v.delete()
            deleted += 1
        else:
            pipeline_vacancies.append(v)
    print(f"Deleted {deleted} extraction vacancies, {len(pipeline_vacancies)} pipeline vacancies remain")

    # 2. Activate all pipeline vacancies and enable auto-matching
    for v in pipeline_vacancies:
        v.status = "active"
        v.auto_matching_enabled = True
        v.auto_matching_frequency = "daily"
        v.auto_matching_min_score = 5  # Lower threshold to get more candidates in demo
        v.auto_matching_max_notifications = 20
        await v.save()
        print(f"Activated: {v.title}")

    # 3. Link resumes to matching vacancies
    for search_kw, vacancy_kw in SEARCH_TO_VACANCY:
        # Find matching searches
        matching_searches = [s for s in all_searches if search_kw in s.query.lower()]
        if not matching_searches:
            print(f"No search found for keyword '{search_kw}'")
            continue

        # Find matching vacancy
        matching_vacancies = [v for v in pipeline_vacancies if vacancy_kw.lower() in v.title.lower()]
        if not matching_vacancies:
            print(f"No vacancy found for keyword '{vacancy_kw}'")
            continue

        vacancy = matching_vacancies[0]

        # Get resumes for these searches
        resume_ids_added = []
        for search in matching_searches:
            resumes = await Resume.find({"search_id": str(search.id)}).to_list()
            for resume in resumes:
                if str(resume.id) not in vacancy.candidate_ids:
                    vacancy.candidate_ids.append(str(resume.id))
                    resume_ids_added.append(str(resume.id))

        await vacancy.save()
        print(f"Vacancy '{vacancy.title[:45]}': linked {len(resume_ids_added)} resumes from {len(matching_searches)} searches")

    # 4. For vacancies without candidates, add best-scoring resumes from related searches
    for v in pipeline_vacancies:
        if len(v.candidate_ids) == 0:
            print(f"Vacancy '{v.title}' still has no candidates")

    # Summary
    print("\n=== Final state ===")
    final_vacancies = await Vacancy.find_all().to_list()
    for v in final_vacancies:
        count = len(v.candidate_ids)
        print(f"{v.title[:50]:50} | {v.status:8} | {count:3} кандидатов | auto={v.auto_matching_enabled}")

    client.close()

if __name__ == "__main__":
    asyncio.run(main())
