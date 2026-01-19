"""Проверка статуса AI анализа кандидатов"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.infrastructure.database.mongodb import connect_to_mongo
from app.domain.entities.search import Search, Resume

async def check():
    await connect_to_mongo()
    
    print("=" * 80)
    print("ПРОВЕРКА СТАТУСА AI АНАЛИЗА КАНДИДАТОВ")
    print("=" * 80)
    print()
    
    # Получить все поиски
    searches = await Search.find_all().sort(-Search.created_at).limit(10).to_list()
    
    print(f"Найдено поисков: {len(searches)}")
    print()
    
    for search in searches:
        print(f"Поиск: {search.id}")
        print(f"  Запрос: {search.query[:50]}")
        print(f"  Статус: {search.status}")
        print(f"  Найдено всего: {search.total_found}")
        print(f"  Обработано: {search.processed_count}/{search.total_to_process}")
        print(f"  Проанализировано: {search.analyzed_count}")
        if search.error_message:
            print(f"  Ошибка: {search.error_message}")
        
        # Проверить резюме
        resumes = await Resume.find(Resume.search_id == str(search.id)).to_list()
        analyzed = [r for r in resumes if r.analyzed]
        not_analyzed = [r for r in resumes if not r.analyzed]
        
        print(f"  Резюме в базе: {len(resumes)}")
        print(f"    Проанализировано: {len(analyzed)}")
        print(f"    Не проанализировано: {len(not_analyzed)}")
        
        if not_analyzed:
            print(f"    Примеры не проанализированных:")
            for r in not_analyzed[:3]:
                print(f"      - {r.name or 'N/A'} (ID: {r.hh_id or 'N/A'})")
        
        print()
    
    print("=" * 80)
    print("РЕКОМЕНДАЦИИ:")
    print("=" * 80)
    print()
    print("Если резюме не проанализированы:")
    print("1. Проверьте логи Celery: docker logs hh_analyzer_celery | grep analyze")
    print("2. Запустите анализ вручную: python scripts/analyze_pending_resumes.py")
    print("3. Убедитесь, что задача analyze_top_resumes работает")

if __name__ == "__main__":
    asyncio.run(check())
