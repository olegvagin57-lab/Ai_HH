"""Запустить AI анализ для не проанализированных резюме"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.infrastructure.database.mongodb import connect_to_mongo
from app.domain.entities.search import Search, Resume
from celery_app.tasks.search_tasks import analyze_top_resumes_task

async def analyze_pending():
    await connect_to_mongo()
    
    print("=" * 80)
    print("AI АНАЛИЗ НЕ ПРОАНАЛИЗИРОВАННЫХ РЕЗЮМЕ")
    print("=" * 80)
    print()
    
    # Найти поиски со статусом completed
    completed_searches = await Search.find(Search.status == "completed").sort(-Search.created_at).limit(10).to_list()
    
    print(f"Найдено завершенных поисков: {len(completed_searches)}")
    print()
    
    for search in completed_searches:
        # Проверить резюме
        resumes = await Resume.find(Resume.search_id == str(search.id)).to_list()
        analyzed = [r for r in resumes if r.analyzed]
        not_analyzed = [r for r in resumes if not r.analyzed]
        
        print(f"Поиск: {search.id}")
        print(f"  Запрос: {search.query[:50]}")
        print(f"  Всего резюме: {len(resumes)}")
        print(f"  Проанализировано: {len(analyzed)}")
        print(f"  Не проанализировано: {len(not_analyzed)}")
        
        if not_analyzed and len(resumes) > 0:
            print(f"  ✅ Запускаю анализ...")
            try:
                # Запустить задачу анализа
                result = analyze_top_resumes_task.delay(str(search.id))
                print(f"  ✅ Задача отправлена: {result.id}")
            except Exception as e:
                print(f"  ❌ Ошибка: {e}")
        elif len(resumes) == 0:
            print(f"  ⚠️ Нет резюме для анализа")
        else:
            print(f"  ✅ Все резюме уже проанализированы")
        
        print()
    
    print("=" * 80)
    print("ГОТОВО")
    print("=" * 80)
    print()
    print("Проверьте логи Celery через несколько минут:")
    print("  docker logs -f hh_analyzer_celery")

if __name__ == "__main__":
    asyncio.run(analyze_pending())
