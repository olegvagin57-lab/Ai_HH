"""Check status of the latest search"""
import asyncio
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.infrastructure.database.mongodb import connect_to_mongo
from app.domain.entities.search import Search, Resume

async def check():
    await connect_to_mongo()
    
    # Get last 3 searches
    searches = await Search.find_all().sort('-created_at').limit(3).to_list()
    
    if not searches:
        print("❌ Нет поисков в базе данных")
        return
    
    print("=" * 80)
    print("ПОСЛЕДНИЕ ПОИСКИ")
    print("=" * 80)
    print()
    
    for i, search in enumerate(searches, 1):
        print(f"Поиск #{i}:")
        print(f"  ID: {search.id}")
        print(f"  Статус: {search.status}")
        print(f"  Запрос: {search.query[:80]}...")
        print(f"  Город: {search.city}")
        print(f"  Создан: {search.created_at}")
        print(f"  Найдено резюме: {search.total_found}")
        print(f"  Проанализировано: {search.analyzed_count}")
        
        if search.error_message:
            print(f"  ❌ Ошибка: {search.error_message[:200]}")
        
        if search.completed_at:
            duration = (search.completed_at - search.created_at).total_seconds()
            print(f"  Завершен: {search.completed_at} (за {duration:.1f} секунд)")
        
        # Get resume count for this search
        resume_count = await Resume.find_all(Resume.search_id == str(search.id)).count()
        print(f"  Резюме в базе: {resume_count}")
        
        print()
    
    # Check latest search in detail
    latest = searches[0]
    print("=" * 80)
    print(f"ДЕТАЛЬНАЯ ИНФОРМАЦИЯ О ПОСЛЕДНЕМ ПОИСКЕ")
    print("=" * 80)
    print(f"ID: {latest.id}")
    print(f"Статус: {latest.status}")
    print()
    
    if latest.status == "processing":
        print("⏳ Поиск обрабатывается...")
        print("   Проверьте Celery worker - он должен обрабатывать задачу")
    elif latest.status == "completed":
        print("✅ Поиск завершен успешно!")
        
        # Get analyzed resumes
        analyzed_resumes = await Resume.find_all(
            Resume.search_id == str(latest.id),
            Resume.analyzed == True
        ).to_list()
        
        print(f"   Проанализировано резюме: {len(analyzed_resumes)}")
        
        if analyzed_resumes:
            avg_score = sum(r.ai_score or 0 for r in analyzed_resumes) / len(analyzed_resumes)
            print(f"   Средняя оценка: {avg_score:.1f}/10")
            
            with_hh = sum(1 for r in analyzed_resumes if r.hh_id)
            print(f"   С ссылками на HH: {with_hh}/{len(analyzed_resumes)}")
    elif latest.status == "failed":
        print("❌ Поиск завершился с ошибкой!")
        print(f"   Ошибка: {latest.error_message}")
    elif latest.status == "pending":
        print("⏳ Поиск ожидает обработки...")
        print("   Проверьте, что Celery worker запущен")
    
    print()
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(check())
