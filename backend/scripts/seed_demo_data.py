"""
Seed demo data: create Candidate records for all AI-analyzed resumes,
assign diverse statuses, tags, notes, ratings to make the app look active.
"""
import asyncio
import random
from datetime import datetime, timedelta

async def seed():
    from app.infrastructure.database.mongodb import connect_to_mongo
    await connect_to_mongo()

    from app.domain.entities.search import Resume
    from app.domain.entities.candidate import Candidate, Interaction

    STATUSES = [
        ("new", 0.20),
        ("reviewed", 0.20),
        ("shortlisted", 0.18),
        ("interview_scheduled", 0.12),
        ("interviewed", 0.10),
        ("offer_sent", 0.05),
        ("hired", 0.04),
        ("rejected", 0.08),
        ("on_hold", 0.03),
    ]

    TAGS_POOL = [
        "приоритет", "опыт 5+", "опыт 10+", "без опыта",
        "рассматривает релокацию", "удалённо", "готов к командировкам",
        "нефтянка", "трубопровод", "автоматизация", "сварка",
        "сильный кандидат", "слабый кандидат", "перезвонить",
        "ждёт оффер", "в процессе", "стажёр",
    ]

    NOTES_POOL = [
        "Кандидат произвёл хорошее впечатление на первичном звонке. Опыт соответствует требованиям.",
        "Провели техническое собеседование. Знает специфику нефтепровода, работал на НПС.",
        "Долго не выходил на связь, перезвонил сам. Мотивация высокая.",
        "Имеет опыт работы в Транснефти, знает регламенты. Требует проверку допусков.",
        "Рассматривает несколько офферов. Нужно ускорить решение.",
        "Опыт меньше, чем указано в вакансии, но потенциал есть.",
        "Согласовали условия, ждём подписания документов.",
        "Кандидат снял свою кандидатуру — принял другой оффер.",
        "Хороший опыт в смежной области. Рассмотреть на другую позицию.",
        "Провели второе собеседование с руководством. Все довольны.",
        "",
        "",
        "",
    ]

    # Get all AI-analyzed resumes
    analyzed = await Resume.find({"analyzed": True}).to_list()
    not_analyzed = await Resume.find({"analyzed": {"$ne": True}, "title": {"$ne": ""}}).limit(100).to_list()
    all_resumes = analyzed + not_analyzed

    print(f"Found {len(analyzed)} analyzed + {len(not_analyzed)} unanalyzed = {len(all_resumes)} total")

    user_ids = ["6a28813f093d1364d91cf1e9"]  # admin user id (will be set in interactions)

    # Delete existing candidates to reseed cleanly
    existing_count = await Candidate.count()
    print(f"Existing candidates: {existing_count}")

    statuses = [s for s, _ in STATUSES]
    weights = [w for _, w in STATUSES]

    created = 0
    updated = 0

    for i, resume in enumerate(all_resumes):
        resume_id = str(resume.id)
        status = random.choices(statuses, weights=weights, k=1)[0]

        candidate = await Candidate.find_one({"resume_id": resume_id})
        if not candidate:
            candidate = Candidate(resume_id=resume_id, status=status)
            # Backdate creation to look like historical data
            days_ago = random.randint(1, 60)
            candidate.created_at = datetime.utcnow() - timedelta(days=days_ago)
            candidate.updated_at = candidate.created_at + timedelta(days=random.randint(0, days_ago))
            candidate.status_changed_at = candidate.updated_at

            # Add tags (50% chance, 1-3 tags)
            if random.random() > 0.5:
                n_tags = random.randint(1, 3)
                candidate.tags = random.sample(TAGS_POOL, n_tags)

            # Add notes (40% chance)
            if random.random() > 0.6:
                note = random.choice([n for n in NOTES_POOL if n])
                candidate.notes = note

            # Add rating for shortlisted/interviewed/offer (60% chance)
            if status in ("shortlisted", "interview_scheduled", "interviewed", "offer_sent", "hired"):
                if random.random() > 0.4:
                    uid = user_ids[0]
                    rating = random.randint(2, 5)
                    candidate.ratings = {uid: rating}
                    candidate.average_rating = float(rating)

            await candidate.create()
            created += 1
        else:
            # Update existing with random enrichments
            if not candidate.tags and random.random() > 0.5:
                candidate.tags = random.sample(TAGS_POOL, random.randint(1, 2))
            if not candidate.notes and random.random() > 0.6:
                note = random.choice([n for n in NOTES_POOL if n])
                candidate.notes = note
            await candidate.save()
            updated += 1

        if (i + 1) % 50 == 0:
            print(f"  Processed {i+1}/{len(all_resumes)}...")

    print(f"\nDone! Created: {created}, Updated: {updated}")
    print(f"Total candidates: {await Candidate.count()}")

    # Print status breakdown
    for s in statuses:
        count = await Candidate.find({"status": s}).count()
        print(f"  {s}: {count}")


if __name__ == "__main__":
    asyncio.run(seed())
